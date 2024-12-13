from typing import Optional
from .models import Role
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Request, Depends
from sqlalchemy import select
from .models import User as UserModel
from .db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "FhOUJeYYgk2JdozbN67j_C9aLwVBdABNOfQNqkV0gpg3-LQOXXAiQuSMv56g5g7v9xUTc0PW8uSycxwjbf_Aaw"
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True})
        token_type = payload.get("token_type") 
        user_id: str = payload.get("id")
        user_id = uuid.UUID(user_id)

        if token_type=="refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Maybe your token has expired"
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Maybe your token is invalid"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        user_id = uuid.UUID(user_id)
        
        token_type = payload.get("token_type")

        if user_id is None:
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
            detail=str(e)
        )
    
    return payload


    
async def is_authenticated(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):

    if token =="":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no token found")
    
    current_user = await get_current_user(token, db=session)

    if current_user is None:
        raise HTTPException(status_code=403, detail="you are not logged in")
    return current_user
    


async def is_admin(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):

    if token =="":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no token found")
    
    current_user = await get_current_user(token, db=session)

    if current_user.role==Role.USER:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="You are not an admin")
    return current_user


