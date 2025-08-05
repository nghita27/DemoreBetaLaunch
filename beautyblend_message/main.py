# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.middleware.cors import CORSMiddleware

from auth import (
    create_access_token, verify_password, get_password_hash, get_current_user
)
from database import Base, engine, get_async_session
from models import User
from schemas import UserCreate, Token

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Register
@app.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    await db.commit()
    return {"message": "User registered successfully"}

# Login
@app.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route
@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}
