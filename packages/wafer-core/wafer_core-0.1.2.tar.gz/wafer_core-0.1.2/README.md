# wafer-core

Core utilities and environments for Wafer GPU kernel optimization.

## Features

- **CUDA Compilation Tools**: Compile CUDA files to PTX/SASS, detect GPU architecture
- **Tool Finding**: Locate CUDA toolkit executables (nvcc, nvdisasm)
- **Telemetry**: Decorator-based telemetry system with hooks
- **Environments**: GPU kernel optimization environments
- **Remote Execution**: SSH and Modal-based remote GPU execution
- **Sessions**: Agent session management
- **Logging**: Structured logging with color and JSON formatters

## Installation

```bash
pip install wafer-core
```

All dependencies, including `rollouts`, are automatically installed.

## Quick Start

```python
from wafer_core import compile_cuda, detect_arch, find_nvcc

# Detect GPU architecture
arch_info = detect_arch()
print(f"Detected architecture: {arch_info['arch']}")

# Compile CUDA file
result = compile_cuda("kernel.cu", arch="sm_90")
print(f"PTX: {result.ptx}")
print(f"SASS: {result.sass}")

# Find nvcc
nvcc_path = find_nvcc()
if nvcc_path:
    print(f"Found nvcc at: {nvcc_path}")
```

## Documentation

See the [Wafer documentation](https://github.com/wafer-ai/wafer) for more information.

## License

MIT License

