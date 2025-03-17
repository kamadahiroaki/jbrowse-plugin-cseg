#!/usr/bin/env python3
import sys
import argparse
import pathlib
import sqlite3
from tqdm import tqdm

def create_tables(db_path: pathlib.Path):
    """データベースのテーブルを作成する"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # パフォーマンス設定
    c.execute('PRAGMA synchronous = OFF')
    c.execute('PRAGMA journal_mode = MEMORY')
    c.execute('PRAGMA cache_size = -2000000')  # 約2GB のキャッシュ
    c.execute('PRAGMA temp_store = MEMORY')
    c.execute('PRAGMA locking_mode = EXCLUSIVE')

    # テーブルを作成（インデックスなし）
    c.execute('''CREATE TABLE cseg_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_name TEXT,
        start INTEGER,
        end INTEGER,
        sample_values BLOB
    )''')

    conn.commit()
    conn.close()

def process_cseg_file(cseg_file: pathlib.Path, db_path: pathlib.Path):
    """CSEGファイルを読み込んでデータベースに格納する"""
    print(f"Creating database {db_path} from {cseg_file}")

    # サンプル数を取得
    with open(cseg_file) as f:
        first_line = f.readline().strip()
        n_samples = len(first_line.split('\t')) - 2
        print(f"Number of samples: {n_samples}")

    # 既存のデータベースを削除
    if db_path.exists():
        db_path.unlink()

    # データベースの初期化
    create_tables(db_path)

    # 行数を数える
    print("Counting lines...")
    with open(cseg_file) as f:
        n_lines = sum(1 for _ in f)

    # データベースに保存
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # データを挿入（単一トランザクション）
    print("Inserting data...")
    c.execute('BEGIN TRANSACTION')

    try:
        # バッファを準備（メモリ効率のため）
        insert_sql = 'INSERT INTO cseg_data (ref_name, start, end, sample_values) VALUES (?, ?, ?, ?)'
        buffer = []
        buffer_size = 10000  # バッファサイズ

        with open(cseg_file) as f:
            with tqdm(total=n_lines, desc="Loading data") as pbar:
                # 最初の行を読み飛ばす（既に読んでいるため）
                next(f)
                pbar.update(1)

                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) < 3:
                        pbar.update(1)
                        continue

                    ref_name = parts[0]
                    pos = parts[1]
                    values = [int(x) for x in parts[2:]]

                    # 位置を解析
                    if '-' in pos:
                        start, end = map(int, pos.split('-'))
                    else:
                        start = end = int(pos)

                    # バイナリデータとして値を保存
                    values_blob = bytes(values)

                    # バッファに追加
                    buffer.append((ref_name, start, end, values_blob))

                    # バッファがいっぱいになったら一括挿入
                    if len(buffer) >= buffer_size:
                        c.executemany(insert_sql, buffer)
                        buffer.clear()

                    pbar.update(1)

                # 残りのバッファを処理
                if buffer:
                    c.executemany(insert_sql, buffer)

        # トランザクションをコミット
        print("Committing transaction...")
        conn.commit()

    except Exception as e:
        # エラーが発生した場合はロールバック
        conn.rollback()
        raise e

    # インデックスを作成
    print("Creating indexes...")
    c.execute('CREATE INDEX idx_ref_pos ON cseg_data(ref_name, start, end)')

    # データベースを最適化
    print("Optimizing database...")
    c.execute('ANALYZE')
    c.execute('VACUUM')

    # 統計情報を表示
    c.execute('SELECT COUNT(*) FROM cseg_data')
    total_rows = c.fetchone()[0]
    print(f"Total records: {total_rows}")

    c.execute('SELECT DISTINCT ref_name FROM cseg_data')
    ref_names = [row[0] for row in c.fetchall()]
    print(f"Reference sequences: {len(ref_names)}")

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
