from dataclasses import dataclass


@dataclass
class PackageConfig:
    id: str
    version: str | None = None
    args: str | None = None
    extra_args: str | None = None
    workspace_mode: str | None = None
