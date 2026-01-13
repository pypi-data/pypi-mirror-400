from typing import Annotated

from app.core.config import settings
from app.core.db import get_session
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.schemas.auth import UserCreate
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

router = APIRouter(tags=["Authentification"])


@router.post("/login")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad credentials",
        )
    token = create_access_token(data={"sub": user.username})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
    )

    return {
        "message": "Login successful",
    }


@router.post("/register")
async def register(
    user: UserCreate,
    response: Response,
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

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
    )

    return {
        "message": "User successfully registered",
    }
