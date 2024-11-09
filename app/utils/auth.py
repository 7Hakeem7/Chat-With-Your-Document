# app/utils/auth.py
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.db.database import get_db
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from app.utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # Import from config

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password before storing it
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Verify the password against the hashed version stored in the database
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Authenticate user with provided credentials
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        return user
    return None

# Create an access token with expiration
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get the current user from the token
def get_current_user(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user