#!/usr/bin/env python3
import sys
import argparse
import pathlib
from typing import TextIO, Iterator, Tuple

def read_vcf_by_contig(file: TextIO) -> Iterator[Tuple[str, list[str]]]:
    """VCFファイルをcontigごとに読み込むジェネレータ"""
    current_contig = None
    current_lines = []
    
    for line in file:
        if line.startswith('#'):
            continue
            
        if not line.strip():
            continue
            
        fields = line.split('\t', 1)
        if not fields:
            continue
            
        contig = fields[0]
        
        if current_contig is None:
            current_contig = contig
            
        if contig != current_contig:
            if current_lines:  # 空でない場合のみyield
                yield current_contig, current_lines
            current_lines = []
            current_contig = contig
            
        current_lines.append(line)
    
    if current_lines:  # 最後のcontigのデータ
        yield current_contig, current_lines

def vcf_to_cseg(vcf_file: pathlib.Path, cseg_file: pathlib.Path = None, use_stdin: bool = False):
    """VCFファイルをCSEGファイルに変換する"""
    # 出力ファイル名の設定
    if not use_stdin and cseg_file is None:
        cseg_file = vcf_file.with_suffix('.cseg')

    # C++モジュールのインポート
    from .vcf2cseg_cpp import process_vcf_chunk

    try:
        if use_stdin:
            print("Reading from stdin...", file=sys.stderr)
            input_file = sys.stdin
        else:
            print(f"Reading file: {vcf_file}", file=sys.stderr)
            if not vcf_file.exists():
                raise FileNotFoundError(f"Input file not found: {vcf_file}")
            input_file = open(vcf_file, 'r')

        # 出力ファイルを開く（標準入力モードの場合は標準出力を使用）
        output_file = sys.stdout if use_stdin else open(cseg_file, 'w')

        try:
            # contigごとに処理
            for contig, lines in read_vcf_by_contig(input_file):
                if not lines:  # 空のcontigをスキップ
                    continue
                print(f"\rProcessing contig {contig}...", end='', file=sys.stderr, flush=True)
                chunk = ''.join(lines)
                result = process_vcf_chunk(chunk)
                if result:
                    output_file.write(result)

            print("\nConversion completed", file=sys.stderr)
            return cseg_file

        finally:
            if not use_stdin:
                input_file.close()
            if not use_stdin:
                output_file.close()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise

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
