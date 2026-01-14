from __future__ import annotations

import ast
import pathlib
from typing import Literal


def detect_arg_parser_type(file_path: str) -> Literal["pydantic_settings", "argparse"]:
    source_code = pathlib.Path(file_path).read_text()
    tree = ast.parse(source_code)

    has_basesettings = False
    has_argumentparser = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    if base.id == "BaseSettings":
                        has_basesettings = True
                elif isinstance(base, ast.Attribute):
                    if base.attr == "BaseSettings":
                        has_basesettings = True

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "ArgumentParser":
                    has_argumentparser = True
            elif isinstance(node.func, ast.Name):
                if node.func.id == "ArgumentParser":
                    has_argumentparser = True

    if has_basesettings:
        return "pydantic_settings"
    if has_argumentparser:
        return "argparse"

    raise ValueError(
        f"No supported argument parsing found in {file_path}. "
        "Expected pydantic.BaseSettings or argparse.ArgumentParser"
    )
