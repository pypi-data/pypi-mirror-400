"""Configuration-driven argument definitions for screenshot CLIs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "cli_v1.json"


class _MissingType:
    """Sentinel that marks argument defaults as unspecified."""


_Missing: Final = _MissingType()


@dataclass(frozen=True)
class CLIArgumentSpec:
    """Specification for a single CLI argument."""

    arg_id: str
    dest: str
    flags: tuple[str, ...]
    type: str
    default: Any = field(default_factory=lambda: _Missing)
    help: str = ""
    action: str | None = None
    choices: tuple[str, ...] | None = None
    required: bool = False
    metavar: str | None = None
    nargs: str | int | None = None
    const: Any | None = None
    parser_type: str = "standard"
    deprecated: bool = False
    added_in: str | None = None


@dataclass(frozen=True)
class CLIArgumentGroup:
    """Logical grouping of related arguments."""

    name: str
    description: str
    arguments: tuple[str, ...]


@dataclass(frozen=True)
class CLIServicePreset:
    """Pre-configured argument selections for common entrypoints."""

    name: str
    description: str
    include_groups: tuple[str, ...] = ()
    exclude_args: tuple[str, ...] = ()
    additional_args: tuple[str, ...] = ()


@dataclass(frozen=True)
class CLIConfigSchema:
    """Top-level configuration container."""

    version: str
    package: str
    arguments: dict[str, CLIArgumentSpec]
    argument_groups: dict[str, CLIArgumentGroup] = field(default_factory=dict)
    service_presets: dict[str, CLIServicePreset] = field(default_factory=dict)


def load_cli_config(config_path: Path | str | None = None) -> CLIConfigSchema:
    """Load CLI configuration from YAML or embedded defaults."""

    if config_path is None:
        target = _DEFAULT_CONFIG_PATH
    else:
        target = Path(config_path)
    if not target.exists():
        raise FileNotFoundError(f"CLI config not found: {target}")
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return _parse_config(data)


def apply_config_to_parser(
    parser: argparse.ArgumentParser,
    config: CLIConfigSchema,
    *,
    include_groups: Iterable[str] | None = None,
    exclude_args: Iterable[str] | None = None,
    preset: str | None = None,
) -> None:
    """Apply the configuration to an ``argparse.ArgumentParser`` instance."""

    from ._shared.cli.arguments import _parse_bool  # noqa: PLC0415 - avoid circular import

    if preset:
        if preset not in config.service_presets:
            raise ValueError(
                f"Unknown preset '{preset}'. Available presets: {sorted(config.service_presets)}"
            )
        preset_cfg = config.service_presets[preset]
        include_groups = preset_cfg.include_groups
        exclude_args = (*preset_cfg.exclude_args, *(exclude_args or ()))
        additional_args = preset_cfg.additional_args
    else:
        additional_args = ()

    included_args: set[str] = set(additional_args)
    if include_groups is None:
        included_args.update(config.arguments.keys())
    else:
        for group_name in include_groups:
            group = config.argument_groups.get(group_name)
            if group is None:
                raise ValueError(f"Unknown argument group '{group_name}'")
            included_args.update(group.arguments)

    if exclude_args:
        included_args -= set(exclude_args)

    for arg_id in included_args:
        if arg_id not in config.arguments:
            raise ValueError(f"Argument '{arg_id}' not defined in CLI config")
        spec = config.arguments[arg_id]
        kwargs: dict[str, Any] = {}
        if spec.help:
            kwargs["help"] = spec.help
        if spec.choices:
            kwargs["choices"] = list(spec.choices)
        if spec.required:
            kwargs["required"] = True
        if spec.metavar:
            kwargs["metavar"] = spec.metavar
        if spec.nargs is not None:
            kwargs["nargs"] = spec.nargs
        if spec.const is not None:
            kwargs["const"] = spec.const
        if spec.action:
            kwargs["action"] = spec.action
        if spec.default is not _Missing:
            kwargs["default"] = spec.default

        if spec.parser_type == "custom_bool":
            kwargs["type"] = _parse_bool
        else:
            type_callable = _resolve_type(spec.type)
            if type_callable is not None and spec.action not in {"store_true", "store_false"}:
                kwargs["type"] = type_callable

        parser.add_argument(*spec.flags, dest=spec.dest, **kwargs)


TypeConverter = Callable[[str], object]


def _resolve_type(type_name: str | None) -> TypeConverter | None:
    if type_name is None:
        return None
    converters: dict[str, TypeConverter] = {
        "int": int,
        "float": float,
        "str": str,
        "path": Path,
        "bool": bool,
    }
    return converters.get(type_name)


def _parse_config(data: dict[str, Any]) -> CLIConfigSchema:
    version = data.get("version")
    if not version:
        raise ValueError("Config missing 'version' field")
    metadata = data.get("metadata") or {}
    package = metadata.get("package", "unknown")

    arguments: dict[str, CLIArgumentSpec] = {}
    for arg_id, arg_data in (data.get("arguments") or {}).items():
        flags = tuple(arg_data["flags"])
        dest = arg_data.get("dest", _derive_dest(flags[0]))
        default = arg_data.get("default", _Missing)
        if default is None and "default" not in arg_data:
            default = _Missing
        arguments[arg_id] = CLIArgumentSpec(
            arg_id=arg_id,
            dest=dest,
            flags=flags,
            type=arg_data.get("type", "str"),
            default=default,
            help=arg_data.get("help", ""),
            action=arg_data.get("action"),
            choices=tuple(arg_data["choices"]) if arg_data.get("choices") else None,
            required=arg_data.get("required", False),
            metavar=arg_data.get("metavar"),
            nargs=arg_data.get("nargs"),
            const=arg_data.get("const"),
            parser_type=arg_data.get("parser_type", "standard"),
            deprecated=arg_data.get("deprecated", False),
            added_in=arg_data.get("added_in"),
        )

    argument_groups = {
        name: CLIArgumentGroup(
            name=name,
            description=group_data.get("description", ""),
            arguments=tuple(group_data.get("arguments", ())),
        )
        for name, group_data in (data.get("argument_groups") or {}).items()
    }

    service_presets = {
        name: CLIServicePreset(
            name=name,
            description=preset.get("description", ""),
            include_groups=tuple(preset.get("include_groups", ())),
            exclude_args=tuple(preset.get("exclude_args", ())),
            additional_args=tuple(preset.get("additional_args", ())),
        )
        for name, preset in (data.get("service_presets") or {}).items()
    }

    return CLIConfigSchema(
        version=version,
        package=package,
        arguments=arguments,
        argument_groups=argument_groups,
        service_presets=service_presets,
    )


def _derive_dest(flag: str) -> str:
    return flag.lstrip("-").replace("-", "_")
