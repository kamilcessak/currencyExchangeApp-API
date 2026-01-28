import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId

from app.models.token import TokenBlacklist
from app.models.user import User

TOKEN_EXPIRATION_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("You dont set secret key")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configuration of bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Verifying password comparing to database hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Changing password to hash
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Creating access token
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject)
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    is_blacklisted = await TokenBlacklist.find_one(TokenBlacklist.token == token)
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User logged out - Invalid token"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await User.get(PydanticObjectId(user_id))

    if user is None:
        raise credentials_exception

    return user

