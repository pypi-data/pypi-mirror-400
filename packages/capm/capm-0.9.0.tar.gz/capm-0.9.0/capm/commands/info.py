import sys
from enum import Enum
from pathlib import Path

from capm.entities.PackageDefinition import PackageDefinition
from capm.utils.cli_utils import fail


class InfoFormat(str, Enum):
    text = "text"
    markdown = "markdown"


def info_command(package_repository: dict[str, PackageDefinition], fmt: InfoFormat, package: str | None):
    if package:
        if package not in package_repository:
            fail(f"Package '{package}' does not exist.")
            sys.exit(1)
        yml_file = Path(__file__).parent / 'package' / 'definitions' / f'{package}.yml'
        with open(yml_file, 'r') as file:
            content = file.read().strip()
        print(content)
    else:
        if fmt == InfoFormat.text:
            print_repository(package_repository)
        elif fmt == InfoFormat.markdown:
            print_repository_markdown(package_repository)


def print_repository(package_repository: dict[str, PackageDefinition]):
    print(f"{'PACKAGE':30s} {'VERSION':8s}")
    packages = sorted(package_repository.keys())
    for k in packages:
        v = package_repository[k]
        print(f"{k:30.30s} {str(v.version):8.8s}")


def print_repository_markdown(package_repository: dict[str, PackageDefinition]):
    print('| **Package** | **Version** | **Type** | **Technology** |')
    print('| --- | ---: | ---: | ---: |')
    packages = sorted(package_repository.keys())
    for k in packages:
        v = package_repository[k]
        technologies = [t.strip() for t in v.technology.split(',')] if v.technology else []
        if len(technologies) < 3:
            technology_cell = ', '.join(technologies)
        else:
            technology_cell = '3+'
        print(f"{k} | {str(v.version)} | {v.type} | {technology_cell} |")
