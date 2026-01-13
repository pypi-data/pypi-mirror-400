import re
from pathlib import Path


def replace_pattern_in_file(file_path: Path, pattern: str, replacement: str, flags=re.DOTALL):
    content = file_path.read_text()
    new_content = re.sub(pattern, replacement, content, flags=flags)
    file_path.write_text(new_content)
    return new_content


def insert_before_pattern(file_path: Path, pattern: str, text_to_insert: str, flags=re.DOTALL):
    content = file_path.read_text()
    new_content = re.sub(pattern, text_to_insert + r"\g<0>", content, flags=flags)
    file_path.write_text(new_content)
    return new_content


def insert_after_pattern(file_path: Path, pattern: str, text_to_insert: str, flags=re.DOTALL):
    content = file_path.read_text()
    new_content = re.sub(pattern, r"\g<0>" + text_to_insert, content, flags=flags)
    file_path.write_text(new_content)
    return new_content
