#!/usr/bin/env python3
import os
import argparse
from ..config import config

def create_data_directories():
    """必要なデータディレクトリを作成する"""
    dirs = [
        config.vcf_path,
        config.cseg_path,
        config.db_path
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

    print("\nCSEG data directories are ready!")
    print(f"VCF files will be stored in: {config.vcf_path}")
    print(f"CSEG files will be stored in: {config.cseg_path}")
    print(f"Database files will be stored in: {config.db_path}")
    print(f"Default database file: {config.db_file}")

def main():
    parser = argparse.ArgumentParser(description='Initialize CSEG data directories')
    parser.add_argument('--data-root', help='Root directory for CSEG data (default: /data)')
    args = parser.parse_args()

    if args.data_root:
        os.environ['CSEG_DATA_ROOT'] = args.data_root

    create_data_directories()

if __name__ == '__main__':
    main()
