from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User as UserModel, Role
from .schema import *
from .db import get_db
from .auth import create_access_token, verify_refresh_token, is_authenticated, is_admin
import uuid
from datetime import timedelta

router = APIRouter()

@router.post("/user/register", response_model=UserType)
async def register(
    user_data: CreateUserRequest, 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UserModel).where(UserModel.username == user_data.username)
    existing_user = await db.execute(stmt)
    existing_user = existing_user.fetchall()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    new_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        hashed_password=UserModel.hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserType(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role="ADMIN" if new_user.role == Role.ADMIN else "USER",
        createdOn=new_user.created_on,
    )


@router.post("/user/login", response_model=AuthResponse)
async def login(
    user_data: UserLoginRequest, db: AsyncSession = Depends(get_db)
):
    user = await db.execute(select(UserModel).filter(UserModel.username == user_data.username))
    user = user.scalar_one_or_none()

    if not user or not user.verify_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        data={"sub": user.username, "id": str(user.id), "token_type": "access"},
        expires_delta=timedelta(days=1),
    )
    refresh_token = create_access_token(
        data={"sub": user.username, "id": str(user.id), "token_type": "refresh"},
        expires_delta=timedelta(days=2),
    )

    return AuthResponse(access_token=access_token, refresh_token=refresh_token)



@router.put("/user/update/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    user_data: UserType,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated)
):
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data is None:
        return UserType.model_validate(user)
    
    updated_fields = {}

    if user_data.username:
        user.username = user_data.username
        updated_fields["username"] = user_data.username

    if user_data.email:
        user.email = user_data.email or user.email
        updated_fields["email"] = user_data.email   

    if user_data.first_name:
        user.first_name = user_data.first_name or user.first_name
        updated_fields["first_name"] = user_data.first_name   
    
    if user_data.last_name:
        user.last_name = user_data.last_name or user.last_name
        updated_fields["last_name"] = user_data.last_name   

    if user_data.phone_no:
        updated_fields["phone_no"] = user_data.phone_no   
        user.phone_no = user_data.phone_no or user.phone_no

    await db.commit()
    await db.refresh(user)
    print(updated_fields)
    return updated_fields


@router.delete("/user/delete/{user_id}", response_model=UserType)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    user_id = uuid.UUID(user_id)

    user = await db.get(UserModel, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()

    return UserType(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role="ADMIN" if user.role == Role.ADMIN else "USER",
    )


@router.get("/user/get/{user_id}", response_model=UserType)
async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect user ID")
    return UserType(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role="ADMIN" if user.role == Role.ADMIN else "USER",
        created_on=user.created_on
    )


@router.get("/user/get-all", response_model=list[UserType])
async def get_all_users(db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    stmt = select(UserModel)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [
        UserType(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role="ADMIN" if user.role == Role.ADMIN else "USER",
        )
        for user in users
    ]

@router.post("/user/{user_id}/role", response_model=UserType)
async def assign_role(user_id: uuid.UUID, user_role: AssignRoleRequest, db: AsyncSession = Depends(get_db), admin: UserModel = Depends(is_admin)):
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_role.role = user_role.role.upper()

    if user_role.role not in Role.__members__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    user.role = Role.__dict__[user_role.role]
    await db.commit()
    await db.refresh(user)

    return UserType(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role="ADMIN" if user.role == Role.ADMIN else "USER",
        created_on=user.created_on
    )


# --- Reset Password ---
@router.post("/user/reset-password")
async def reset_password(user_data: ResetPasswordRequest, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_authenticated)):
    user = await db.execute(select(UserModel).filter(UserModel.username == user_data.username))
    user = user.scalar_one_or_none()

    if not user or not user.verify_password(user_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if user_data.new_password == user_data.old_password:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="new password can not be same as the old password"
        )

    user.hashed_password = UserModel.hash_password(user_data.new_password)
    await db.commit()
    await db.refresh(user)
    return "Your password has been reset successfully"


@router.post("/user/refresh", response_model=AuthResponse)
async def refresh_access_token(request: Request):
    
    refresh_token = request.headers.get("Refresh", "").replace("Bearer ", "")

    payload = verify_refresh_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = create_access_token(
        data={"sub": payload["sub"], "id": str(payload["id"])},
        expires_delta=timedelta(minutes=15)
    )

    return AuthResponse(access_token=access_token, refresh_token=refresh_token)