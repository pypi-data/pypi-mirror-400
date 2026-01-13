from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.db import get_session
from app.core.security import verify_password, create_access_token, get_password_hash
from app.schemas.auth import Token, UserCreate
from app.models.user import User

router = APIRouter(tags=["Authentification"])


@router.post("/login")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()

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
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(select(User).where(User.username == user.username))
    existing_user = result.first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    result = await session.execute(select(User).where(User.email == user.email))
    exists_email = result.first()
    if exists_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    session.add(
        User(username=user.username, email=user.email, hashed_password=hashed_password)
    )
    await session.commit()

    token = create_access_token(data={"sub": user.username})

    return Token(access_token=token, token_type="bearer")
