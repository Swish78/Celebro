from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from backend.core.config import MONGODB_URI, DATABASE_NAME, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.models.user import UserCreate, UserResponse, TokenData, Token
from pytz import timezone


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.client = AsyncIOMotorClient(MONGODB_URI)
        self.db = self.client[DATABASE_NAME]
        self.users_collection = self.db['users']
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
            salt = hashed_password.split('$')[1]
            return self.get_password_hash(plain_password, salt) == hashed_password

    def get_password_hash(self, password: str, salt: str = None) -> str:
            if salt is None:
                salt = secrets.token_hex(16)

            # Using SHA-256 for hashing
            hashed = hashlib.sha256((password + salt).encode()).hexdigest()
            return f'sha256${salt}${hashed}'

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.now(timezone("Asia/Kolkata")) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def get_current_user(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception

        user = await self.get_user_by_username(token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def authenticate_user(self, username: str, password: str):
        user = await self.users_collection.find_one({"username": username})
        if not user or not self.verify_password(password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        return UserResponse(**user)

    async def create_user(self, user: UserCreate):
        hashed_password = self.get_password_hash(user.password)
        user_doc = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow()
        }

        try:
            await self.users_collection.create_index([("username", 1)], unique=True)
            await self.users_collection.create_index([("email", 1)], unique=True)
            await self.users_collection.insert_one(user_doc)
            return UserResponse(**user_doc)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

    async def get_user_by_username(self, username: str):
        user = await self.users_collection.find_one({"username": username})
        return UserResponse(**user) if user else None
