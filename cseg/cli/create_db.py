#!/usr/bin/env python3
import sqlite3
import argparse
import os
from tqdm import tqdm

def create_cseg_database(cseg_file, db_file):
    """CSEGファイルからSQLiteデータベースを作成する"""
    # サンプル数を取得
    with open(cseg_file) as f:
        first_line = f.readline().strip()
        n_samples = len(first_line.split('\t')) - 2
        print(f"Number of samples: {n_samples}")
    
    # 既存のデータベースを削除
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # データベースを作成
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # パフォーマンス設定
    c.execute('PRAGMA synchronous = OFF')
    c.execute('PRAGMA journal_mode = MEMORY')
    c.execute('PRAGMA cache_size = -2000000')  # 約2GB のキャッシュ
    c.execute('PRAGMA temp_store = MEMORY')
    c.execute('PRAGMA locking_mode = EXCLUSIVE')
    
    # テーブルを作成（インデックスなし）
    print("Creating table...")
    c.execute('''CREATE TABLE cseg_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ref_name TEXT,
                  start INTEGER,
                  end INTEGER,
                  sample_values BLOB)''')
    
    # 行数を数える
    print("Counting lines...")
    with open(cseg_file) as f:
        n_lines = sum(1 for _ in f)
    
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
    parser = argparse.ArgumentParser(description='Create SQLite database from CSEG file')
    parser.add_argument('cseg_file', help='Input CSEG file')
    parser.add_argument('--db', help='Output database file (default: input_file.db)',
                      default=None)
    
    args = parser.parse_args()
    
    if args.db is None:
        args.db = os.path.splitext(args.cseg_file)[0] + '.db'
    
    print(f"Creating database {args.db} from {args.cseg_file}")
    create_cseg_database(args.cseg_file, args.db)
    print("Done!")

if __name__ == '__main__':
    main()
