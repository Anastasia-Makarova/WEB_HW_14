import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter


from src.entity.models import User
from src.services.auth import auth_service
from src.schemas.user import UserResponse
from src.database.db import get_db
from src.config.config import config
from src.repository import users as repository_users


router = APIRouter(prefix='/users', tags=['users'])
cloudinary.config(cloud_name=config.CLD_NAME, 
                  api_key=config.CLD_API_KEY, 
                  api_secret=config.CLD_API_SECRET,
                  secure=True)

@router.get('/me', response_model=UserResponse, 
            description='No more than 1 requests per 20 sec',
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.patch('/avatar', response_model=UserResponse, 
              description='No more than 1 requests per 20 sec',
              dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_avatar(file: UploadFile = File(),  
                        user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_db)):
    public_id = f"Web18/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    return user


@router.patch('/password', response_model=UserResponse, 
              description='No more than 1 requests per 20 sec',
              dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_password(old_password: str,  
                          new_password: str,
                          user: User = Depends(auth_service.get_current_user),
                          db: AsyncSession = Depends(get_db)):
    if not auth_service.verify_password(old_password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    new_password = auth_service.get_password_hash(new_password)
    user = await repository_users.update_password(user.email, new_password, db)
    return user