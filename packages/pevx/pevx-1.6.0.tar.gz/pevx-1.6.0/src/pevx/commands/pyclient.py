import os
import subprocess
import tomllib
from pathlib import Path

import click


def _get_project_info(pyproject_path: Path) -> dict:
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    project = data["project"]
    name = project["name"]
    return {
        "version": project["version"],
        "project_name": name,
        "package_name": name.replace("-", "_"),
    }


def _write_pyclient_yml(pyclient_yml: Path, info: dict) -> None:
    content = f"""package_version_override: {info["version"]}
project_name_override: {info["project_name"]}
package_name_override: {info["package_name"]}
docstrings_on_attributes: true
literal_enums: false
generate_all_tags: false
"""
    pyclient_yml.write_text(content)


@click.command("pyclient")
@click.option(
    "--pyproject",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default="pyproject.toml",
    help="Path to pyproject.toml",
)
@click.option(
    "--app-path",
    default="app.main:app",
    help="Python path to FastAPI app (e.g., app.main:app)",
)
def pyclient(pyproject: Path, app_path: str):
    """Generate Python client from FastAPI OpenAPI spec."""
    pyclient_yml = Path("pyclient.yml")
    openapi_json = Path("openapi.json")

    info = _get_project_info(pyproject)
    _write_pyclient_yml(pyclient_yml, info)
    click.echo(f"pyclient.yml ready with version {info['version']}")

    module_path, app_name = app_path.split(":")
    export_code = f"""
import json
from {module_path} import {app_name}
openapi = {app_name}.openapi()
with open('openapi.json', 'w') as f:
    json.dump(openapi, f, indent=2)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    subprocess.run(["uv", "run", "python", "-c", export_code], check=True, env=env)
    click.echo("Exported openapi.json")

    subprocess.run(
        [
            "openapi-python-client",
            "generate",
            "--path",
            "openapi.json",
            "--config",
            str(pyclient_yml),
            "--overwrite",
        ],
        check=True,
    )
    click.echo("Generated Python client")

    openapi_json.unlink()
    pyclient_yml.unlink()
    click.echo("Cleaned up temporary files")
