import pathlib
import time

import redis.asyncio as redis
from datetime import date, timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.database.connect import get_db
from src.database.models import User
from src.routes import auth, users, photos, comments, rating
from src.schemas import UserDb
from src.conf.config import settings
from utils.py_logger import get_logger


app = FastAPI()
origins = ["*"]
logger = get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["Process-Time"] = str(process_time)
    return response


templates = Jinja2Templates(directory="templates")
# BASE_DIR = pathlib.Path(__file__).parent
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "PS4"}
    )


# @app.on_event("startup")
# async def startup():
#     r = await redis.Redis(
#         host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
#     )
#     await FastAPILimiter.init(r)


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to PhotoShare4!"}
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


@app.get("/", name="Info page")
def info():
    return {"message": "Welcome to Photo Share"}


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(rating.router, prefix="/api")
