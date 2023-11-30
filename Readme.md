# Person deteciton CCTV
## 사람을 감지하고 사람을 감지하면 녹화와 알림을 제공하는 웹서비스를 제공!
### 기능 요약도


### 관리자페이지 로그인 및 회원가입

![programindex](https://github.com/heoap9/mediapipe_fastapi_manage/assets/83992590/e5489cb8-14df-4916-a2f0-71c9dbf62999)
### 관리자 페이지 진입 후 현재 녹화(감지),녹화된 파일 목록 출력
![recordindex](https://github.com/heoap9/mediapipe_fastapi_manage/assets/83992590/e3e35c98-4b76-4d16-bd1d-7d5a18d69a64)



## 기능명세
![login_and_register](https://github.com/heoap9/mediapipe_fastapi_manage/assets/83992590/f473a58a-4bc7-4d66-9b91-3c0b9ed275bc)

### Fast api로 간단하게 구현되어있는 로그인메뉴!
```python
@app.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
```

### 웹으로 확인할 수 있는 디텍트 결과!
![record (1)](https://github.com/heoap9/mediapipe_fastapi_manage/assets/83992590/02a6f7ae-a5e2-4bd4-9c9c-5c675a406b57)

### 웹소켓으로 처리된 결과를 전송한다
```python
@app.get('/stream')
async def root():
    with open(os.path.join('templates', 'stream.html'), 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
```

### 저장된 파일 목록 표시
![filelist (1)](https://github.com/heoap9/mediapipe_fastapi_manage/assets/83992590/8672a2e0-33a4-4bfd-86e3-