import getpass
import secrets
from pathlib import Path

from volt.core.template import add_env_variables
from volt.stacks.constants import SQL_DEFAULT_DATABASE, DB_USER_DEFAULT

DB_CONFIGS = {
    "SQLite": {
        "vars": {"DB_NAME": None},
        "uri": "sqlite+aiosqlite:///{self.DB_NAME}",
    },
    "PostgreSQL": {
        "vars": {
            "DB_HOST": "localhost",
            "DB_PORT": 5432,
            "DB_USER": None,
            "DB_NAME": "postgres",
        },
        "uri": (
            "postgresql+asyncpg://{self.DB_USER}"
            "@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        ),
    },
    "MySQL": {
        "vars": {
            "DB_HOST": "localhost",
            "DB_PORT": 3306,
            "DB_USER": "root",
            "DB_NAME": None,
        },
        "uri": (
            "mysql+aiomysql://{self.DB_USER}"
            "@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        ),
    },
    "MongoDB": {
        "vars": {
            "DB_HOST": "localhost",
            "DB_PORT": 27017,
            "DB_USER": "local",
            "DB_PASSWORD": "local",
            "DB_NAME": None,
        },
        "uri": "mongodb://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}",
        "uri_no_auth": "mongodb://{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}",
    },
}

AUTH_CONFIGS = {
    "Bearer Token (Authorization Header)": True,
    "Cookie-based Authentication (HTTPOnly)": True,
}


def generate_db_block(
    db_choice: str,
    env_path: Path,
    env_example_path: Path,
    project_name: str,
) -> str:
    if db_choice not in DB_CONFIGS:
        return "\n# No database configured"

    cfg = DB_CONFIGS[db_choice]
    vars_with_values: dict[str, str | None] = dict(cfg["vars"])

    if db_choice in DB_USER_DEFAULT:
        vars_with_values["DB_USER"] = getpass.getuser()
        vars_with_values["DB_NAME"] = SQL_DEFAULT_DATABASE[db_choice]
    else:
        if "DB_NAME" in vars_with_values and not vars_with_values["DB_NAME"]:
            vars_with_values["DB_NAME"] = project_name

    add_env_variables(env_path, vars_with_values)
    add_env_variables(env_example_path, {k: None for k in vars_with_values})

    uri_expr = cfg.get("uri_no_auth") if db_choice == "MongoDB" else cfg["uri"]
    return f'''
    {"".join(f"{k}: {type(v).__name__ if v is not None else 'str'}\n    " for k, v in vars_with_values.items())}
    DATABASE_URL: Optional[str] = None

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"{uri_expr}"
    '''


def generate_auth_block(
    auth_choice: str, env_path: Path, env_example_path: Path
) -> str:
    if auth_choice in AUTH_CONFIGS:
        secret_key = secrets.token_hex(32)

        add_env_variables(env_path, {"SECRET_KEY": secret_key})
        add_env_variables(env_example_path, {"SECRET_KEY": None})

        return """
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    """
    return "\n# No authentication configured"


def generate_redis_block(env_path: Path, env_example_path: Path) -> str:
    redis_url = "redis://redis:6379/0"

    add_env_variables(env_path, {"REDIS_URL": redis_url})
    add_env_variables(env_example_path, {"REDIS_URL": None})

    return """
    REDIS_URL: str
"""


def generate_sentry_block(env_path: Path, env_example_path: Path) -> str:
    add_env_variables(env_path, {"SENTRY_DSN": ""})
    add_env_variables(env_example_path, {"SENTRY_DSN": None})

    return """
    SENTRY_DSN: Optional[str] = None
"""


def generate_logfire_block(env_path: Path, env_example_path: Path) -> str:
    add_env_variables(env_path, {"LOGFIRE_TOKEN": ""})
    add_env_variables(env_example_path, {"LOGFIRE_TOKEN": None})

    return """
    LOGFIRE_TOKEN: Optional[str] = None
"""


def generate_observability_block(
    choice: str, env_path: Path, env_example_path: Path
) -> str:
    if choice == "Sentry":
        return generate_sentry_block(env_path, env_example_path)
    elif choice == "Logfire":
        return generate_logfire_block(env_path, env_example_path)
    return "\n# No external observability configured"
