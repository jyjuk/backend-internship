from typing import Optional
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    sub: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
