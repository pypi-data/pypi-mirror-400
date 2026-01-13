from typing import Annotated

from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.schemas.auth import Token, UserCreate
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

router = APIRouter(tags=["Authentification"])


@router.post("/login")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await User.find_one(User.username == form.username)

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.username})

    return Token(access_token=token, token_type="bearer")


@router.post("/register")
async def register(
    user: UserCreate,
):
    existing_user = await User.find_one(User.username == user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    exists_email = await User.find_one(User.email == user.email)
    if exists_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    await User.insert_one(
        User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )
    )

    token = create_access_token(data={"sub": user.username})

    return Token(access_token=token, token_type="bearer")
