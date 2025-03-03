#!/usr/bin/env python3
import sys
from cseg.bin import vcf2cseg_cpp

def main():
    # 標準入力からVCFデータを行ごとに読み込む
    lines = []
    for line in sys.stdin:
        lines.append(line)
    vcf_content = ''.join(lines)
    
    try:
        # VCFをCSEGに変換
        cseg_output = vcf2cseg_cpp.convert_vcf_to_cseg(vcf_content)
        
        # 結果を標準出力に書き込む
        sys.stdout.write(cseg_output)
        
    except Exception as e:
        print(f"Error converting VCF to CSEG: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
