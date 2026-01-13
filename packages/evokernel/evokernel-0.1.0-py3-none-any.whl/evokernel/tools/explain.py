"""evo_explain tool - Explain optimization results using LLM."""

import difflib
from pathlib import Path
from typing import Generator

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..openevolve_integration.runner import get_best_kernel_code, get_evolution_status


def execute_explain(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Explain optimization results."""
    kwargs = kwargs or {}

    # Get run directory
    if "run_dir" in kwargs:
        run_dir = kwargs["run_dir"]
    elif args:
        run_dir = args[0]
    else:
        # Find most recent completed run
        evokernel_dir = Path.cwd() / ".evokernel" / "evolution"
        if not evokernel_dir.exists():
            yield Message("system", "No evolution runs found.")
            return

        runs = sorted(evokernel_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        if not runs:
            yield Message("system", "No evolution runs found.")
            return
        run_dir = str(runs[0])

    run_path = Path(run_dir)
    if not run_path.exists():
        yield Message("system", f"Run directory not found: {run_dir}")
        return

    # Get status
    status = get_evolution_status(run_path)

    # Get initial and best code
    initial_path = run_path / "initial.cu"
    if not initial_path.exists():
        yield Message("system", "Initial kernel not found.")
        return

    initial_code = initial_path.read_text()
    best_code = get_best_kernel_code(run_path)

    if not best_code:
        yield Message("system", "No optimized kernel found yet. Evolution may still be running.")
        return

    # Generate diff
    diff = difflib.unified_diff(
        initial_code.splitlines(keepends=True),
        best_code.splitlines(keepends=True),
        fromfile="initial.cu",
        tofile="optimized.cu",
        lineterm=""
    )
    diff_text = "".join(diff)

    if not diff_text.strip():
        yield Message("system", "No changes were made to the kernel.")
        return

    # Build explanation prompt for the assistant
    speedup = status.get("best_speedup", 0)
    score = status.get("best_score", 0)

    explanation_request = f"""Please analyze the following CUDA kernel optimization and explain:

1. **What optimizations were applied** - Describe each change
2. **Why they improve performance** - Explain the performance impact
3. **Potential further optimizations** - Suggest what else could be tried

## Performance Results
- Speedup: {speedup:.2f}x
- Score: {score:.4f}

## Diff (initial -> optimized)
```diff
{diff_text}
```

## Initial Kernel
```cuda
{initial_code[:2000]}{'...' if len(initial_code) > 2000 else ''}
```

## Optimized Kernel
```cuda
{best_code[:2000]}{'...' if len(best_code) > 2000 else ''}
```

Provide a clear, technical explanation of the optimizations."""

    # Return as a user message so the assistant will respond
    yield Message("user", explanation_request)


evo_explain = ToolSpec(
    name="evo_explain",
    desc="Explain what optimizations were applied to a kernel and why they improve performance",
    instructions="""Use this tool after evolution completes to get an explanation of:
- What changes were made to the kernel
- Why those changes improve performance
- What further optimizations could be tried

The tool generates a prompt for the assistant to analyze the diff.""",
    examples="""
### Explain latest evolution

```evo_explain
```

### Explain specific run

```evo_explain .evokernel/evolution/layernorm_20240101_120000
```
""",
    execute=execute_explain,
    block_types=["evo_explain"],
    parameters=[
        Parameter(name="run_dir", type="string", description="Path to evolution run directory", required=False),
    ],
)
