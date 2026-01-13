"""evo_mark tool - Auto-add EVOLVE markers to CUDA kernels."""

import shutil
from collections.abc import Generator
from pathlib import Path

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..cuda.parser import parse_cuda_file


def execute_mark(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Add EVOLVE markers to a CUDA kernel file."""
    kwargs = kwargs or {}

    filepath = kwargs.get("file") or (args[0] if args else None)
    if not filepath and code:
        filepath = code.strip().split()[0]

    if not filepath:
        yield Message("system", "Error: No file path provided. Use: evo_mark kernel.cu")
        return

    path = Path(filepath).expanduser()
    if not path.exists():
        yield Message("system", f"Error: File not found: {path}")
        return

    info = parse_cuda_file(path)

    if info.has_evolve_markers:
        yield Message(
            "system",
            f"File already has EVOLVE markers at lines {info.evolve_regions[0].start_line}-{info.evolve_regions[0].end_line}",
        )
        return

    if not info.kernels:
        yield Message("system", "Error: No __global__ kernel functions found in file")
        return

    # Determine which kernel to mark
    kernel_name = kwargs.get("kernel")
    if kernel_name:
        kernel = next((k for k in info.kernels if k.name == kernel_name), None)
        if not kernel:
            names = ", ".join(k.name for k in info.kernels)
            yield Message(
                "system", f"Error: Kernel '{kernel_name}' not found. Available: {names}"
            )
            return
    else:
        kernel = info.kernels[0]
        if len(info.kernels) > 1:
            names = ", ".join(k.name for k in info.kernels)
            yield Message(
                "system",
                f"Multiple kernels found: {names}\nMarking first kernel: {kernel.name}\nUse kernel=<name> to specify a different one.",
            )

    # Read file content
    lines = path.read_text().split("\n")

    # Find the line before the kernel signature (for EVOLVE_START)
    start_insert = kernel.start_line - 1  # 0-indexed, insert before
    end_insert = kernel.end_line  # Insert after this line (0-indexed would be end_line)

    # Confirm before modifying
    if not confirm(
        f"Add EVOLVE markers around {kernel.name} (lines {kernel.start_line}-{kernel.end_line})?"
    ):
        yield Message("system", "Cancelled.")
        return

    # Create backup
    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy(path, backup_path)

    # Insert markers
    new_lines = lines[:start_insert]
    new_lines.append("// EVOLVE_START")
    new_lines.extend(lines[start_insert:end_insert])
    new_lines.append("// EVOLVE_END")
    new_lines.extend(lines[end_insert:])

    # Write back
    path.write_text("\n".join(new_lines))

    yield Message(
        "system",
        f"""Added EVOLVE markers to {path.name}:
- Wrapped kernel `{kernel.name}` (lines {kernel.start_line}-{kernel.end_line})
- Backup saved to {backup_path.name}

The kernel is now ready for evolution with evo_evolve.""",
    )


evo_mark = ToolSpec(
    name="evo_mark",
    desc="Add EVOLVE_START/EVOLVE_END markers around a CUDA kernel function",
    instructions="""Use this tool to automatically add EVOLVE markers to a kernel.

The tool will:
1. Parse the CUDA file to find kernel functions
2. Add // EVOLVE_START before the kernel
3. Add // EVOLVE_END after the kernel
4. Create a .bak backup file

If multiple kernels exist, specify which one with kernel=<name>.""",
    examples="""
### Mark first kernel in file

```evo_mark src/kernel.cu
```

### Mark specific kernel

```evo_mark
file: src/kernels.cu
kernel: layernorm_forward
```
""",
    execute=execute_mark,
    block_types=["evo_mark"],
    parameters=[
        Parameter(
            name="file", type="string", description="Path to CUDA file", required=True
        ),
        Parameter(
            name="kernel",
            type="string",
            description="Kernel function name (optional, defaults to first)",
            required=False,
        ),
    ],
)
