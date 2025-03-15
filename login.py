from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas import UserCreate, UserLogin
from data_base import get_db
from models import User
from passlib.context import CryptContext
import uuid
import datetime


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


@router.post("/registration/")
def registration(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user (UserCreate): The user information for registration.
        db (Session): The database session.

    Returns:
        dict: A message indicating successful user creation.

    Raises:
        HTTPException: If the email is already registered.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=user.email, hashed_password=pwd_context.hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@router.post("/login/")

def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a token.

    Args:
        user (UserLogin): The user login information.
        db (Session): The database session.

    Returns:
        dict: A token for the authenticated user.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = uuid.uuid4().hex[:32]
    db_user.token = token
    db_user.last_action = datetime.datetime.now()
    db.commit()
    db.refresh(db_user)
    
    return {"token": token}

