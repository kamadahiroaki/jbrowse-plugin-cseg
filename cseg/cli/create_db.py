#!/usr/bin/env python3
import os
import argparse
import pathlib
import sqlite3
from tqdm import tqdm
from ..config import config

def create_tables(db_path: pathlib.Path):
    """データベースのテーブルを作成する"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # テーブルの作成
    c.execute('''CREATE TABLE IF NOT EXISTS variants (
        id INTEGER PRIMARY KEY,
        chrom TEXT,
        pos INTEGER,
        ref TEXT,
        alt TEXT,
        sample_id INTEGER,
        value REAL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )''')

    # インデックスの作成
    c.execute('CREATE INDEX IF NOT EXISTS idx_variants_pos ON variants(chrom, pos)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_variants_sample ON variants(sample_id)')

    conn.commit()
    conn.close()

def process_cseg_file(cseg_file: pathlib.Path, db_path: pathlib.Path):
    """CSEGファイルを読み込んでデータベースに格納する"""
    print(f"Creating database {db_path} from {cseg_file}")

    # データベースの初期化
    create_tables(db_path)

    # CSEGファイルの処理
    # Note: ここでは簡略化していますが、実際にはCSEGファイルのフォーマットに
    # 合わせて適切な処理を行う必要があります
    from ..bin.vcf2cseg_cpp import process_cseg_file
    process_cseg_file(str(cseg_file), str(db_path))

def main():
    parser = argparse.ArgumentParser(description='Create CSEG database from CSEG file')
    parser.add_argument('cseg_file', type=pathlib.Path,
                      help='Input CSEG file')
    parser.add_argument('--db', type=pathlib.Path,
                      help='Output database file (default: config.db_file)')
    parser.add_argument('--data-root', help='Root directory for CSEG data (default: /data)')
    args = parser.parse_args()

    if args.data_root:
        os.environ['CSEG_DATA_ROOT'] = args.data_root

    db_path = args.db if args.db else config.db_file
    
    # 親ディレクトリが存在しない場合は作成
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        process_cseg_file(args.cseg_file, db_path)
        print(f"\nDatabase created successfully at: {db_path}")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    main()
