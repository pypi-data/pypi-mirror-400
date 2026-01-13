"""Debug utilities for torch_stack."""


def debug_info() -> None:
    """Print a compact debug summary useful for bug reports.

    This collects Python, platform and tries to import torch to show
    torch version and CUDA availability/version. It also attempts to record
    torchvision/torchaudio/torchtext versions and the CUDA device name when
    available. The final output is a pprint'd dictionary for easy copy/paste.
    """
    import importlib
    import platform
    import sys
    from pprint import pprint

    # Basic system
    info = {"python": sys.version.replace("\n", " "), "platform": platform.platform()}

    # Torch and CUDA info: import separately and handle errors close to the failing call
    try:
        import torch
    except (ImportError, ModuleNotFoundError) as exc:
        info["torch_import_error"] = repr(exc)
    else:
        # torch version
        try:
            info["torch"] = getattr(torch, "__version__", "<unknown>")
        except AttributeError:
            info["torch"] = None  # type: ignore[assignment]

        # cuda availability, TODO, add mps/rocm/tpu checks?
        try:
            info["cuda_available"] = bool(torch.cuda.is_available())  # type: ignore[assignment]
        except (RuntimeError, OSError, AssertionError):
            info["cuda_available"] = False  # type: ignore[assignment]

        # cuda version
        try:
            info["cuda_version"] = getattr(torch.version, "cuda", None)  # type: ignore[assignment]
        except AttributeError:
            info["cuda_version"] = None  # type: ignore[assignment]

        # cuda device name (may fail if driver inaccessible)
        if info["cuda_available"]:
            try:
                info["cuda_device_name"] = torch.cuda.get_device_name(0)
            except (RuntimeError, OSError, AssertionError):
                info["cuda_device_name"] = None  # type: ignore[assignment]

    # Optional ecosystem packages
    for pkg in ("torchvision", "torchaudio", "torchtext"):
        try:
            mod = importlib.import_module(pkg)
            info[pkg] = getattr(mod, "__version__", "<unknown>")
        except (ImportError, ModuleNotFoundError):
            info[pkg] = None  # type: ignore[assignment]
        except OSError as err:
            info[pkg] = err  # type: ignore[assignment]

    # Pretty-print the collected info at the end for easy copy/paste into bug reports
    pprint(info)
