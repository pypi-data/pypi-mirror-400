"""evo_show tool - Display evolution results."""

import difflib
from pathlib import Path
from typing import Generator

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..openevolve_integration.runner import get_best_kernel_code, get_evolution_status


def execute_show(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Show evolution results."""
    
    kwargs = kwargs or {}
    
    # Get run directory
    if "run_dir" in kwargs:
        run_dir = kwargs["run_dir"]
    elif args:
        run_dir = args[0]
    else:
        # Find most recent run
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
    
    # Get status for context
    status = get_evolution_status(run_path)
    
    # Get best kernel code
    best_code = get_best_kernel_code(run_path)
    
    if not best_code:
        # Fallback: check standard paths
        for path in [run_path / "best_program.cu", run_path / "best.cu"]:
            if path.exists():
                best_code = path.read_text()
                break
    
    if not best_code:
        yield Message("system", f"No best program found yet in {run_dir}\nStatus: {status}")
        return
    
    # Show status summary
    status_line = []
    if status.get("best_speedup"):
        status_line.append(f"Speedup: {status['best_speedup']:.2f}x")
    if status.get("best_score"):
        status_line.append(f"Score: {status['best_score']:.4f}")
    if status.get("iteration"):
        status_line.append(f"Iteration: {status['iteration']}/{status.get('max_iterations', '?')}")
    
    # Show diff or full code
    show_diff = kwargs.get("diff", "true").lower() == "true"
    
    if show_diff:
        initial_path = run_path / "initial.cu"
        if initial_path.exists():
            initial_code = initial_path.read_text()
            
            diff = difflib.unified_diff(
                initial_code.splitlines(keepends=True),
                best_code.splitlines(keepends=True),
                fromfile="initial.cu",
                tofile="best.cu",
            )
            diff_text = "".join(diff)
            
            header = " | ".join(status_line) if status_line else ""
            if diff_text:
                yield Message("system", f"**Best kernel** ({header})\n\n```diff\n{diff_text}```")
            else:
                yield Message("system", f"No changes from original. ({header})")
        else:
            yield Message("system", f"**Best kernel:**\n\n```cuda\n{best_code}```")
    else:
        header = " | ".join(status_line) if status_line else ""
        yield Message("system", f"**Best kernel** ({header})\n\n```cuda\n{best_code}```")


evo_show = ToolSpec(
    name="evo_show",
    desc="Display the best evolved kernel, optionally as a diff",
    instructions="""Use this tool to view the evolution results.

By default shows a diff against the original. Use diff=false for full code.""",
    examples="""
### Show diff

```evo_show
```

### Show full code

```evo_show
diff: false
```
""",
    execute=execute_show,
    block_types=["evo_show"],
    parameters=[
        Parameter(name="run_dir", type="string", description="Path to evolution run directory", required=False),
        Parameter(name="diff", type="string", description="Show diff (true) or full code (false)", required=False),
    ],
)
