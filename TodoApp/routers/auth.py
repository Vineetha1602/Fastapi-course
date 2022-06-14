import sys

from starlette.responses import JSONResponse

sys.path.append("..")

from fastapi import Depends, HTTPException, status, APIRouter, Request, Body, Response
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

import models
from passlib.context import CryptContext
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "A1B2C3D4E5FGHIJK9LMNO78aqwexcrtQWE"
ALGORITHM = "HS256"


class LoginModel(BaseModel):
    username: str
    password: str


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):               # for password hashing
    return bcrypt_context.hash(password)


def get_user(email: str, db):
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if not user:
        return None
    return user


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict,
                        expires_delta: Optional[timedelta] = None):
    encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    encode.update({"exp": expire})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(str(token_data.email), db)
    if user is None:
        raise credentials_exception
    return user


@router.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    hash_password = get_password_hash(create_user.password)
    create_user_model.hashed_password = hash_password
    create_user_model.is_active = True
    user_details = {
        "username": create_user_model.username,
        "email": create_user_model.email,
        "password": create_user_model.hashed_password
    }
    db.add(create_user_model)
    db.commit()
    response = {
        "status": True,
        "data": user_details
    }
    return response


@router.post("/login")
async def login(request: LoginModel, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.email == request.username).first()
    if not user:
        raise token_exception()
    if not verify_password(request.password, user.hashed_password):
        raise token_exception()
    access_token = create_access_token(data={"sub": user.email})
    response = {
        "name": user.username,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer"
    }
    return response


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user: object = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/log_out", description="Business logout")
async def log_out():
    response = {
        "status": True,
        "message": "Log out successful"}
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)

# User defined Exceptions


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response

