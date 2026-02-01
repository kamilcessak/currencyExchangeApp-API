import secrets
from fastapi import APIRouter, HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError
from fastapi.security import OAuth2PasswordBearer

from app.models.token import TokenBlacklist
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas import (
    UserRegister, UserResponse, Token, UserLogin, UserUpdate,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.utils.security import get_password_hash, create_access_token, verify_password, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    exists = await User.find_one(User.email == user_data.email)

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="User with this email already exists!"
        )

    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        balances=[]
    )

    try:
        await new_user.create()
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="User with this email already exists!"
        )
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred while creating user!"
        )

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name
    )

@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin):
    user = await User.find_one(User.email == user_data.email)

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
async def user_data(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return current_user

    if "email" in update_data:
        exists = await User.find_one(User.email == update_data["email"])
        if exists and exists.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already taken",
            )

    for field, value in update_data.items():
        setattr(current_user, field, value)
    await current_user.save()

    return current_user

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(token: str = Depends(oauth2_scheme)):
    exists = await TokenBlacklist.find_one(TokenBlacklist.token == token)

    if not exists:
        await TokenBlacklist(token=token).create()

    return {
        "message": "User logged out successfully"
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: ForgotPasswordRequest):
    user = await User.find_one(User.email == data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist",
        )

    await PasswordResetToken.find(PasswordResetToken.email == user.email).delete()

    token = secrets.token_urlsafe(32)
    await PasswordResetToken(token=token, email=user.email).create()

    return {
        "message": "Password reset token generated. Valid for 15 minutes.",
        "reset_token": token,
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetPasswordRequest):
    reset_record = await PasswordResetToken.find_one(PasswordResetToken.token == data.token)

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = await User.find_one(User.email == reset_record.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = get_password_hash(data.new_password)
    await user.save()

    await reset_record.delete()

    return {
        "message": "Password has been reset successfully",
    }
