"""CUDA file parser for extracting structure and dependencies."""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class KernelFunction:
    name: str
    signature: str
    start_line: int
    end_line: int
    is_device: bool = False  # __device__ function
    is_global: bool = False  # __global__ kernel


@dataclass
class EvolveRegion:
    start_line: int
    end_line: int
    content: str


@dataclass
class CUDAFileInfo:
    path: Path
    includes: list[str] = field(default_factory=list)
    kernels: list[KernelFunction] = field(default_factory=list)
    device_functions: list[KernelFunction] = field(default_factory=list)
    evolve_regions: list[EvolveRegion] = field(default_factory=list)
    line_count: int = 0

    @property
    def has_evolve_markers(self) -> bool:
        return len(self.evolve_regions) > 0

    @property
    def all_functions(self) -> list[KernelFunction]:
        return self.kernels + self.device_functions


# Regex patterns
INCLUDE_PATTERN = re.compile(r'^\s*#include\s*[<"]([^>"]+)[>"]', re.MULTILINE)
KERNEL_PATTERN = re.compile(r"__global__\s+\w+\s+(\w+)\s*\([^)]*\)", re.MULTILINE)
DEVICE_PATTERN = re.compile(r"__device__\s+\w+\s+(\w+)\s*\([^)]*\)", re.MULTILINE)
EVOLVE_START_PATTERN = re.compile(r"//\s*EVOLVE_START", re.IGNORECASE)
EVOLVE_END_PATTERN = re.compile(r"//\s*EVOLVE_END", re.IGNORECASE)


def find_includes(content: str) -> list[str]:
    """Extract all #include statements from CUDA code."""
    return INCLUDE_PATTERN.findall(content)


def find_evolve_markers(content: str) -> list[EvolveRegion]:
    """Find EVOLVE_START/EVOLVE_END marker pairs."""
    lines = content.split("\n")
    regions = []
    start_line = None

    for i, line in enumerate(lines, 1):
        if EVOLVE_START_PATTERN.search(line):
            start_line = i
        elif EVOLVE_END_PATTERN.search(line) and start_line is not None:
            region_content = "\n".join(lines[start_line : i - 1])
            regions.append(
                EvolveRegion(start_line=start_line, end_line=i, content=region_content)
            )
            start_line = None

    return regions


def find_kernel_functions(content: str) -> list[KernelFunction]:
    """Find __global__ kernel functions."""
    kernels = []
    lines = content.split("\n")

    for match in KERNEL_PATTERN.finditer(content):
        name = match.group(1)
        sig_start = match.start()

        # Find line number
        line_num = content[:sig_start].count("\n") + 1

        # Find the end of the function (matching braces)
        end_line = find_function_end(lines, line_num - 1)

        kernels.append(
            KernelFunction(
                name=name,
                signature=match.group(0),
                start_line=line_num,
                end_line=end_line,
                is_global=True,
            )
        )

    return kernels


def find_device_functions(content: str) -> list[KernelFunction]:
    """Find __device__ functions."""
    functions = []
    lines = content.split("\n")

    for match in DEVICE_PATTERN.finditer(content):
        name = match.group(1)
        sig_start = match.start()
        line_num = content[:sig_start].count("\n") + 1
        end_line = find_function_end(lines, line_num - 1)

        functions.append(
            KernelFunction(
                name=name,
                signature=match.group(0),
                start_line=line_num,
                end_line=end_line,
                is_device=True,
            )
        )

    return functions


def find_function_end(lines: list[str], start_idx: int) -> int:
    """Find the end line of a function by matching braces."""
    brace_count = 0
    started = False

    for i in range(start_idx, len(lines)):
        line = lines[i]
        for char in line:
            if char == "{":
                brace_count += 1
                started = True
            elif char == "}":
                brace_count -= 1
                if started and brace_count == 0:
                    return i + 1  # 1-indexed

    return len(lines)


def parse_cuda_file(filepath: Path | str) -> CUDAFileInfo:
    """Parse a CUDA file and extract structure information."""
    filepath = Path(filepath)
    content = filepath.read_text()
    lines = content.split("\n")

    return CUDAFileInfo(
        path=filepath,
        includes=find_includes(content),
        kernels=find_kernel_functions(content),
        device_functions=find_device_functions(content),
        evolve_regions=find_evolve_markers(content),
        line_count=len(lines),
    )


def suggest_evolve_markers(info: CUDAFileInfo) -> str | None:
    """Suggest where to add EVOLVE markers if missing."""
    if info.has_evolve_markers:
        return None

    if not info.kernels:
        return None

    # Suggest wrapping the first kernel
    kernel = info.kernels[0]
    return f"""Consider adding EVOLVE markers around your kernel:

```cuda
// EVOLVE_START
{kernel.signature}
{{
    // ... kernel code ...
}}
// EVOLVE_END
```

Lines {kernel.start_line}-{kernel.end_line} contain the `{kernel.name}` kernel."""
