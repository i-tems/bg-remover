from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from rembg import remove
from PIL import Image
import os
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4

app = FastAPI()

# CORS 설정 (HTML과 FastAPI 간의 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)  # tmp 디렉토리 생성 (존재하지 않으면 생성)

@app.post("/uploadimage/")
async def upload_remove_bg(file: UploadFile):
    # 1. 업로드된 파일을 읽음 (file은 실제 바이너리 데이터가 아닌 웹에서 업로드된 파일의 추상화된 메타 데이터이므로 실제 데이터는 .read()가 필요)
    file_data = await file.read()
    
    # 2. PIL로 이미지 로드 (image를 다루기 위해 변환)
    input_image = Image.open(BytesIO(file_data))
    
    # 3. 배경 제거 (rembg 사용)
    processed_image = remove(input_image)

    # 4. 처리된 이미지를 메모리에 저장
    output_buffer = BytesIO()
    processed_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)  # 스트림 포인터를 시작으로 이동

    return StreamingResponse(output_buffer, media_type="image/png")
