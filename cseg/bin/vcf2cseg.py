#!/usr/bin/env python3
import sys
import argparse
import pathlib

def vcf_to_cseg(vcf_file: pathlib.Path, cseg_file: pathlib.Path = None):
    """VCFファイルをCSEGファイルに変換する"""
    # 出力ファイル名を自動生成（/data直下に配置）
    if cseg_file is None:
        cseg_file = pathlib.Path('/data') / f"{vcf_file.stem}.cseg"

    # VCFファイルの内容を読み込む
    with open(vcf_file, 'r') as f:
        vcf_content = f.read()

    # C++の関数を呼び出してCSEGデータを生成
    from .vcf2cseg_cpp import convert_vcf_to_cseg
    cseg_data = convert_vcf_to_cseg(vcf_content)

    # CSEGファイルに保存
    with open(cseg_file, 'w') as f:
        f.write(cseg_data)

    # CSEGデータを標準出力に出力
    sys.stdout.write(cseg_data)

    return cseg_file

def main():
    parser = argparse.ArgumentParser(description='Convert VCF file to CSEG format')
    parser.add_argument('vcf_file', type=pathlib.Path,
                      help='Input VCF file')
    parser.add_argument('-o', '--output', type=pathlib.Path,
                      help='Output CSEG file (default: <input_name>.cseg)')
    args = parser.parse_args()

    # 入力ファイルが/data内にない場合は、/data内のパスに変換
    if not str(args.vcf_file).startswith('/data/'):
        vcf_file = pathlib.Path('/data') / args.vcf_file.name
    else:
        vcf_file = args.vcf_file

    # 出力ファイルが指定されている場合は、/data内のパスに変換
    if args.output:
        if not str(args.output).startswith('/data/'):
            cseg_file = pathlib.Path('/data') / args.output.name
        else:
            cseg_file = args.output
    else:
        cseg_file = None

    try:
        cseg_file = vcf_to_cseg(vcf_file, cseg_file)
        print(f"Successfully created CSEG file: {cseg_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
