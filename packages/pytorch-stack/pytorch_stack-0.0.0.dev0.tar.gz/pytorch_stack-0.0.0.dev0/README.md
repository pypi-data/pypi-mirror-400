# torch-stack

**Install PyTorch ecosystem with automatic version compatibility via extras.**

## Motivation

PyTorch's ecosystem has complex version dependencies between `torch`, `torchvision`, `torchaudio`, and `torchtext`. Finding compatible versions is tedious and error-prone - this is the "PyTorch version hell."

**Before torch-stack:**

```bash
# Manual version hunting and compatibility checking
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0
```

**With torch-stack:**

```bash
# Just specify torch version, get compatible ecosystem automatically
pip install torch-stack[vision,audio]==2.1.0
```

torch-stack solves this by:

- 🎯 **Extras notation**: `torch-stack[vision]==2.1.0` installs compatible versions
- 📦 **No manual lookup**: Automatically resolves ecosystem compatibility
- 🔄 **Zero configuration**: Works out of the box with correct version mapping

## Installation

### Basic Installation

```bash
# Base torch only
pip install torch-stack==2.1.0

# With torchvision (gets compatible 0.16.0)
pip install torch-stack[vision]==2.1.0

# With audio and vision
pip install torch-stack[vision,audio]==2.1.0

# Everything
pip install torch-stack[all]==2.1.0
```

### CPU/CUDA Specific Installation

For specific hardware targets, use PyTorch's index URLs:

```bash
# CPU-only installation
pip install torch-stack[all]==2.1.0 --extra-index-url https://download.pytorch.org/whl/cpu

# CUDA 11.8
pip install torch-stack[all]==2.1.0 --extra-index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch-stack[all]==2.1.0 --extra-index-url https://download.pytorch.org/whl/cu121
```

### Available Index URLs

- **CPU**: `https://download.pytorch.org/whl/cpu`
- **CUDA 11.8**: `https://download.pytorch.org/whl/cu118`
- **CUDA 12.1**: `https://download.pytorch.org/whl/cu121`
- **ROCm 5.6**: `https://download.pytorch.org/whl/rocm5.6`

*Note: torch-stack resolves version compatibility; the index URL determines CPU/GPU variant.*

## Usage

### Simple Installation

Replace your manual PyTorch installs:

```bash
# Instead of researching compatible versions:
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0

# Just use:
pip install torch-stack[vision,audio]==2.1.0
```

### In requirements.txt

```txt
# Before: manual compatibility management
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0

# After: automatic compatibility
torch-stack[vision,audio]==2.1.0
```

### In pyproject.toml

```toml
[project]
dependencies = [
    "torch-stack[vision,audio]==2.1.0"
]
```

### Available Extras

- `vision` - Installs compatible `torchvision`
- `audio` - Installs compatible `torchaudio`
- `text` - Installs compatible `torchtext`

### Python API (for package maintainers)

```python
from torch_stack.resolver import VersionResolver

# Get compatible versions programmatically
torch_ver = "2.1.0"
vision_ver = VersionResolver.torchvision(torch_ver)  # "0.16.0"
audio_ver = VersionResolver.torchaudio(torch_ver)  # "2.1.0"
```

## Supported Versions

- PyTorch 1.8+ through latest
- Handles version exceptions and edge cases
- CPU and CUDA installation support

______________________________________________________________________

*No more PyTorch version hell* 🎉
