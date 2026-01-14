from __future__ import annotations

import pathlib
from typing import Annotated, Literal

import typer

from .detector import detect_arg_parser_type
from .extractors import ArgparseExtractor, PydanticSettingsExtractor
from .generator import generate_app_panel
from .types import ParameterExtractor

app = typer.Typer(help="Generate app-panel.json from Python argument parsing classes")


@app.command()
def generate(
    source: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to Python file containing argument parsing class",
        ),
    ],
    output: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path where App Panel JSON will be written",
        ),
    ] = pathlib.Path("/root/capsule/.codeocean/app-panel.json"),
    strategy: Annotated[
        Literal["overwrite", "preserve"],
        typer.Option(
            help="Strategy for merging with existing app-panel.json: 'overwrite' updates fields, 'preserve' keeps existing values",
        ),
    ] = "preserve",
    no_backup: Annotated[
        bool,
        typer.Option(
            help="Skip creating backup of existing app-panel.json",
        ),
    ] = False,
) -> None:
    parser_type = detect_arg_parser_type(str(source))

    extractor: ParameterExtractor  # set the expectation for type checkers
    if parser_type == "argparse":
        extractor = ArgparseExtractor()
    elif parser_type == "pydantic_settings":
        extractor = PydanticSettingsExtractor()
    else:
        raise NotImplementedError(
            f"Unsupported parser type discovered: {parser_type!r}"
        )

    parameters = extractor.extract_parameters(str(source))
    typer.echo(f"Found {len(parameters)} parameters in {source}")
    generate_app_panel(parameters, output, strategy=strategy, backup=not no_backup)
    typer.echo(f"✓ Generated app-panel.json at {output}")


if __name__ == "__main__":
    app()
