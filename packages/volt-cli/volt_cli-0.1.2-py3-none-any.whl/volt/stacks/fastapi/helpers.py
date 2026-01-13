from pathlib import Path

from volt.core.template import copy_template
from volt.stacks.constants import DB_NOSQL_MODEL, DB_SQL_MODEL
from volt.stacks.fastapi.injectors import (
    inject_auth_routers,
    inject_users_model,
    setup_health_router,
    inject_lifespan,
    inject_redis_healthcheck,
)


def setup_db_templates(dest: Path, db_choice: str):
    from volt.stacks.constants import DB_NOSQL_MODEL
    from volt.stacks.constants import DB_SQL_MODEL

    if db_choice in DB_SQL_MODEL:
        copy_template("fastapi", "db_sqlmodel", dest, True)
    elif db_choice in DB_NOSQL_MODEL:
        copy_template("fastapi", "db_mongo", dest, True)

    if db_choice != "None":
        inject_lifespan(db_choice, dest / "app" / "main.py")
        setup_health_router(dest, db_choice)


def setup_auth_templates(dest: Path, auth_choice: str, db_choice: str):
    if auth_choice == "None":
        return
    auth_type = "auth_bearer" if "Bearer" in auth_choice else "auth_cookie"
    auth_type_model = f"{auth_type}_model"
    copy_template("fastapi", auth_type, dest, True)

    inject_auth_routers(dest / "app" / "routers" / "main.py")
    inject_users_model(dest / "app" / "models" / "user.py", db_choice)

    if db_choice in DB_NOSQL_MODEL:
        copy_template("fastapi", f"{auth_type_model}/mongo", dest, True)
    elif db_choice in DB_SQL_MODEL:
        copy_template("fastapi", f"{auth_type_model}/sqlmodel", dest, True)


def setup_alembic_templates(dest: Path):
    from volt.core.template import copy_template

    copy_template("fastapi", "alembic", dest, True)


def setup_redis_templates(dest: Path):
    from volt.core.template import copy_template
    from volt.stacks.fastapi.injectors import inject_redis

    copy_template("fastapi", "redis", dest, True)
    inject_redis(dest / "app" / "main.py")
    inject_redis_healthcheck(dest)
