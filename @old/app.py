# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import FileResponse
# from rembg import remove
# from PIL import Image
# import os
# from io import BytesIO

# app = FastAPI()

# # 임시 디렉토리 설정
# TEMP_DIR = "/tmp"

# @app.get("/hello")
# async def hello():
#     return {"message": "Hello, the server is running!"}


# @app.post("/remove-bg/")
# async def remove_background(file: UploadFile = File(...)):
#     # 파일을 메모리로 읽고 배경 제거
#     input_image = Image.open(BytesIO(await file.read()))
#     output_image = remove(input_image)
    
#     # 항상 RGBA 모드로 변환하여 투명 배경 유지
#     output_image = output_image.convert("RGBA")

#     # 파일 경로를 PNG 확장자로 설정하여 항상 투명 배경 유지
#     output_filename = os.path.join(TEMP_DIR, f"{os.path.splitext(file.filename)[0]}_removebg.png")

#     # PNG 형식으로 저장
#     output_image.save(output_filename, format="PNG")

#     return FileResponse(output_filename, media_type="image/png", filename=f"{file.filename}_removebg.png")

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from rembg import remove
from PIL import Image, ImageSequence
import os
from io import BytesIO

app = FastAPI()

# 임시 디렉토리 설정
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/hello")
async def hello():
    return {"message": "Hello, the server is running!"}


@app.post("/remove-bg/")
async def remove_background(file: UploadFile = File(...)):
    # 파일 저장 경로 설정
    input_file_path = os.path.join(TEMP_DIR, file.filename)
    with open(input_file_path, "wb") as buffer:
        buffer.write(await file.read())

    # GIF 처리 여부 확인
    if file.filename.lower().endswith(".gif"):
        input_image = Image.open(input_file_path)
        frames = []

        # GIF의 각 프레임 배경 제거
        for frame in ImageSequence.Iterator(input_image):
            frame = frame.convert("RGBA")  # RGBA 모드로 변환
            frame_bytes = BytesIO()
            frame.save(frame_bytes, format="PNG")  # 프레임을 PNG로 변환
            processed_frame = remove(Image.open(frame_bytes))
            # frames.append(processed_frame)

            #  # 투명 배경을 검은색으로 변경
            # black_background = Image.new("RGBA", processed_frame.size, (0, 0, 0, 255))  # 검은 배경 생성
            # black_background.paste(processed_frame, (0, 0), processed_frame)  # 검은 배경 위에 프레임 붙이기
            # frames.append(black_background)

            # GIF 팔레트(P) 모드로 변환
            palette_frame = processed_frame.convert("P", palette=Image.ADAPTIVE)
            frames.append(palette_frame)


        # 처리된 프레임을 새로운 GIF로 저장
        output_filename = f"{os.path.splitext(file.filename)[0]}_removebg.gif"
        output_file_path = os.path.join(TEMP_DIR, output_filename)
        frames[0].save(
            output_file_path,
            save_all=True,
            append_images=frames[1:],  # 나머지 프레임 추가
            disposal=2,
            loop=0,
            duration=input_image.info.get("duration", 100),  # 원래 GIF의 지속 시간
        )
    else:
        # 정적 이미지 처리
        input_image = Image.open(input_file_path)
        output_image = remove(input_image)
        output_image = output_image.convert("RGBA")

        output_filename = f"{os.path.splitext(file.filename)[0]}_removebg.png"
        output_file_path = os.path.join(TEMP_DIR, output_filename)
        output_image.save(output_file_path, format="PNG")

    return FileResponse(output_file_path, media_type="image/gif" if file.filename.lower().endswith(".gif") else "image/png", filename=output_filename)