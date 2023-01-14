from fastapi import FastAPI

from routers import router
from db import db

app = FastAPI()

app.include_router(router, prefix="/api/v1")