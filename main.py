from ipaddress import ip_address
import re
from typing import Callable
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, Request, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.routres import contacts, auth, users
from src.config.config import config


app = FastAPI()

'''IP blacklist'''

# banned_ips = [ip_address("192.168.1.1"), ip_address("192.168.1.2")]     #    , ip_address("127.0.0.1")

# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response

'''UserAgent blacklist'''

# user_agent_ban_list = [r"bot-Yandex"]


# @app.middleware("http")
# async def user_agent_ban_middleware(request: Request, call_next: Callable):
#     print(request.headers)
#     user_agent = request.headers.get("user-agent")
#     print(user_agent)
#     for ban_pattern in user_agent_ban_list:
#         if re.search(ban_pattern, user_agent):
#             return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response

'''CORS'''

origins = ["*"]     #   public; or origins = ["http://localhost:3000"] for some web on localhost:port

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  #     True for JWT tokens
    allow_methods=["*"],  #     [*] for all or ["GET, POST, PUT, DELETE"]
    allow_headers= ["*"]   #     [*] for all or ["Authorization"]
)

BASE_DIR = Path('.')

app.mount('/static', StaticFiles(directory=BASE_DIR /'src' / 'static'), name='static')

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=config.REDIS_DOMAIN, 
                          port=config.REDIS_PORT, 
                          db=0, 
                          password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


templates = Jinja2Templates(directory=BASE_DIR /'src' /'templates')


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'our': 'Contact book on REST API'})

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        reult = result.fetchone() 
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)