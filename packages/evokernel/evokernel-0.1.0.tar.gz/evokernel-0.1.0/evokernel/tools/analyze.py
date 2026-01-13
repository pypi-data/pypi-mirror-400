"""evo_analyze tool - Analyze CUDA kernel structure."""

from pathlib import Path
from typing import Generator

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..cuda.parser import parse_cuda_file, suggest_evolve_markers
from ..cuda.context import format_kernel_summary


def execute_analyze(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Analyze a CUDA kernel file."""
    
    # Get file path from args, kwargs, or code content
    filepath = None
    if kwargs and "file" in kwargs:
        filepath = kwargs["file"]
    elif args:
        filepath = args[0]
    elif code and code.strip():
        # Code block content is the file path
        filepath = code.strip().split()[0]  # Take first word/line
    
    if not filepath:
        yield Message("system", "Error: No file path provided. Use: evo_analyze path/to/kernel.cu")
        return
    
    path = Path(filepath).expanduser()
    
    if not path.exists():
        yield Message("system", f"Error: File not found: {path}")
        return
    
    if not path.suffix in [".cu", ".cuh", ".cuda"]:
        yield Message("system", f"Warning: File {path} may not be a CUDA file")
    
    try:
        info = parse_cuda_file(path)
    except Exception as e:
        yield Message("system", f"Error parsing CUDA file: {e}")
        return
    
    # Format summary
    summary = format_kernel_summary(info)
    
    # Add marker suggestion if needed
    marker_suggestion = suggest_evolve_markers(info)
    if marker_suggestion:
        summary += "\n\n" + marker_suggestion
    
    yield Message("system", summary)


evo_analyze = ToolSpec(
    name="evo_analyze",
    desc="Analyze a CUDA kernel file to understand its structure, functions, and dependencies",
    instructions="""Use this tool to analyze a CUDA kernel file before optimization.
It will extract:
- Kernel functions (__global__)
- Device functions (__device__)
- Include dependencies
- EVOLVE_START/EVOLVE_END marker regions

If no EVOLVE markers exist, it will suggest where to add them.""",
    examples="""
### Analyze a kernel file

```evo_analyze src/kernels/layernorm.cu
```
""",
    execute=execute_analyze,
    block_types=["evo_analyze"],
    parameters=[
        Parameter(name="file", type="string", description="Path to CUDA file", required=True),
    ],
)
