from strawberry.types import Info
from typing import Optional
from .models import Role
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy import select
from .models import User as UserModel
from strawberry.permission import BasePermission
import uuid


SECRET_KEY = "83daa0256a2289b0fb23693bf1f60354d44396675749244721a2b20e896e1162"
ALGORITHM = "HS256"

def get_id_from_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    id: str = payload.get("id")
    id = uuid.UUID(id)
    return id
    

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str, db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    
    user = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type = payload.get("token_type")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        
        if token_type!='refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your token is invalid"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials, Maybe your token is expired"
        )
    return payload


class IsAunthenticated(BasePermission):

    message = "you must be logged in to access this resource"
    
    async def has_permission(self, source, info: Info, **kwargs):
        token = info.context['request'].headers.get('Authorization', '').replace('Bearer ', '')
        session = info.context['session']
        current_user = await get_current_user(token, db=session)

        if current_user is None:
            raise HTTPException(status_code=403, detail=self.message)
        return True
    

class IsAdmin(BasePermission):
    message = "Unauthorized access. You are not an Admin"

    async def has_permission(self, source, info: Info, **kwargs):
        token = info.context['request'].headers.get('Authorization', '').replace('Bearer ', '')

        session = info.context['session']
        current_user = await get_current_user(token, db=session)
        if current_user.role==Role.USER:
            raise HTTPException(status_code=403, detail=self.message)
        return True
