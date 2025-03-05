#!/usr/bin/env python3
import os

def create_data_directories():
    """必要なデータディレクトリを作成する"""
    dirs = [
        '/data/vcf',
        '/data/cseg',
        '/data/db'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

def main():
    create_data_directories()

if __name__ == '__main__':
    main()
