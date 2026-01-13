import yaml

FASTAPI_DOCKERFILE = """FROM ghcr.io/astral-sh/uv:python{python_version}-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:{python_version}-slim-bookworm

COPY --from=builder --chown=app:app /app /app
WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "app.main:app"]
"""


def generate_docker_compose_string(
    db_choice: str,
    redis_enabled: bool = False,
) -> str:
    from volt.stacks.fastapi.docker_config import DOCKER_CONFIGS

    services = {
        "app": {
            "build": ".",
            "ports": ["8000:8000"],
            "env_file": [".env"],
        }
    }

    if db_choice not in {"SQLite", "None"}:
        services["app"]["depends_on"] = {"db": {"condition": "service_healthy"}}

    if db_choice not in {"SQLite", "None"}:
        services["db"] = yaml.safe_load(DOCKER_CONFIGS[db_choice])

        if db_choice == "MongoDB":
            services["app"].setdefault("environment", {})
            services["app"]["environment"]["DB_HOST"] = "db"

    if redis_enabled:
        services["redis"] = {
            "image": "redis:latest",
            "healthcheck": {
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "5s",
                "timeout": "5s",
                "retries": 5,
            },
        }

        services["app"].setdefault("depends_on", {})
        services["app"]["depends_on"]["redis"] = {"condition": "service_healthy"}

    compose = {"services": services}

    return yaml.safe_dump(
        compose,
        sort_keys=False,
        default_flow_style=False,
    )
