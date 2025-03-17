#!/usr/bin/env python3
from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image
import io
import sqlite3
from cseg.lib import cseg_renderer
import os
import tempfile

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:9000"}})

# データベースファイルのディレクトリを設定
DB_DIR = os.environ.get('CSEG_DB_DIR', '/data')

def create_image_from_db(db_file, region_ref, region_start, region_end, canvas_width=1600, sample_height=5):
    """データベースからデータを抽出して画像を生成する"""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # サンプル名を取得
    c.execute('SELECT id, name FROM samples ORDER BY id')
    samples = c.fetchall()
    
    # 一時ファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cseg', delete=True) as temp_cseg:
        # ヘッダー行を書き出し
        header = ['chrom', 'pos'] + [name for _, name in samples]
        temp_cseg.write('\t'.join(header) + '\n')
        
        # データを取得（インデックスを使用）
        c.execute('''
            SELECT DISTINCT chrom, start, end
            FROM variants 
            WHERE chrom = ? 
            AND NOT (end < ? OR start > ?)
            ORDER BY start, end
        ''', (region_ref, region_start, region_end))
        positions = c.fetchall()
        
        # 各位置でのサンプルごとの値を取得
        for chrom, start, end in positions:
            # 位置の文字列を生成
            if start == end:
                pos = str(start)
            else:
                pos = f"{start}-{end}"
            
            # この位置での全サンプルの値を取得
            values = []
            for sample_id, _ in samples:
                c.execute('''
                    SELECT value 
                    FROM variants 
                    WHERE chrom = ? AND start = ? AND end = ? AND sample_id = ?
                ''', (chrom, start, end, sample_id))
                result = c.fetchone()
                values.append(str(result[0]) if result else '0')
            
            # CSEGファイルに行を書き出し
            temp_cseg.write(f"{chrom}\t{pos}\t{'\t'.join(values)}\n")
        
        # ファイルをフラッシュして確実にディスクに書き出す
        temp_cseg.flush()
        
        # C++実装を呼び出し
        image_data = cseg_renderer.create_cseg_image(
            temp_cseg.name,
            region_ref,
            region_start,
            region_end,
            canvas_width,
            sample_height
        )
    
    conn.close()
    
    if image_data is None:
        return None
    
    # NumPy配列からPIL Imageを作成
    img = Image.fromarray(image_data, 'RGB')
    return img

@app.route('/')
def serve_image():
    # パラメータを取得
    cseg = request.args.get('cseg', type=str)
    ref_name = request.args.get('ref_name', type=str)
    start = request.args.get('start', type=int)
    end = request.args.get('end', type=int)
    width = request.args.get('width', default=1600, type=int)
    sample_height = request.args.get('sample_height', default=5, type=int)
    
    # パラメータのバリデーション
    if not all([cseg, ref_name, start is not None, end is not None]):
        return 'Missing required parameters', 400
    
    # データベースファイルのパスを構築
    db_file = os.path.join(DB_DIR, f"{cseg}.db")
    
    # データベースファイルの存在確認
    if not os.path.exists(db_file):
        return f'Database file {db_file} not found', 404
    
    try:
        # 画像を生成
        img = create_image_from_db(
            db_file,
            ref_name,
            start,
            end,
            canvas_width=width,
            sample_height=sample_height
        )
        
        if img is None:
            return 'No data found for the specified region', 404
        
        # 画像をバイトストリームに変換
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # 画像を送信
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False
        )
        
    except Exception as e:
        return str(e), 500

def main():
    # 0.0.0.0でリッスンしてコンテナ外からのアクセスを許可
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
