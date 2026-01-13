import os
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
import yaml
from typer import Context
from typer.core import TyperGroup

import capm.version
from capm.commands.info import info_command, InfoFormat
from capm.config import load_config_from_file, save_config_to_file
from capm.entities.PackageConfig import PackageConfig
from capm.entities.PackageDefinition import PackageDefinition
from capm.package.package import run_package, load_packages
from capm.utils.cli_utils import fail, succeed, console, read_input
from capm.utils.utils import data_class_to_dict

CONFIG_FILE = Path('.capm.yml')


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        return list(self.commands)


cli = typer.Typer(cls=OrderCommands, no_args_is_help=True, add_completion=False)
package_repository: dict[str, PackageDefinition] = {}


@cli.command(help="Add a package")
def add(package: Annotated[str, typer.Argument(help="Package name")]):
    if package not in package_repository:
        fail(f"Package '{package}' does not exist.")
        sys.exit(1)
    config = load_config_from_file(CONFIG_FILE)
    for p in config.packages:
        if p.id == package:
            fail(f"Package '{package}' is already added.")
            sys.exit(1)
    config.packages.append(PackageConfig(package))
    save_config_to_file(config, CONFIG_FILE)
    succeed(f'Package \'{package}\' added successfully.')


@cli.command(help="Run all configured package")
def check(show_output: Annotated[bool | None, typer.Option(help="Show output of package", show_default=False)] = None):
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} does not exist.")
        sys.exit(1)
    config = load_config_from_file(CONFIG_FILE)
    for package_config in config.packages:
        if package_config.id not in package_repository:
            fail(f"Package '{package_config.id}' does not exist.")
            sys.exit(1)
        package_definition = package_repository[package_config.id]
        exit_code = run_package(package_definition, package_config,
                                show_output if show_output is not None else False)
        if exit_code != 0:
            sys.exit(exit_code)


@cli.command(help="Create new package")
def create():
    image = read_input('Base image for package',
                       ['docker.io/library/python:3.11-slim', 'docker.io/library/node:22-alpine',
                        'docker.io/library/alpine:3.22.1', 'demisto/powershell:7.5.0.3759715',
                        'docker.io/library/ubuntu:24.04'])
    version = read_input('Version of package')
    install_command = read_input('Install command (optional)')
    entrypoint = read_input('Entrypoint (optional)')
    args = read_input('Arguments', default='')
    repository = read_input('Repository (optional)')
    about = read_input('About (optional)')
    website = read_input('Website (optional)')
    technology = read_input('Technology (optional)')
    package_type = read_input('Type', ['linter', 'formatter', 'analyzer', 'duplication', 'complexity', 'other'])
    package_definition = PackageDefinition(image=image, version=version, args=args, type=package_type,
                                           install_command=install_command,
                                           entrypoint=entrypoint, repository=repository, about=about, website=website,
                                           technology=technology)
    print(yaml.dump(data_class_to_dict(package_definition)))
    package_id = read_input('Package ID')
    if package_id:
        with open(f'{package_id}.yml', 'w') as file:
            yaml.dump(data_class_to_dict(package_definition), file)


@cli.command(help="Show information about package")
def info(package: Annotated[str | None, typer.Argument(help="Package name", show_default=False)] = None,
         fmt: Annotated[
             InfoFormat, typer.Option("--format", help="Output format")
         ] = InfoFormat.text
         ):
    info_command(package_repository, fmt, package)


@cli.command(name="list", help="List package")
def list_packages():
    config = load_config_from_file(CONFIG_FILE)
    if not config.packages:
        print("No package found.")
        return
    for package in config.packages:
        print(f"{package.id}")


@cli.command(help="Remove a package")
def remove(package: Annotated[str, typer.Argument(help="Package name")]):
    config = load_config_from_file(CONFIG_FILE)
    config.packages = [p for p in config.packages if p.id != package]
    save_config_to_file(config, CONFIG_FILE)
    succeed(f'Package \'{package}\' removed successfully.')


@cli.command(help='Run single package')
def run(_: Annotated[str, typer.Argument(metavar='PACKAGE', help="Package name")],
        __: Annotated[str, typer.Argument(metavar='ARGS', help="Arguments for the package")]):
    pass


def _version_callback(show: bool):
    if show:
        global package_repository
        package_repository = load_packages()
        console.print(f"CAPM v. {capm.version.version} [{len(package_repository)} package definitions]")
        raise typer.Exit()


@cli.callback()
def cli_callback(
        version: Annotated[
            Optional[bool],
            typer.Option(
                "--version", "-V", help="Show version", callback=_version_callback
            ),
        ] = None,
):
    """CAPM: Code Analysis Package Manager"""
    if version:
        raise typer.Exit()


def main():
    global package_repository
    package_repository = load_packages()
    if len(sys.argv) > 1 and sys.argv[1] == 'run' and len(sys.argv) >= 3:
        package = sys.argv[2]
        if package not in package_repository:
            fail(f"Package '{package}' does not exist.")
            sys.exit(1)
        package_definition = package_repository[package]
        args = ' '.join(sys.argv[3:])
        exit_code = run_package(package_definition, PackageConfig(package, args=args), True)
        if exit_code != 0:
            sys.exit(exit_code)
    else:
        cli()


if __name__ == "__main__":
    main()
