#!/usr/bin/env python3
import sys
import argparse
import pathlib
import sqlite3

def create_tables(db_path: pathlib.Path):
    """データベースのテーブルを作成する"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # テーブルの作成
    c.execute('''CREATE TABLE IF NOT EXISTS variants (
        id INTEGER PRIMARY KEY,
        chrom TEXT,
        start INTEGER,
        end INTEGER,
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
    c.execute('CREATE INDEX IF NOT EXISTS idx_variants_pos ON variants(chrom, start, end)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_variants_sample ON variants(sample_id)')

    conn.commit()
    conn.close()

def process_cseg_file(cseg_file: pathlib.Path, db_path: pathlib.Path):
    """CSEGファイルを読み込んでデータベースに格納する"""
    print(f"Creating database {db_path} from {cseg_file}")

    # データベースの初期化
    create_tables(db_path)

    # データベースに保存
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # CSEGファイルを1行ずつ読み込んで処理
    with open(cseg_file, 'r') as f:
        # ヘッダー行を処理
        header = f.readline().strip()
        sample_names = header.split('\t')[2:]  # contigとpos以外の列はサンプル名
        
        # サンプルをデータベースに登録
        for i, name in enumerate(sample_names, start=1):
            c.execute('INSERT OR IGNORE INTO samples (id, name) VALUES (?, ?)', (i, name))

        # バリアントデータを登録
        for line in f:  # ヘッダー以外の行を処理
            if not line.strip():  # 空行をスキップ
                continue
                
            fields = line.strip().split('\t')
            chrom = fields[0]
            pos_field = fields[1]
            values = fields[2:]  # サンプルごとの値

            # pos_fieldを解析（整数一つまたは整数-整数の形式）
            if '-' in pos_field:
                start, end = map(int, pos_field.split('-'))
            else:
                start = end = int(pos_field)

            for sample_id, value in enumerate(values, start=1):
                if value.strip():  # 空の値をスキップ
                    c.execute('''
                        INSERT INTO variants (chrom, start, end, sample_id, value)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (chrom, start, end, sample_id, float(value)))

        conn.commit()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Create CSEG database from CSEG file')
    parser.add_argument('cseg_file', type=pathlib.Path,
                      help='Input CSEG file')
    args = parser.parse_args()

    # 入力ファイルが/data内にない場合は、/data内のパスに変換
    if not str(args.cseg_file).startswith('/data/'):
        cseg_file = pathlib.Path('/data') / args.cseg_file.name
    else:
        cseg_file = args.cseg_file

    # データベースファイル名を入力ファイル名から自動生成
    db_path = pathlib.Path('/data') / f"{cseg_file.stem}.db"

    try:
        process_cseg_file(cseg_file, db_path)
        print(f"\nDatabase created successfully at: {db_path}")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    main()
