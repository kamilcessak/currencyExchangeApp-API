from fastapi import APIRouter, HTTPException, status, Depends
from pymongo.errors import DuplicateKeyError
from fastapi.security import OAuth2PasswordBearer

from app.models.token import TokenBlacklist
from app.models.user import User
from app.schemas import UserRegister, UserResponse, Token, UserLogin
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

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(token: str = Depends(oauth2_scheme)):
    exists = await TokenBlacklist.find_one(TokenBlacklist.token == token)

    if not exists:
        await TokenBlacklist(token=token).create()

    return {
        "message": "User logged out successfully"
    }
