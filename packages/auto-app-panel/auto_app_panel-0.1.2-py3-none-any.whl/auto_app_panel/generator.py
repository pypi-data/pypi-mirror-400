from __future__ import annotations

import datetime
import json
import pathlib
import random
import string
from collections.abc import Iterable
from typing import Literal

import pydantic

from .types import Parameter


class AppPanelParameter(pydantic.BaseModel):
    id: str
    name: str
    param_name: str
    description: str | None = None
    help_text: str | None = None
    type: str = "text"
    value_type: str
    default_value: str | None = None
    minimum: int | None = None
    maximum: int | None = None


class AppPanel(pydantic.BaseModel):
    version: int = 1
    named_parameters: bool = True
    parameters: tuple[AppPanelParameter, ...]


def _generate_random_id(length: int = 16) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def _parameter_to_app_panel(
    param: Parameter, existing_id: str | None = None
) -> AppPanelParameter:
    app_param = AppPanelParameter(
        id=existing_id or _generate_random_id(),
        name=param.name,
        param_name=param.name,
        description=param.description,
        help_text=param.description,
        value_type=param.type,
        default_value=param.default_value,
    )

    if param.type == "integer" and param.default_value in ["True", "False"]:
        app_param.minimum = 0
        app_param.maximum = 1
        if param.default_value in ["True", "False"]:
            app_param.default_value = "1" if param.default_value == "True" else "0"

    return app_param


def _merge_app_panels(
    parameters: Iterable[Parameter],
    existing: AppPanel | None,
    strategy: Literal["overwrite", "preserve"],
) -> AppPanel:
    if existing is None:
        return AppPanel(
            parameters=tuple(_parameter_to_app_panel(param) for param in parameters)
        )

    existing_by_name = {p.param_name: p for p in existing.parameters}

    merged_params = []

    for param in parameters:
        if param.name in existing_by_name:
            existing_param = existing_by_name[param.name]
            if strategy == "preserve":
                merged_param = _parameter_to_app_panel(param, existing_param.id)
                if existing_param.description and not merged_param.description:
                    merged_param.description = existing_param.description
                    merged_param.help_text = existing_param.help_text
                if existing_param.minimum is not None:
                    merged_param.minimum = existing_param.minimum
                if existing_param.maximum is not None:
                    merged_param.maximum = existing_param.maximum
                merged_params.append(merged_param)
            else:
                merged_param = _parameter_to_app_panel(param, existing_param.id)
                merged_params.append(merged_param)
        else:
            merged_params.append(_parameter_to_app_panel(param))

    return AppPanel(parameters=tuple(merged_params))


def generate_app_panel(
    parameters: Iterable[Parameter],
    output_path: str | pathlib.Path,
    strategy: Literal["overwrite", "preserve"] = "preserve",
    backup: bool = True,
) -> None:
    output_path = pathlib.Path(output_path)
    existing_app_panel = None

    if output_path.exists():
        with open(output_path) as f:
            existing_data = json.load(f)
            existing_app_panel = AppPanel(**existing_data)

        if backup:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = (
                output_path.parent
                / f"{output_path.stem}_{timestamp}{output_path.suffix}"
            )
            with open(backup_path, "w") as f:
                json.dump(existing_data, f, indent="\t")

    new_app_panel = _merge_app_panels(parameters, existing_app_panel, strategy)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(new_app_panel.model_dump(exclude_none=True), f, indent="\t")
