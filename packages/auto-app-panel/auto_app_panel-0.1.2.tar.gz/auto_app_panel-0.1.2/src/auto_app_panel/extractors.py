from __future__ import annotations

import argparse
import importlib.util
import inspect
import pathlib
import sys
import types
import typing
from typing import Any, Literal

import pydantic_core
import pydantic_settings

from .types import Parameter


def _load_module_from_file(file_path: str) -> types.ModuleType:
    module_path = pathlib.Path(file_path).resolve()
    if not module_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    spec = importlib.util.spec_from_file_location("_temp_module", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["_temp_module"] = module

    module_dir = str(module_path.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(module_dir)
    else:
        spec.loader.exec_module(module)

    return module


def _extract_type_from_annotation(annotation: Any) -> type | None:
    origin = typing.get_origin(annotation)
    if origin is not None:
        args = typing.get_args(annotation)
        if len(args) > 0:
            return args[0]  # type: ignore[no-any-return, unused-ignore]
    return annotation  # type: ignore[no-any-return, unused-ignore]


def _python_type_to_app_panel_type(
    type_class: Any,
) -> Literal["string", "integer", "number"]:
    type_mapping: dict[type, Literal["string", "integer", "number"]] = {
        float: "number",
        int: "integer",
        str: "string",
        bool: "integer",
    }
    return type_mapping.get(type_class, "string")


class PydanticSettingsExtractor:
    def extract_parameters(self, file_path: str) -> tuple[Parameter, ...]:
        module = _load_module_from_file(file_path)

        settings_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, pydantic_settings.BaseSettings)
                and obj is not pydantic_settings.BaseSettings
            ):
                settings_classes.append(obj)

        if len(settings_classes) == 0:
            raise ValueError(f"No BaseSettings class found in {file_path}")
        if len(settings_classes) > 1:
            raise ValueError(
                f"Multiple BaseSettings classes found in {file_path}: {[cls.__name__ for cls in settings_classes]}. "
                "Please specify which one to use."
            )

        settings_class = settings_classes[0]
        parameters = []

        for field_name, field_info in settings_class.model_fields.items():
            type_class = _extract_type_from_annotation(field_info.annotation)
            param_type = _python_type_to_app_panel_type(type_class)
            default_value = None

            if (
                field_info.default is not pydantic_core.PydanticUndefined
                and field_info.default is not None
            ):
                if isinstance(field_info.default, bool):
                    default_value = str(int(field_info.default))
                elif isinstance(field_info.default, (int, float)):
                    default_value = str(field_info.default)
                elif isinstance(field_info.default, str):
                    default_value = field_info.default
                else:
                    default_value = str(field_info.default)
            elif (
                hasattr(field_info, "default_factory")
                and field_info.default_factory is not None
            ):
                default_value = str(field_info.default_factory())  # type: ignore[call-arg]

            description = field_info.description

            parameters.append(
                Parameter(
                    name=field_name,
                    type=param_type,
                    default_value=default_value,
                    description=description,
                )
            )

        return tuple(parameters)


class ArgparseExtractor:
    def extract_parameters(self, file_path: str) -> tuple[Parameter, ...]:
        module = _load_module_from_file(file_path)

        parsers = []
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, argparse.ArgumentParser):
                parsers.append(obj)

        if len(parsers) == 0:
            raise ValueError(f"No ArgumentParser found in {file_path}")
        if len(parsers) > 1:
            raise ValueError(
                f"Multiple ArgumentParser instances found in {file_path}. "
                "Please specify which one to use."
            )

        parser = parsers[0]
        parameters = []

        for action in parser._actions:
            if action.dest == "help":
                continue

            option_strings = action.option_strings
            if not option_strings:
                continue

            name = option_strings[0].lstrip("-").replace("-", "_")

            if action.type is bool:
                raise ValueError(
                    f"Argument '{name}' uses type=bool, which will not work as expected. "
                    "argparse's bool() function returns True for all non-empty strings (including '0' and 'False'). "
                    "For boolean fields compatible with app panels (which use integer inputs), use type=int with True/False defaults instead."
                )

            if isinstance(action, argparse.BooleanOptionalAction) or action.nargs == 0:
                raise ValueError(
                    f"Argument '{name}' uses a flag-type action (BooleanOptionalAction, store_true, store_false, etc.) which is not compatible with app panels. "
                    "App panels always pass argument values as '--name value', but flag actions don't accept values. "
                    "For boolean fields, use type=int with default=0 or default=1 instead."
                )

            param_type = _python_type_to_app_panel_type(action.type)

            default_value = None
            if action.default is not None and action.default is not argparse.SUPPRESS:
                if isinstance(action.default, bool):
                    default_value = str(int(action.default))
                else:
                    default_value = str(action.default)

            description = action.help

            parameters.append(
                Parameter(
                    name=name,
                    type=param_type,
                    default_value=default_value,
                    description=description,
                )
            )

        return tuple(parameters)
