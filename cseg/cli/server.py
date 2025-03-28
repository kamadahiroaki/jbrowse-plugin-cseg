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
    
    # 一時ファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cseg', delete=True) as temp_cseg:
        # データを取得（インデックスを使用）
        c.execute('''
            SELECT ref_name, start, end, sample_values 
            FROM cseg_data 
            WHERE ref_name = ? 
            AND NOT (end < ? OR start > ?)
            ORDER BY start
        ''', (region_ref, region_start, region_end))
        
        # 一時CSEGファイルに書き出し
        for ref_name, start, end, values_blob in c:
            values = list(values_blob)
            if start == end:
                pos = str(start)
            else:
                pos = f"{start}-{end}"
            values_str = '\t'.join(str(x) for x in values)
            temp_cseg.write(f"{ref_name}\t{pos}\t{values_str}\n")
        
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
        # JBrowseの0-baseからVCFの1-baseに変換
        query_start = start + 1
        query_end = end + 1

        # 画像を生成
        img = create_image_from_db(
            db_file,
            ref_name,
            query_start,
            query_end,
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
