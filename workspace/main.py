from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from rembg import remove
from PIL import Image
import os
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
# import logging



app = FastAPI()

# logging.basicConfig(
#     level=logging.DEBUG,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#     format="%(asctime)s - %(levelname)s - %(message)s",  # 로그 포맷 설정
#     handlers=[
#         logging.StreamHandler(),  # 콘솔 출력
#     ],
# )
# logger = logging.getLogger(__name__)  # 로거 생성

# 동시 처리 제한 (예: 최대 10개의 요청만 동시에 처리)
semaphore = asyncio.Semaphore(10)

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

class State:
    current_tasks = 0

state = State()

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
    # 동시 처리 제한
    async with semaphore:
        try:
            # state.current_tasks += 1
            # max_tasks = semaphore._value + state.current_tasks  # 최대 작업 수 계산
            # available_slots = max_tasks - state.current_tasks  # 남은 작업 가능 수 계산

            # # 현재 상태 로그 출력
            # logger.debug(f"현재 실행 중인 작업 수: {state.current_tasks}")
            # logger.info(f"남은 작업 가능 수: {available_slots}")

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
        except Exception as e:
            logger.error(f"이미지 처리 중 오류 발생: {e}")
            raise HTTPException(status_code=500, detail="이미지 처리 중 오류 발생")
        # finally:
        #     state.current_tasks -= 1  # 작업 완료
        #     logger.debug(f"작업 완료, 남은 작업 수: {state.current_tasks}")

    return StreamingResponse(output_buffer, media_type="image/png")
