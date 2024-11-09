from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from rembg import remove
from PIL import Image
import os
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (HTML과 FastAPI 간의 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 임시 디렉토리 설정
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

# 업로드된 파일 저장소
uploaded_files = {}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    업로드된 파일 저장
    """
    file_path = os.path.join(TEMP_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    uploaded_files[file.filename] = file_path
    return {"message": f"{file.filename}\n업로드 성공"}

@app.get("/files/")
async def list_files():
    """
    업로드된 파일 목록 반환
    """
    return {"files": list(uploaded_files.keys())}

@app.post("/remove-bg/")
async def remove_background(filename: str = Form(...)):
    """
    파일의 배경 제거
    """
    if filename not in uploaded_files:
        return JSONResponse({"error": "파일을 찾을 수 없음"}, status_code=404)

    input_file_path = uploaded_files[filename]
    input_image = Image.open(input_file_path)

    # 배경 제거
    output_image = remove(input_image)
    output_image = output_image.convert("RGBA")

    output_filename = f"{os.path.splitext(filename)[0]}_removebg.png"
    output_file_path = os.path.join(TEMP_DIR, output_filename)
    output_image.save(output_file_path, format="PNG")

    return {"message": "이미지 배경 제거 성공", "output_file": output_filename}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    배경 제거된 파일 다운로드
    """
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "파일을 찾을 수 없음"}, status_code=404)
    return FileResponse(file_path, media_type="image/png", filename=filename)

@app.post("/reset/")
async def reset_files():
    """
    업로드된 파일 및 서버 캐시 초기화
    """
    global uploaded_files

    # TEMP_DIR 내의 모든 파일 삭제
    for file in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # 업로드된 파일 목록 초기화
    uploaded_files = {}

    return {"message": "서버 상태 초기화 완료"}
