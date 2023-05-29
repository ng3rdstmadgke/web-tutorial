from fastapi import FastAPI
from routers import router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(router, prefix="/api/v1")

# html=True : パスの末尾が "/" の時に自動的に index.html をロードする
# name="static" : FastAPIが内部的に利用する名前を付けます
app.mount("/", StaticFiles(directory=f"/opt/app/static", html=True), name="static")