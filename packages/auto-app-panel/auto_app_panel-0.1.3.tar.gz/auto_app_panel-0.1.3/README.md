# auto-app-panel

Automatically generate a Code Ocean App Panel from an argument parser defined in code.

[![PyPI](https://img.shields.io/pypi/v/auto-app-panel.svg?label=PyPI&color=blue)](https://pypi.org/project/auto-app-panel/)
[![Python version](https://img.shields.io/pypi/pyversions/auto-app-panel)](https://pypi.org/project/auto-app-panel/)

[![Coverage](https://img.shields.io/badge/coverage-75%25-yellow?logo=codecov)](https://app.codecov.io/github/AllenNeuralDynamics/auto-app-panel)
[![mypy](https://img.shields.io/badge/mypy-strict-blue)](https://mypy-lang.org/)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/AllenNeuralDynamics/auto-app-panel/publish.yml?label=CI/CD&logo=github)](https://github.com/AllenNeuralDynamics/auto-app-panel/actions/workflows/publish.yaml)
[![GitHub issues](https://img.shields.io/github/issues/AllenNeuralDynamics/auto-app-panel?logo=github)](https://github.com/AllenNeuralDynamics/auto-app-panel/issues)


## Status
- Initial release supporting extraction from `pydantic_settings.BaseSettings` and `argparse.ArgumentParser` classes at top-level of a specified Python file.

### TODO

- [ ] support classes defined inside functions or conditionals
- [ ] preserve groups and other formatting in existing app panel
- [ ] create explicit string/number/integer Parameter classes to support additional constraints (e.g. min/max length for strings, regex validators etc.) - see codeocean sdk for full schema


## Usage

### Typical Workflow

1. Develop your code with a class for parsing capsule parameters **at the top-level of the file** (not inside a function or conditional)
2. Run the tool in a Code Ocean cloud workstation terminal, pointing to the file containing the parameter-parsing class:
   ```bash
   pip install auto-app-panel
   auto-app-panel /root/capsule/code/run.py
   ```
   This generates `/root/capsule/.codeocean/app-panel.json`, which configures the capsule's App Panel GUI.
3. Re-run the tool when you add/modify parameters (use `--strategy preserve` to keep any edits made in the App Panel GUI/in an existing `app-panel.json`)
4. Verify that the App Panel is visible and has all expected fields when you exit the cloud workstation

### Command Line Interface
```bash
auto-app-panel SOURCE [OUTPUT] [OPTIONS]
```

**Arguments:**
- `SOURCE` - Path to Python file containing argument parsing class (required)
- `OUTPUT` - Output path for app-panel.json (default: `/root/capsule/.codeocean/app-panel.json`)

**Options:**
- `--strategy [overwrite|preserve]` - Merge strategy (default: `preserve`)
  - `overwrite`: Updates parameter values from code, preserves existing descriptions
  - `preserve`: Keeps all existing values, only adds new parameters
- `--no-backup` - Skip creating timestamped backup of existing file

### Example files

**Input Python file (`run.py`):**

```python
import time

import pydantic
import pydantic_settings

class Params(pydantic_settings.BaseSettings):
    max_workers: int | None = pydantic.Field(6, description="Number of parallel workers. Leave empty or set to 0 to use max available.")
    threshold: float = 0.5    
    output_dir: str = pydantic.Field("/root/capsule/results/dryrun", description="Output path for results, posix format.")
    save_intermediate: bool = False
    
    # other attributes that are not parsed from command-line inputs (e.g. PrivateAttr or @computed_field) are ignored
    _start_time: float = pydantic.PrivateAttr(time.time())

    # Ensure class parses arguments from command line (and set priority of other sources):
    @classmethod  
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        *args,
        **kwargs,
    ):
        # instantiating the class will use arguments passed directly, or provided via the command line/app panel
        # - the order of the sources below defines the priority (highest to lowest):
        # - for each field in the class, the first source that contains a value will be used
        return (
            init_settings,
            pydantic_settings.sources.JsonConfigSettingsSource(settings_cls, json_file='parameters.json'),
            pydantic_settings.CliSettingsSource(settings_cls, cli_parse_args=True),
        )
```

**Generate file at standard path:**
```bash
auto-app-panel /root/capsule/code/run.py
```
**Generated `app-panel.json`:**

```json
{
    "version": 1,
    "named_parameters": true,
    "parameters": [
        {
            "id": "a1b2c3d4e5f6g7h8",
            "name": "max_workers",
            "param_name": "max_workers",
            "description": "Number of parallel workers",
            "help_text": "Number of parallel workers",
            "type": "text",
            "value_type": "integer",
            "default_value": "6"
        },
        {
            "id": "i9j0k1l2m3n4o5p6",
            "name": "threshold",
            "param_name": "threshold",
            "type": "text",
            "value_type": "number",
            "default_value": "0.5"
        },
        {
            "id": "q7r8s9t0u1v2w3x4",
            "name": "output_dir",
            "param_name": "output_dir",
            "description": "Output path for results, posix format.",
            "help_text": "Output path for results, posix format.",
            "type": "text",
            "value_type": "string",
            "default_value": "/root/capsule/results/dryrun"
        },
        {
            "id": "y5z6a7b8c9d0e1f2",
            "name": "save_intermediate",
            "param_name": "save_intermediate",
            "type": "text",
            "value_type": "integer",
            "default_value": "0",
            "minimum": 0,
            "maximum": 1
        }
    ]
}
```
## Development
Clone the repository and setup with `uv sync`.

Run tests with `uv run task test`.

Pushing to `main` or creating a PR to `main` will trigger CI/CD. Updates on `main` that pass all tests
will trigger a minor version bump, then be published on PyPI.