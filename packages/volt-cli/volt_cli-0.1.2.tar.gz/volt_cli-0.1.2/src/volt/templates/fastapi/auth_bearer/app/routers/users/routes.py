from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from app.dependencies.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
