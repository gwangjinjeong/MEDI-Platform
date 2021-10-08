from fastapi import FastAPI
from server.routes.userRouter import router as UserRouter

app = FastAPI() # 서버에 접속시 FastAPI를 실행

app.include_router(UserRouter, tags=["User"], prefix="/user") # 서버에 접속시 root 말고 user쪽 추가


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}
