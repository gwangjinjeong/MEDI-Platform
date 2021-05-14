# 기본
from fastapi import FastAPI
from server.routes.userRouter import router as UserRouter
# from server.routes.bcmRouter import router as BCMRouter

app = FastAPI()

app.include_router(UserRouter, tags=["User"], prefix="/user")
# app.include_router(BCMRouter, tags=["bcm"], prefix="/bcm")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}
# def index():
#     return {'data': 'blog list'}



# @app.get('/blog/{blog_id}')
# def show(blog_id):
#     # fetch blog with id = id
#     return {'data': blog_id}

# @app.get('/blog/{blog_id}/comments')
# def show(blog_id):
#     # fetch blog with id = id
#     return {'data': 'gwangjin'}