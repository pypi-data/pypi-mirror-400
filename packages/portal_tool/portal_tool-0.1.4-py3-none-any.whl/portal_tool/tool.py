import logging
import pathlib
from typing import Annotated
from importlib.metadata import version as meta_version

import typer

from portal_tool.framework.framework_manager import FrameworkManager
from portal_tool.installer.repo.repo_maker import RepoMaker
from portal_tool.installer.installer import Installer
from portal_tool.models import Configuration
from portal_tool.registry.registry_update import RegistryManager

global_working_directory = pathlib.Path.cwd()
configuration: Configuration
framework_manager: FrameworkManager


def version_callback(value: bool):
    if value:
        typer.echo(f"Portal Tool version: {meta_version('portal_tool')}")
        raise typer.Exit()


def registry_start(
    working_dir: Annotated[
        pathlib.Path,
        typer.Option(
            "-d", "--working-dir", help="The working directory of the project"
        ),
    ] = pathlib.Path.cwd(),
):
    global global_working_directory
    global_working_directory = working_dir


registry = typer.Typer(callback=registry_start)


@registry.command()
def update() -> None:
    manager = RegistryManager(global_working_directory, framework_manager)
    manager.update()


@registry.command()
def update_versions() -> None:
    manager = RegistryManager(global_working_directory, framework_manager)
    manager.update_version()


app = typer.Typer()
app.add_typer(registry, name="registry", help="Commands for managing the registry")


@app.command()
def install(
    dependencies_only: Annotated[
        bool,
        typer.Option(
            "--only-dependencies",
            help="Only installs the dependencies, skips all other stages",
        ),
    ] = False,
    auto_yes: Annotated[
        bool,
        typer.Option(
            "-y",
            "--yes",
            help="Automatically answer yes to all questions.",
        ),
    ] = False,
) -> None:
    installer = Installer(
        configuration.registry_url_template.format(
            repo=configuration.vcpkg_registry_repo
        ),
        auto_yes,
    )

    if dependencies_only:
        installer.install(False, True)
    else:
        installer.install(True, True)


@app.command()
def init(
    directory: Annotated[
        pathlib.Path,
        typer.Option("-d", "--dir", help="The directory to initialize the project in"),
    ] = pathlib.Path.cwd(),
) -> None:
    RepoMaker(directory, framework_manager)


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
    framework_repo: Annotated[
        str,
        typer.Option("--framework", help="The repo of portal-framework"),
    ] = "JonatanNevo/portal-framework",
    working_branch: Annotated[
        str,
        typer.Option("--branch", help="The branch of the framework repo to work on"),
    ] = "main",
    registry_repo: Annotated[
        str, typer.Option("--registry", help="The repo of the vcpkg registry")
    ] = "JonatanNevo/portal-vcpkg-registry",
):
    global configuration
    global framework_manager
    logging.basicConfig(level=logging.INFO)

    configuration = Configuration(
        repo=framework_repo,
        repo_branch=working_branch,
        vcpkg_registry_repo=registry_repo,
    )

    framework_manager = FrameworkManager(configuration)


if __name__ == "__main__":
    app()
