import uvicorn

if __name__ == "__main__":  # REST API server를 실행시키기 위한 코드부분 server폴더의 app.py를 url과 포트에 따라 실행시킨다.
        uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
