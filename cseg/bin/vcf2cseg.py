#!/usr/bin/env python3
import sys
import argparse
import pathlib

def vcf_to_cseg(vcf_content: str, cseg_file: pathlib.Path = None, input_name: str = 'stdin'):
    """VCFデータをCSEGファイルに変換する"""
    # 出力ファイル名を自動生成（/data直下に配置）
    if cseg_file is None:
        cseg_file = pathlib.Path('/data') / f"{input_name}.cseg"

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
    parser.add_argument('vcf_file', nargs='?', type=pathlib.Path, default=pathlib.Path('<stdin>'),
                      help='Input VCF file (default: stdin)')
    parser.add_argument('-o', '--output', type=pathlib.Path,
                      help='Output CSEG file (default: <input_name>.cseg)')
    args = parser.parse_args()

    # 入力ソースを決定
    if args.vcf_file.name != '<stdin>':
        # ファイルが/data内にない場合は、/data内のパスに変換
        if not str(args.vcf_file).startswith('/data/'):
            vcf_file = pathlib.Path('/data') / args.vcf_file.name
        else:
            vcf_file = args.vcf_file

        # ファイルから読み込み
        try:
            with open(vcf_file, 'r') as f:
                vcf_content = f.read()
            input_name = vcf_file.stem
        except FileNotFoundError:
            print(f"Error: Input file not found: {vcf_file}", file=sys.stderr)
            sys.exit(1)
    else:
        # 標準入力から読み込み
        print("Reading from standard input...", file=sys.stderr)
        vcf_content = sys.stdin.read()
        input_name = 'stdin'

    # 出力ファイルが指定されている場合は、/data内のパスに変換
    if args.output:
        if not str(args.output).startswith('/data/'):
            cseg_file = pathlib.Path('/data') / args.output.name
        else:
            cseg_file = args.output
    else:
        cseg_file = None

    try:
        cseg_file = vcf_to_cseg(vcf_content, cseg_file, input_name)
        print(f"Successfully created CSEG file: {cseg_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
