"""evo_compare tool - Compare two CUDA kernels."""

import difflib
from collections.abc import Generator
from pathlib import Path

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..cuda.parser import parse_cuda_file


def generate_side_by_side_diff(file1: Path, file2: Path, context: int = 3) -> str:
    """Generate a side-by-side diff view."""
    lines1 = file1.read_text().splitlines()
    lines2 = file2.read_text().splitlines()

    differ = difflib.unified_diff(
        lines1, lines2, fromfile=file1.name, tofile=file2.name, lineterm="", n=context
    )
    return "\n".join(differ)


def compare_kernel_structure(info1, info2) -> list[str]:
    """Compare structural differences between two kernels."""
    diffs = []

    # Compare kernel count
    k1 = len(info1.kernels)
    k2 = len(info2.kernels)
    if k1 != k2:
        diffs.append(f"Kernel count: {k1} vs {k2}")

    # Compare kernel names
    names1 = {k.name for k in info1.kernels}
    names2 = {k.name for k in info2.kernels}
    if names1 != names2:
        added = names2 - names1
        removed = names1 - names2
        if added:
            diffs.append(f"Added kernels: {', '.join(added)}")
        if removed:
            diffs.append(f"Removed kernels: {', '.join(removed)}")

    # Compare device functions
    d1 = len(info1.device_functions)
    d2 = len(info2.device_functions)
    if d1 != d2:
        diffs.append(f"Device functions: {d1} vs {d2}")

    # Compare includes
    inc1 = set(info1.includes)
    inc2 = set(info2.includes)
    if inc1 != inc2:
        added = inc2 - inc1
        removed = inc1 - inc2
        if added:
            diffs.append(f"Added includes: {', '.join(added)}")
        if removed:
            diffs.append(f"Removed includes: {', '.join(removed)}")

    # Compare line counts
    lines_diff = info2.line_count - info1.line_count
    if abs(lines_diff) > 5:
        sign = "+" if lines_diff > 0 else ""
        diffs.append(f"Line count change: {sign}{lines_diff}")

    return diffs


def execute_compare(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Compare two CUDA kernel files."""
    kwargs = kwargs or {}

    # Get file paths
    file1 = kwargs.get("file1") or (args[0] if args and len(args) > 0 else None)
    file2 = kwargs.get("file2") or (args[1] if args and len(args) > 1 else None)

    # Parse YAML-style input from code block
    if code and not (file1 and file2):
        import yaml

        try:
            parsed = yaml.safe_load(code)
            if isinstance(parsed, dict):
                file1 = file1 or parsed.get("file1") or parsed.get("original")
                file2 = file2 or parsed.get("file2") or parsed.get("optimized")
        except yaml.YAMLError:
            # Try to parse as two paths
            parts = code.strip().split()
            if len(parts) >= 2:
                file1 = file1 or parts[0]
                file2 = file2 or parts[1]

    if not file1 or not file2:
        yield Message(
            "system",
            """Error: Two files required.

Usage:
```evo_compare original.cu optimized.cu```

Or:
```evo_compare
file1: original.cu
file2: optimized.cu
```""",
        )
        return

    path1 = Path(file1).expanduser()
    path2 = Path(file2).expanduser()

    if not path1.exists():
        yield Message("system", f"Error: File not found: {path1}")
        return
    if not path2.exists():
        yield Message("system", f"Error: File not found: {path2}")
        return

    # Parse both files
    try:
        info1 = parse_cuda_file(path1)
        info2 = parse_cuda_file(path2)
    except Exception as e:
        yield Message("system", f"Error parsing files: {e}")
        return

    lines = [f"**Comparison: {path1.name} vs {path2.name}**", ""]

    # Structural comparison
    lines.append("## Structure")
    lines.append(f"| Metric | {path1.name} | {path2.name} |")
    lines.append("|--------|-------------|-------------|")
    lines.append(f"| Lines | {info1.line_count} | {info2.line_count} |")
    lines.append(f"| Kernels | {len(info1.kernels)} | {len(info2.kernels)} |")
    lines.append(
        f"| Device funcs | {len(info1.device_functions)} | {len(info2.device_functions)} |"
    )
    lines.append(f"| Includes | {len(info1.includes)} | {len(info2.includes)} |")
    lines.append("")

    # Key differences
    struct_diffs = compare_kernel_structure(info1, info2)
    if struct_diffs:
        lines.append("## Key Differences")
        for d in struct_diffs:
            lines.append(f"- {d}")
        lines.append("")

    # Code diff
    diff_text = generate_side_by_side_diff(path1, path2)
    if diff_text:
        # Truncate if too long
        diff_lines = diff_text.split("\n")
        if len(diff_lines) > 100:
            diff_text = (
                "\n".join(diff_lines[:100])
                + f"\n... ({len(diff_lines) - 100} more lines)"
            )

        lines.append("## Code Diff")
        lines.append(f"```diff\n{diff_text}\n```")
    else:
        lines.append("## Code Diff")
        lines.append("*Files are identical*")

    yield Message("system", "\n".join(lines))


evo_compare = ToolSpec(
    name="evo_compare",
    desc="Compare two CUDA kernel files showing structural and code differences",
    instructions="""Use this tool to compare two CUDA kernel files.

It shows:
- Structural comparison (line count, kernels, functions, includes)
- Key differences (added/removed kernels, functions)
- Code diff (unified format)

Useful for comparing original vs optimized kernels, or different optimization approaches.""",
    examples="""
### Compare two files

```evo_compare original.cu optimized.cu
```

### Compare with YAML syntax

```evo_compare
file1: src/kernel_v1.cu
file2: src/kernel_v2.cu
```

### Compare initial vs best from evolution

```evo_compare .evokernel/evolution/latest/initial.cu .evokernel/evolution/latest/best_program.cu
```
""",
    execute=execute_compare,
    block_types=["evo_compare"],
    parameters=[
        Parameter(
            name="file1",
            type="string",
            description="First CUDA file (original)",
            required=True,
        ),
        Parameter(
            name="file2",
            type="string",
            description="Second CUDA file (optimized)",
            required=True,
        ),
    ],
)
