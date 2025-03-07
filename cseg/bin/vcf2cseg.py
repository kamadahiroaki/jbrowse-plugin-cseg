#!/usr/bin/env python3
import sys
import os
import argparse
import pathlib
from ..config import config

def vcf_to_cseg(vcf_file: pathlib.Path, cseg_file: pathlib.Path = None):
    """VCFファイルをCSEGファイルに変換する"""
    if cseg_file is None:
        # 出力ファイル名を自動生成
        if vcf_file.name == '<stdin>':
            cseg_file = config.cseg_path / 'stdin.cseg'
        else:
            cseg_file = config.cseg_path / f"{vcf_file.stem}.cseg"

    # 入力がパイプからの場合は一時ファイルに保存
    if vcf_file.name == '<stdin>':
        temp_vcf = config.vcf_path / 'temp.vcf'
        temp_vcf.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_vcf, 'wb') as f:
            f.write(sys.stdin.buffer.read())
        vcf_file = temp_vcf

    # 親ディレクトリが存在しない場合は作成
    cseg_file.parent.mkdir(parents=True, exist_ok=True)

    # C++の関数を呼び出してCSEGファイルを生成
    from .vcf2cseg_cpp import convert_vcf_to_cseg
    convert_vcf_to_cseg(str(vcf_file), str(cseg_file))

    # 一時ファイルを削除
    if vcf_file.name == 'temp.vcf':
        vcf_file.unlink()

    # CSEGファイルの内容を標準出力に出力
    with open(cseg_file, 'r') as f:
        sys.stdout.write(f.read())

    return cseg_file

def main():
    parser = argparse.ArgumentParser(description='Convert VCF file to CSEG format')
    parser.add_argument('vcf_file', nargs='?', type=pathlib.Path, default=pathlib.Path('<stdin>'),
                      help='Input VCF file (default: stdin)')
    parser.add_argument('-o', '--output', type=pathlib.Path,
                      help='Output CSEG file (default: <input_name>.cseg in CSEG directory)')
    parser.add_argument('--data-root', help='Root directory for CSEG data (default: /data)')
    args = parser.parse_args()

    if args.data_root:
        os.environ['CSEG_DATA_ROOT'] = args.data_root

    try:
        cseg_file = vcf_to_cseg(args.vcf_file, args.output)
        print(f"Successfully created CSEG file: {cseg_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
