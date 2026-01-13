import functools

import questionary
from rich import print


def safe_prompt(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        answer = func(*args, **kwargs)
        if answer is None:
            raise KeyboardInterrupt
        return answer

    return wrapper


@safe_prompt
def choose(prompt: str, choices: list[str], default: str | None = None) -> str:
    return questionary.select(
        prompt,
        choices=choices,
        default=default or (choices[0] if choices else None),
    ).ask()


@safe_prompt
def confirm(prompt: str, default: bool = False) -> bool:
    return questionary.confirm(prompt, default=default).ask()


@safe_prompt
def input_text(prompt: str, default: str | None = None) -> str:
    return questionary.text(prompt, default=default or "").ask()
