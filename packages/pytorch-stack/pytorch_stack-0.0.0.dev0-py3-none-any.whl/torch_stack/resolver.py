"""Resolve versions across PyTorch ecosystem based on `torch` version."""

import re
from typing import Optional


class VersionResolver:
    """Resolve versions across PyTorch ecosystem based on `torch` version."""

    _torchaudio_exceptions = {
        "2.0.1": "2.0.2",
        "2.0.0": "2.0.1",
        "1.8.2": "0.9.1",
    }

    _torchtext_exceptions = {
        "2.0.1": "0.15.2",
        "2.0.0": "0.15.1",
        "1.8.2": "0.9.1",
    }

    _torchvision_exceptions = {
        "2.0.1": "0.15.2",
        "2.0.0": "0.15.1",
        "1.10.2": "0.11.3",
        "1.10.1": "0.11.2",
        "1.10.0": "0.11.1",
        "1.8.2": "0.9.1",
    }

    @staticmethod
    def get_torch_version(path: str = "pyproject.toml") -> str:
        """Parse torch version from pyproject.toml dependencies."""
        import tomlkit

        with open(path, encoding="utf-8") as fp:
            config = tomlkit.load(fp)

        # PEP 621: [project] dependencies = ["torch>=2.0.0", ...]
        dependencies = config.get("project", {}).get("dependencies", [])
        for dep in dependencies:
            if re.match(r"^torch(\s|$|[<>=!~])", dep):
                match = re.search(r"([\d\.]+)", dep)
                if match:
                    return match.group(1)

        raise ValueError(
            f"Could not find a 'torch' dependency with a version specifier in [project.dependencies] of {path}"
        )

    @staticmethod
    def _parse_version(ver: str) -> tuple[int, int, int]:
        """Parse version string into major, minor, bugfix integers."""
        ver_major, ver_minor, ver_bugfix = map(int, ver.split("."))
        if ver_major < 1:
            raise ValueError(f"Unsupported version: {ver} (major={ver_major})")
        return ver_major, ver_minor, ver_bugfix

    @staticmethod
    def torchaudio(torch_version: str) -> str:
        """Determine the torchaudio version based on the torch version.

        >>> VersionResolver.torchaudio("1.9.0")
        '0.9.0'
        >>> VersionResolver.torchaudio("2.4.1")
        '2.4.1'
        >>> VersionResolver.torchaudio("1.8.2")
        '0.9.1'

        """
        if torch_version in VersionResolver._torchaudio_exceptions:
            return VersionResolver._torchaudio_exceptions[torch_version]
        ver_major, ver_minor, ver_bugfix = VersionResolver._parse_version(torch_version)
        ver_array = [ver_major, ver_minor, ver_bugfix]
        if ver_major == 1:
            ver_array[0] = 0

        return ".".join(map(str, ver_array))

    @staticmethod
    def torchtext(torch_version: str) -> str:
        """Determine the torchtext version based on the torch version.

        >>> VersionResolver.torchtext("1.9.0")
        '0.10.0'
        >>> VersionResolver.torchtext("2.4.1")
        '0.18.0'
        >>> VersionResolver.torchtext("1.8.2")
        '0.9.1'

        """
        if torch_version in VersionResolver._torchtext_exceptions:
            return VersionResolver._torchtext_exceptions[torch_version]
        ver_major, ver_minor, ver_bugfix = VersionResolver._parse_version(torch_version)
        ver_array = [0, 0, 0]
        if ver_major == 1:
            ver_array[1] = ver_minor + 1
            ver_array[2] = ver_bugfix
        elif ver_major == 2:
            if ver_minor >= 3:
                # discontinued development of torchtext for 2.3+
                ver_array[1] = 18
            else:
                ver_array[1] = ver_minor + 15
                ver_array[2] = ver_bugfix
        return ".".join(map(str, ver_array))

    @staticmethod
    def torchvision(torch_version: str) -> str:
        """Determine the torchvision version based on the torch version.

        >>> VersionResolver.torchvision("1.9.0")
        '0.10.0'
        >>> VersionResolver.torchvision("2.4.1")
        '0.19.1'
        >>> VersionResolver.torchvision("2.0.1")
        '0.15.2'

        """
        if torch_version in VersionResolver._torchvision_exceptions:
            return VersionResolver._torchvision_exceptions[torch_version]
        ver_major, ver_minor, ver_bugfix = VersionResolver._parse_version(torch_version)
        ver_array = [0, 0, 0]
        if ver_major == 1:
            ver_array[1] = ver_minor + 1
        elif ver_major == 2:
            ver_array[1] = ver_minor + 15
        ver_array[2] = ver_bugfix
        return ".".join(map(str, ver_array))

    @staticmethod
    def update_pyproject_extras(path: str = "pyproject.toml", torch_version: Optional[str] = None) -> None:
        """Update pyproject.toml extras with compatible torch versions."""
        import tomlkit

        torch_ver = torch_version or VersionResolver.get_torch_version(path)

        targets = {
            "torchvision": VersionResolver.torchvision(torch_ver),
            "torchaudio": VersionResolver.torchaudio(torch_ver),
            "torchtext": VersionResolver.torchtext(torch_ver),
        }

        with open(path, encoding="utf-8") as fp:
            config = tomlkit.load(fp)

        extras = config.get("project", {}).get("optional-dependencies", {})
        # Compile regex patterns to ensure we only match the exact package name
        # at the start of the dependency string, followed by a version specifier,
        # whitespace, or end-of-string. This avoids matching similarly-prefixed
        # but distinct packages (e.g. "torchvision-nightly").
        patterns = {pkg: re.compile(rf"^{re.escape(pkg)}(?=([<>=!~ ]|$))") for pkg in targets}
        for group in extras.values():
            for i, dep in enumerate(group):
                for pkg, ver in targets.items():
                    if patterns[pkg].match(dep):
                        group[i] = f"{pkg}=={ver}"

        with open(path, "w", encoding="utf-8") as fp:
            tomlkit.dump(config, fp)

    @staticmethod
    def update_package_version(
        init_path: str = "torch_stack/__init__.py",
        proj_path: str = "pyproject.toml",
        torch_version: Optional[str] = None,
    ) -> None:
        """Update package __init__.py version to match torch version."""
        torch_ver = torch_version or VersionResolver.get_torch_version(proj_path)

        with open(init_path, encoding="utf-8") as fp:
            content = fp.read()

        content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{torch_ver}"', content)

        with open(init_path, "w", encoding="utf-8") as fp:
            fp.write(content)
