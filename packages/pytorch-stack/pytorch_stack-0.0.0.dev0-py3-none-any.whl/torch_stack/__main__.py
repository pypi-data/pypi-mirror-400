"""CLI for torch-stack version utilities."""

from torch_stack.debug import debug_info
from torch_stack.resolver import VersionResolver


def main() -> None:
    """Run the CLI for torch-stack version utilities."""
    from jsonargparse import auto_cli, set_parsing_settings

    set_parsing_settings(parse_optionals_as_positionals=True)
    auto_cli(
        {
            "update": {
                "pyproject_extras": VersionResolver.update_pyproject_extras,
                "package_version": VersionResolver.update_package_version,
            },
            "debug": debug_info,
        }
    )


if __name__ == "__main__":
    main()
