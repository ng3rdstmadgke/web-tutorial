from fastapi import FastAPI
from routers import router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # クロスオリジンリクエストを許可するオリジンのリスト。 "*" はすべて許可。
    allow_credentials=True,  # Cookieがクロスオリジンリクエストに対してサポートされるべきかどうか。
    allow_methods=["*"],     # クロスオリジンリクエストで許可されるHTTPメソッドのリスト。 "*" はすべて許可。
    allow_headers=["*"],     # クロスオリジンリクエストで許可されるHTTPヘッダのリスト。 "*" はすべて許可。
)

app.include_router(router, prefix="/api/v1")

# html=True : パスの末尾が "/" の時に自動的に index.html をロードする
# name="static" : FastAPIが内部的に利用する名前を付けます
app.mount("/", StaticFiles(directory=f"/opt/app/static", html=True), name="static")