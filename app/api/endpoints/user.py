# app/api/endpoints/user.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.auth import authenticate_user, get_current_user, get_password_hash
from app.db.database import get_db
from app.db.schemas import UserCreate, UserResponse , UserLogin  # Import UserCreate model
from app.models.user import User  # Import your User model
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.utils.jwt import create_access_token

router = APIRouter()

@router.post("/register/", response_model=UserResponse)  # Add registration endpoint
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)  # Hash the password
    new_user = User(username=user.username, password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(id=new_user.id, username=new_user.username)

@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_record = authenticate_user(db, user.username, user.password)
    if not user_record:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create a JWT token
    access_token_expires = timedelta(minutes=30)  # or use ACCESS_TOKEN_EXPIRE_MINUTES if defined
    access_token = create_access_token(
        data={"sub": user_record.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(id=user_record.id, username=user_record.username)
    }


@router.get("/current-user/", response_model=UserResponse)  # Protected route to get current user
async def get_current_user_route(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, username=current_user.username)  # Return the current user's info