import os
import re
import hashlib
import secrets
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Response, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repo import ResumeRepo, User


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

SECRET_FILE = Path(os.getenv("JWT_SECRET_FILE", "data/.jwt_secret"))
def _get_or_create_secret() -> str:
    if (env_secret := os.getenv("JWT_SECRET_KEY")):
        return env_secret
    try:
        with open(SECRET_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
        new_secret = secrets.token_hex(32)
        with open(SECRET_FILE, "w") as f:
            f.write(new_secret)
        return new_secret

SECRET_KEY = _get_or_create_secret()
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))
CSRF_TOKEN_EXPIRE_SECONDS = 3600
SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    nickname: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError("用户名至少需要3个字符")
        if len(v) > 20:
            raise ValueError("用户名不能超过20个字符")
        if ":" in v:
            raise ValueError("用户名不能包含冒号")
        if not re.match(r"^[a-zA-Z0-9_\u4e00-\u9fa5]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线和中文")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError("请输入邮箱")
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v):
            raise ValueError("请输入有效的邮箱地址")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("密码至少需要6个字符")
        if len(v) > 50:
            raise ValueError("密码不能超过50个字符")
        return v


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('请输入用户名')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError('请输入密码')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    csrf_token: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_value = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}:{hash_value.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, stored_hash = password_hash.split(":")
        hash_value = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return secrets.compare_digest(hash_value.hex(), stored_hash)
    except Exception:
        return False


def create_token(user_id: int, username: str) -> str:
    expire_time = int(time.time()) + TOKEN_EXPIRE_HOURS * 3600
    payload = f"{user_id}:{username}:{expire_time}"
    signature = hashlib.sha256(f"{payload}:{SECRET_KEY}".encode()).hexdigest()
    return f"{payload}:{signature}"


def verify_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return None
        
        user_id_str, username, expire_str, signature = parts
        user_id = int(user_id_str)
        expire_time = int(expire_str)
        
        if expire_time < int(time.time()):
            return None
        
        payload = f"{user_id}:{username}:{expire_time}"
        expected_signature = hashlib.sha256(f"{payload}:{SECRET_KEY}".encode()).hexdigest()
        
        if not secrets.compare_digest(signature, expected_signature):
            return None
        
        return {"user_id": user_id, "username": username}
    except Exception:
        return None


def create_csrf_token() -> str:
    return secrets.token_urlsafe(32)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = None

    if credentials:
        token = credentials.credentials
    elif request.cookies.get("access_token"):
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="未登录")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    repo = ResumeRepo(db)
    user = await repo.get_user_by_id(payload["user_id"])

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, response: Response, db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)

    existing_user = await repo.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    existing_email = await repo.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    password_hash = hash_password(user_data.password)

    try:
        user_id = await repo.create_user(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            nickname=user_data.nickname
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

    user = await repo.get_user_by_id(user_id)
    token = create_token(user_id, user_data.username)
    csrf_token = create_csrf_token()
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=TOKEN_EXPIRE_HOURS * 3600,
        path="/"
    )
    
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=CSRF_TOKEN_EXPIRE_SECONDS,
        path="/"
    )
    
    return TokenResponse(
        access_token=token,
        csrf_token=csrf_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            nickname=user.nickname,
            avatar=user.avatar,
            created_at=user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)

    user = await repo.get_user_by_username(user_data.username)
    if not user:
        user = await repo.get_user_by_email(user_data.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = create_token(user.id, user.username)
    csrf_token = create_csrf_token()
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=TOKEN_EXPIRE_HOURS * 3600,
        path="/"
    )
    
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=CSRF_TOKEN_EXPIRE_SECONDS,
        path="/"
    )
    
    return TokenResponse(
        access_token=token,
        csrf_token=csrf_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            nickname=user.nickname,
            avatar=user.avatar,
            created_at=user.created_at
        )
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    return MessageResponse(message="已成功登出")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        created_at=current_user.created_at
    )


@router.get("/check", response_model=dict)
async def check_auth(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")

    if not token:
        return {"authenticated": False}

    payload = verify_token(token)
    if not payload:
        return {"authenticated": False}

    repo = ResumeRepo(db)
    user = await repo.get_user_by_id(payload["user_id"])
    
    if not user:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "avatar": user.avatar
        }
    }
