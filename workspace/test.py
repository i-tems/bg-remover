import argparse
from rembg import remove
from PIL import Image
import os

# argparse 설정
parser = argparse.ArgumentParser(description="Remove background from an image file")
parser.add_argument("input_file", help="Path to the input image file")
parser.add_argument("output_file", nargs="?", help="Optional custom name for the output file")

args = parser.parse_args()

# 입력 파일의 확장자를 가져와 기본 출력 파일 이름 설정
input_file_name, input_extension = os.path.splitext(args.input_file)
default_output_file = f"{input_file_name}_removebg{input_extension}"

# 사용자가 제공한 이름이 없다면 기본 파일명 사용
output_file = args.output_file if args.output_file else default_output_file

# 이미지 파일 불러오기
img = Image.open(args.input_file)

# 배경 제거하기
out = remove(img)

# 출력 파일이 PNG인지 확인하여 RGBA 모드를 유지하고 저장
if output_file.lower().endswith(".png"):
    out.save(output_file)  # RGBA로 저장하여 투명 배경 유지
else:
    out = out.convert("RGB")  # JPEG로 저장하려면 RGB로 변환 필요
    out.save(output_file)

print(f"Processed image saved as {output_file}")