from passlib.context import CryptContext

# Configuration of bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Verifying password comparing to database hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Changing password to hash
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)