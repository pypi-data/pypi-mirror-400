from dataclasses import dataclass


@dataclass
class PackageDefinition:
    image: str
    version: str
    args: str
    type: str
    install_command: str | None = None
    entrypoint: str | None = None
    workspace_mode: str = 'rw'
    repository: str | None = None
    about: str | None = None
    website: str | None = None
    technology: str | None = None
