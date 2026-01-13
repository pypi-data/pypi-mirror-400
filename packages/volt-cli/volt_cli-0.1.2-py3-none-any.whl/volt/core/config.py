import tomli
import tomli_w
from pathlib import Path
from pydantic import BaseModel


class VoltConfig(BaseModel):
    project_name: str
    stack: str
    features: dict[str, str | bool] = {}


def load_config(path: Path) -> VoltConfig | None:
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            data = tomli.load(f)
        return VoltConfig(**data)
    except Exception:
        return None


def save_config(config: VoltConfig, path: Path) -> None:
    with open(path, "wb") as f:
        tomli_w.dump(config.model_dump(), f)
