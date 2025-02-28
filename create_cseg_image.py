from PIL import Image
import numpy as np
import argparse
import os
import cseg_renderer

def create_image_from_cseg(cseg_file, region_ref, region_start, region_end, canvas_width=1600, canvas_height=None, sample_height=5):
    # C++実装を呼び出し
    image_data = cseg_renderer.create_cseg_image(
        cseg_file,
        region_ref,
        region_start,
        region_end,
        canvas_width,
        sample_height
    )
    
    # NumPy配列からPIL Imageを作成
    img = Image.fromarray(image_data, 'RGB')
    return img

def main():
    parser = argparse.ArgumentParser(description='Create image from CSEG file')
    parser.add_argument('cseg_file', help='Input CSEG file path')
    parser.add_argument('--ref', help='Reference name (if not specified, uses first found in file)')
    parser.add_argument('--start', type=int, help='Start position (default: 1000)', default=1000)
    parser.add_argument('--end', type=int, help='End position (default: 2000)', default=2000)
    parser.add_argument('--width', type=int, help='Canvas width (default: 1600)', default=1600)
    parser.add_argument('--sample-height', type=int, help='Height per sample in pixels (default: 5)', default=5)
    
    args = parser.parse_args()
    
    # refが指定されていない場合は最初の行から取得
    if not args.ref:
        with open(args.cseg_file) as f:
            first_line = f.readline().strip()
            args.ref = first_line.split('\t')[0]
            print(f"Using refName from file: {args.ref}")
    
    print(f"Creating image for region {args.ref}:{args.start}-{args.end}")
    
    img = create_image_from_cseg(
        args.cseg_file,
        args.ref,
        args.start,
        args.end,
        canvas_width=args.width,
        sample_height=args.sample_height
    )
    
    if img:
        # 出力ファイル名を生成
        base_name = os.path.splitext(os.path.basename(args.cseg_file))[0]
        output_file = f"{base_name}_{args.ref}_{args.start}_{args.end}.png"
        img.save(output_file)
        print(f"Image saved as {output_file}")
    else:
        print("No data found for the specified region")

if __name__ == "__main__":
    main()
