from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.routers.main import api_router

app = FastAPI(
    title=settings.PROJECT_NAME, debug=settings.DEBUG, root_path=settings.API_V1
)

setup_exception_handlers(app)
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}
