from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostCreate(BaseModel):
    text: str
    token: str


class PostResponse(BaseModel):
    id: int
    token: str
