from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from rembg import remove
from PIL import Image
import os
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# CORS 설정 (HTML과 FastAPI 간의 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Processed-Filename"],  # 클라이언트에서 읽을 수 있는 헤더
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="page.html")

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap(request: Request):
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url>
    <loc>https://bgremove.item-inventory.com/</loc>
    <lastmod>2024-11-01</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
</url>
</urlset>""".strip()

@app.post("/uploadimage/")
async def upload_remove_bg(file: UploadFile):
    # # 1. 파일 이름 설정
    # original_filename = file.filename
    # name_to_ext = os.path.splitext(original_filename)  # 확장자와 파일 이름 분리
    # processed_filename = f"{name_to_ext[0]}_remove.png"


    # 2. 업로드된 파일을 읽음 (file은 실제 바이너리 데이터가 아닌 웹에서 업로드된 파일의 추상화된 메타 데이터이므로 실제 데이터는 .read()가 필요)
    file_data = await file.read()
    
    # 3. PIL로 이미지 로드 (image를 다루기 위해 변환)
    input_image = Image.open(BytesIO(file_data))
    
    # 4. 배경 제거 (rembg 사용)
    processed_image = remove(input_image)

    # 5. 처리된 이미지를 메모리에 저장
    output_buffer = BytesIO()
    processed_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)  # 스트림 포인터를 시작으로 이동

    # # 6. 처리된 이미지를 클라이언트에 스트리밍 응답
    # headers = {"Processed-Filename": processed_filename}  # 파일 이름을 헤더로 전달 ####################
    # return StreamingResponse(output_buffer, media_type="image/png", headers=headers)

    return StreamingResponse(output_buffer, media_type="image/png")
