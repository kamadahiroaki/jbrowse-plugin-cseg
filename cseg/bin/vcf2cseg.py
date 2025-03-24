#!/usr/bin/env python3
import sys
import argparse
import pathlib

def vcf_to_cseg(vcf_file: pathlib.Path, cseg_file: pathlib.Path = None, use_stdin: bool = False):
    """VCFファイルをCSEGファイルに変換する"""
    # VCFファイルの内容を読み込む
    if use_stdin:
        print("Reading from stdin...", file=sys.stderr)
        vcf_content = sys.stdin.read()
    else:
        print(f"Reading file: {vcf_file}", file=sys.stderr)
        if not vcf_file.exists():
            raise FileNotFoundError(f"Input file not found: {vcf_file}")
        with open(vcf_file, 'r') as f:
            vcf_content = f.read()

    # C++の関数を呼び出してCSEGデータを生成
    print("Converting to CSEG format...", file=sys.stderr)
    from .vcf2cseg_cpp import convert_vcf_to_cseg
    cseg_data = convert_vcf_to_cseg(vcf_content)

    # CSEGファイルに保存またはstdoutに出力
    if not use_stdin:
        # 出力ファイル名が指定されていない場合は、入力ファイル名から自動生成
        if cseg_file is None:
            cseg_file = vcf_file.with_suffix('.cseg')
        print(f"Writing to file: {cseg_file}", file=sys.stderr)
        with open(cseg_file, 'w') as f:
            f.write(cseg_data)
    else:
        sys.stdout.write(cseg_data)

    return cseg_file

def main():
    parser = argparse.ArgumentParser(description='Convert VCF file to CSEG format')
    parser.add_argument('vcf_file', type=pathlib.Path, nargs='?',
                      help='Input VCF file')
    parser.add_argument('-o', '--output', type=pathlib.Path,
                      help='Output CSEG file (default: <input_name>.cseg)')
    parser.add_argument('-T', '--use-stdin', action='store_true',
                      help='Read from stdin instead of file')
    args = parser.parse_args()

    # 入力ファイルと-Tオプションのチェック
    if args.use_stdin and args.vcf_file:
        parser.error("Cannot specify both input file and -T option")

    if not args.use_stdin and not args.vcf_file:
        parser.error("Must specify input file or -T option")

    # 入力ファイルが/data内にない場合は、/data内のパスに変換
    vcf_file = None
    if args.vcf_file:
        vcf_file = pathlib.Path(str(args.vcf_file))
        if not vcf_file.is_absolute():
            vcf_file = pathlib.Path('/data') / vcf_file

    # 出力ファイルが指定されている場合は、/data内のパスに変換
    cseg_file = None
    if args.output:
        cseg_file = pathlib.Path(str(args.output))
        if not cseg_file.is_absolute():
            cseg_file = pathlib.Path('/data') / cseg_file

    try:
        vcf_to_cseg(vcf_file, cseg_file, args.use_stdin)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
