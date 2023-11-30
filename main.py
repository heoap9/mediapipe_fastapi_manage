import base64
import json
import os
import time
import cv2

from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from fastapi import Depends, WebSocket, Form, HTTPException
from starlette.responses import RedirectResponse, FileResponse

from common import create_app
from database import get_db, file_transfor_db, SessionLocal, AdminList,FileList
from stream.render_stream import render_detection

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


app, templates = create_app()


@app.get('/stream')
async def root():
    with open(os.path.join('templates', 'stream.html'), 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    default_model = 'mediapipe_demo/models/ssd_mobilenet_v2.tflite'
    base_options = python.BaseOptions(model_asset_path=default_model)
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                           score_threshold=0.5,
                                           category_allowlist=["person"])
    detector = vision.ObjectDetector.create_from_options(options)


    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    await websocket.accept()

    detect_start_time = None
    detect_end_time = None
    recording = False
    out = None
    grace_period = 3  # 유예 시간

    while cap.isOpened():
        ret, frame = cap.read()

        det_val,vis_image = render_detection(frame,detector)

        if det_val.detections:
            if not detect_start_time:
                detect_start_time = time.time()
            detect_end_time = None  # 사람이 감지되면 감지 종료 시간 초기화
        else:
            if detect_end_time is None:
                detect_end_time = time.time()

            # 유예 시간이 지났다면 녹화 종료
            if detect_end_time and time.time() - detect_end_time >= grace_period:
                detect_start_time = None
                recording = False

                # 녹화 종료
                if out:
                    out.release()
                    out = None
                    file_transfor_db(filename)

        # 녹화 시작
        if detect_start_time and time.time() - detect_start_time >= 3 and not recording:
            recording = True

            # 새 녹화 파일 설정
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            filename = f"recordfiles/{time.strftime('%Y_%m_%d__%H_%M_%S')}.mp4"
            out = cv2.VideoWriter(filename, fourcc, 13.0, (1280, 720))

        # 녹화 진행
        if recording and out:
            out.write(vis_image)

        ret, buffer = cv2.imencode('.jpg', vis_image)
        img_str = base64.b64encode(buffer.tobytes()).decode('utf-8')
        msg = json.dumps({'image': img_str, 'detection': str(det_val)})
        await websocket.send_text(msg)

    cap.release()
    if out:
        out.release()
        file_transfor_db(filename)


@app.post("/register")
def register(id: str = Form(...), pwd: str = Form(...), phone: int = Form(...)):
    db: Session = SessionLocal()
    db_user = db.query(AdminList).filter(AdminList.id == id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        new_user = AdminList(id=id, pwd=pwd, phone=phone)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return RedirectResponse(url="/login", status_code=303)


@app.post("/login")
def login(id: str = Form(...), pwd: str = Form(...)):
    db: Session = SessionLocal()
    db_user = db.query(AdminList).filter(AdminList.id == id).first()
    if db_user:
        if db_user.pwd == pwd:
            # return {"message": "Logged in successfull"}
            return RedirectResponse(url="/stream", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Incorrect password")
    else:
        raise HTTPException(status_code=400, detail="User not found")


@app.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/mainpage")
async def main_form(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/get_file_list")
def get_file_list(request: Request, db: Session = Depends(get_db)):
    files = db.query(FileList).all()
    return templates.TemplateResponse("file_list.html", {"request": request, "files": files})


@app.get("/download_file/{filename}")
def download_file(filename: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 절대 경로를 구함
    file_path = os.path.join(base_dir, 'recordfiles', filename)  # 파일의 절대 경로를 구함
    return FileResponse(file_path, filename=filename)
