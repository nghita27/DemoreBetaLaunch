# schemas.py

from pydantic import BaseModel, EmailStr

# ----- For registration -----
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# ----- For login token -----
class Token(BaseModel):
    access_token: str
    token_type: str

# ----- For public user display (optional future use) -----
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
