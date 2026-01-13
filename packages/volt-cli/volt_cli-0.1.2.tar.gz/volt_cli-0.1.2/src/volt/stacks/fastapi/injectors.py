import re
from pathlib import Path

from rich import print

from volt.core.injectors import replace_pattern_in_file
from volt.stacks.constants import DB_SQL_MODEL, DB_NOSQL_MODEL

ASYNC_CONTEXT_IMPORT = "from contextlib import asynccontextmanager"


def inject_lifespan_for_mongo(main_file: Path):
    content = main_file.read_text()
    if "lifespan=" in content:
        return

    pattern = r"app\s*=\s*FastAPI\s*\(([^)]*)\)"
    match = re.search(pattern, content)
    if not match:
        raise RuntimeError("FastAPI app instance not found in main.py")

    lifespan_code = """\n
from contextlib import asynccontextmanager
from app.core.db import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
"""

    new_content = re.sub(
        pattern,
        f"{lifespan_code}\napp = FastAPI(\\1, lifespan=lifespan)",
        content,
    )
    main_file.write_text(new_content)


def inject_lifespan_for_sqlmodel(main_file: Path):
    content = main_file.read_text()
    if "lifespan=" in content:
        return

    pattern = r"app\s*=\s*FastAPI\s*\(([^)]*)\)"
    match = re.search(pattern, content)
    if not match:
        raise RuntimeError("FastAPI app instance not found in main.py")

    lifespan_code = """\n
from contextlib import asynccontextmanager
from app.core.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
"""

    new_content = re.sub(
        pattern,
        f"{lifespan_code}\napp = FastAPI(\\1, lifespan=lifespan)",
        content,
    )
    main_file.write_text(new_content)


def inject_lifespan(db_choice: str, main_file: Path):
    if db_choice in DB_NOSQL_MODEL:
        inject_lifespan_for_mongo(main_file)
    elif db_choice in DB_SQL_MODEL:
        inject_lifespan_for_sqlmodel(main_file)
    else:
        raise ValueError(f"Unsupported database choice: {db_choice}")


def register_model_in_init_beanie(root: Path, model_name: str):
    db_file = root / "app" / "core" / "db.py"
    content = db_file.read_text()

    import_stmt = (
        f"from app.models.{model_name.lower()} import {model_name.capitalize()}"
    )

    if import_stmt not in content:
        content = re.sub(
            r"^(from .+|import .+)$",
            r"\1\n" + import_stmt,
            content,
            count=1,
            flags=re.MULTILINE,
        )

    pattern = r"await\s+init_beanie\s*\(\s*database\s*=\s*db\s*,\s*document_models\s*=\s*\[([^\]]*)\]\s*\)"
    match = re.search(pattern, content, flags=re.DOTALL)

    if not match:
        db_file.write_text(content)
        return

    existing_models = match.group(1).strip()
    if existing_models:
        models = [m.strip() for m in existing_models.split(",") if m.strip()]
        if model_name not in models:
            models.append(model_name)
        new_models = ", ".join(models)
    else:
        new_models = model_name

    new_content = re.sub(
        pattern,
        f"await init_beanie(database=db, document_models=[{new_models}])",
        content,
    )
    db_file.write_text(new_content)


def setup_health_router(project_path: Path, db_choice: str):
    routers_dir = project_path / "app" / "routers"
    health_file = routers_dir / "health.py"
    routers_main = routers_dir / "main.py"

    if health_file.exists():
        print("[yellow]Health router already exists, skipping creation.[/yellow]")
    else:
        health_code = """from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def health_check():
    return {"status": "ok"}
"""
        health_file.write_text(health_code)

    main_content = routers_main.read_text()
    if "from app.routers.health import router as health_router" not in main_content:
        import_line = "from app.routers.health import router as health_router"
        if "from fastapi import APIRouter" in main_content:
            main_content = main_content.replace(
                "from fastapi import APIRouter",
                f"from fastapi import APIRouter\n{import_line}",
            )
        else:
            main_content = f"{import_line}\n" + main_content

        if "api_router.include_router(health_router)" not in main_content:
            main_content = main_content.replace(
                "api_router = APIRouter()",
                "api_router = APIRouter()\napi_router.include_router(health_router)",
            )
        routers_main.write_text(main_content)

    content = health_file.read_text()
    if "async def database_health" in content:
        return

    if db_choice == "MongoDB":
        db_health = """
from fastapi import HTTPException
import app.core.db as db

@router.get("/db")
async def database_health():
    try:
        if not db.client:
            raise Exception("Database not initialized")
        await db.client.admin.command("ping")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not reachable: {e}")
    return {"status": "ok", "database": "reachable"}
"""
        health_file.write_text(content.strip() + "\n" + db_health)
    elif db_choice in DB_SQL_MODEL:
        db_health = """
from fastapi import Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.core.db import get_session

@router.get("/db")
async def database_health(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not reachable: {e}")
    return {"status": "ok", "database": "reachable"}
"""
        health_file.write_text(content.strip() + "\n" + db_health)


def inject_redis_healthcheck(project_path: Path):
    health_file = project_path / "app" / "routers" / "health.py"
    if not health_file.exists():
        setup_health_router(project_path, "None")

    content = health_file.read_text()
    if "async def redis_health" in content:
        return

    redis_health = """
from fastapi import Depends
from app.core.redis import get_redis

@router.get("/redis")
async def redis_health(redis=Depends(get_redis)):
    return {"status": await redis.ping()}
"""
    health_file.write_text(content.strip() + "\n" + redis_health)


def inject_auth_routers(routers_file: Path):
    new_router_code = """api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
"""

    content = routers_file.read_text()

    if "app.routers.auth.routes" in content and "app.routers.users.routes" in content:
        print("[yellow]Routers already injected, skipping.[/yellow]")
        return

    pattern = r"api_router\s*=\s*APIRouter\(\)"
    import_pattern = r"from fastapi import APIRouter"
    if import_pattern not in content:
        print("[yellow]APIRouter not found, skipping.[/yellow]")
        return

    import_code = """from fastapi import APIRouter
from app.routers.auth.routes import router as auth_router
from app.routers.users.routes import router as user_router
"""

    replace_pattern_in_file(routers_file, pattern, new_router_code.strip())
    replace_pattern_in_file(routers_file, import_pattern, import_code.strip())


def inject_users_model(models_file: Path, db_choice: str):
    if db_choice == "MongoDB":
        register_model_in_init_beanie(models_file.parent.parent.parent, "User")
        new_model_code = """from beanie import Document
from pydantic import EmailStr


class User(Document):
    username: str
    email: EmailStr
    hashed_password: str
    disabled: bool = False

    class Settings:
        name = "users"
"""
    elif db_choice in DB_SQL_MODEL:
        new_model_code = """from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    email: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str
    disabled: bool = False
"""
    else:
        raise ValueError(f"Unsupported database choice: {db_choice}")

    models_file.write_text(new_model_code)


def inject_redis(main_file: Path):
    content = main_file.read_text()
    if "init_redis" in content:
        return

    import_code = "from app.core.redis import init_redis, close_redis"
    if ASYNC_CONTEXT_IMPORT not in content:
        content = re.sub(
            r"(from fastapi import FastAPI[^\n]*)",
            r"\1\n" + ASYNC_CONTEXT_IMPORT,
            content,
        )

    if import_code not in content:
        content = re.sub(
            r"(from fastapi import FastAPI)", r"\1\n" + import_code, content
        )

    if "async def lifespan(app: FastAPI):" in content:
        content = re.sub(
            r"(async def lifespan\(app: FastAPI\):)",
            r"\1\n    await init_redis()",
            content,
        )
        content = re.sub(r"(yield)", r"\1\n    await close_redis()", content)
    else:
        lifespan_code = """
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()
"""
        pattern = r"app\s*=\s*FastAPI\s*\(([^)]*)\)"
        content = re.sub(
            pattern,
            f"{lifespan_code}\napp = FastAPI(\\1, lifespan=lifespan)",
            content,
        )

    main_file.write_text(content)


def inject_sentry(main_file: Path):
    content = main_file.read_text()
    if "sentry_sdk.init" in content:
        return

    import_code = """import sentry_sdk
from app.core.config import settings"""

    init_code = """
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        send_default_pii=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
"""

    if "import sentry_sdk" not in content:
        content = import_code + "\n" + content

    pattern = r"(app\s*=\s*FastAPI\s*\([^)]*\))"
    content = re.sub(pattern, r"\1\n" + init_code, content)

    main_file.write_text(content)


def inject_logfire(main_file: Path):
    content = main_file.read_text()
    if "logfire.instrument_fastapi" in content:
        return

    import_code = """import logfire
from app.core.config import settings"""

    init_code = """
if settings.LOGFIRE_TOKEN:
    logfire.configure(token=settings.LOGFIRE_TOKEN)
    logfire.instrument_fastapi(app)
"""

    if "import logfire" not in content:
        content = import_code + "\n" + content

    pattern = r"(app\s*=\s*FastAPI\s*\([^)]*\))"
    content = re.sub(pattern, r"\1\n" + init_code, content)

    main_file.write_text(content)


def setup_exception_infrastructure(app_path: Path):
    """Ensures exceptions.py exists and is registered in main.py."""
    from volt.core.template import TEMPLATES_ROOT
    import shutil

    exception_path = app_path / "app" / "core" / "exceptions.py"
    main_file = app_path / "app" / "main.py"

    # 1. Ensure app/core/exceptions.py exists
    if not exception_path.exists():
        exception_path.parent.mkdir(parents=True, exist_ok=True)

        template_path = (
            TEMPLATES_ROOT / "fastapi" / "base" / "app" / "core" / "exceptions.py"
        )
        shutil.copy(template_path, exception_path)

    # 2. Ensure app/main.py calls setup_exception_handlers
    if main_file.exists():
        content = main_file.read_text()
        import_line = "from app.core.exceptions import setup_exception_handlers"
        setup_call = "setup_exception_handlers(app)"

        if import_line not in content:
            lines = content.splitlines()
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, import_line)
            content = "\n".join(lines) + "\n"

        if setup_call not in content:
            content = re.sub(
                r"(app\s*=\s*FastAPI\(.*?\))",
                r"\1\n\n" + setup_call,
                content,
                flags=re.DOTALL,
            )
        main_file.write_text(content)


def add_exception_to_map(
    app_path: Path,
    exception_class_name: str,
    status_code: int,
    exception_definition: str = None,
):
    """Adds an exception class and its mapping to app/core/exceptions.py."""
    exception_path = app_path / "app" / "core" / "exceptions.py"
    if not exception_path.exists():
        setup_exception_infrastructure(app_path)

    content = exception_path.read_text()

    # Add class definition if provided and not present
    if exception_definition and exception_class_name not in content:
        # Find the line before EXCEPTION_MAP
        content = re.sub(
            r"EXCEPTION_MAP\s*=\s*{",
            f"{exception_definition}\n\nEXCEPTION_MAP = {{",
            content,
        )

    # Add to EXCEPTION_MAP if not present
    mapping_entry = f"{exception_class_name}: {status_code},"
    if mapping_entry not in content:
        content = re.sub(
            r"EXCEPTION_MAP\s*=\s*{([^}]*)}",
            f"EXCEPTION_MAP = {{\\1    {mapping_entry}\n}}",
            content,
            flags=re.DOTALL,
        )

    exception_path.write_text(content)
