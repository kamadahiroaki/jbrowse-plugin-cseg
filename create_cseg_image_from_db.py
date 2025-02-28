#!/usr/bin/env python3
import sqlite3
import argparse
import os
from PIL import Image
import numpy as np
import cseg_renderer
import tempfile

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
    
    # NumPy配列からPIL Imageを作成
    img = Image.fromarray(image_data, 'RGB')
    return img

def main():
    parser = argparse.ArgumentParser(description='Create image from CSEG database')
    parser.add_argument('db_file', help='Input database file')
    parser.add_argument('--ref', help='Reference name (if not specified, uses first found in database)')
    parser.add_argument('--start', type=int, help='Start position (default: 1000)', default=1000)
    parser.add_argument('--end', type=int, help='End position (default: 2000)', default=2000)
    parser.add_argument('--width', type=int, help='Canvas width (default: 1600)', default=1600)
    parser.add_argument('--sample-height', type=int, help='Height per sample in pixels (default: 5)', default=5)
    
    args = parser.parse_args()
    
    # refが指定されていない場合は最初のref_nameを使用
    if not args.ref:
        conn = sqlite3.connect(args.db_file)
        c = conn.cursor()
        c.execute('SELECT DISTINCT ref_name FROM cseg_data LIMIT 1')
        args.ref = c.fetchone()[0]
        conn.close()
        print(f"Using refName from database: {args.ref}")
    
    print(f"Creating image for region {args.ref}:{args.start}-{args.end}")
    
    img = create_image_from_db(
        args.db_file,
        args.ref,
        args.start,
        args.end,
        canvas_width=args.width,
        sample_height=args.sample_height
    )
    
    if img:
        # 出力ファイル名を生成
        base_name = os.path.splitext(os.path.basename(args.db_file))[0]
        output_file = f"{base_name}_{args.ref}_{args.start}_{args.end}.png"
        img.save(output_file)
        print(f"Image saved as {output_file}")
    else:
        print("No data found for the specified region")

if __name__ == '__main__':
    main()
