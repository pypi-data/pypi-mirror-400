"""evo_status tool - Check evolution progress."""

import json
import time
from collections.abc import Generator
from pathlib import Path

from rich.console import Console

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..openevolve_integration.runner import get_evolution_status


def format_status_rich(status: dict, run_path: Path) -> str:
    """Format status with rich text indicators."""
    Console(force_terminal=True, width=80)

    # Status indicator
    if status.get("running"):
        status_text = "[bold green]Running[/bold green]"
        status_emoji = "🔄"
    elif status.get("completed"):
        status_text = "[bold blue]Completed[/bold blue]"
        status_emoji = "✅"
    elif status.get("error"):
        status_text = "[bold red]Error[/bold red]"
        status_emoji = "❌"
    else:
        status_text = "[dim]Unknown[/dim]"
        status_emoji = "❓"

    # Progress calculation
    iteration = status.get("iteration", 0)
    max_iter = status.get("max_iterations", 100)
    progress_pct = (iteration / max_iter * 100) if max_iter > 0 else 0

    # Progress bar (ASCII)
    bar_width = 30
    filled = int(bar_width * progress_pct / 100)
    bar = "█" * filled + "░" * (bar_width - filled)

    # ETA calculation
    eta_str = ""
    if status.get("running") and iteration > 0:
        # Try to get start time from process_info
        info_path = run_path / "process_info.json"
        if info_path.exists():
            try:
                json.load(open(info_path))
                start_time = info_path.stat().st_mtime
                elapsed = time.time() - start_time
                if iteration > 0:
                    time_per_iter = elapsed / iteration
                    remaining_iters = max_iter - iteration
                    eta_seconds = time_per_iter * remaining_iters
                    if eta_seconds < 60:
                        eta_str = f"~{int(eta_seconds)}s"
                    elif eta_seconds < 3600:
                        eta_str = f"~{int(eta_seconds / 60)}m"
                    else:
                        eta_str = f"~{int(eta_seconds / 3600)}h {int((eta_seconds % 3600) / 60)}m"
            except Exception:
                pass

    # Build output
    lines = [
        f"**Evolution: {run_path.name}**",
        "",
        f"Status: {status_emoji} {status_text}",
        "",
        f"Progress: [{bar}] {progress_pct:.1f}%",
        f"Iteration: {iteration} / {max_iter}"
        + (f"  ETA: {eta_str}" if eta_str else ""),
    ]

    # Metrics
    if status.get("best_speedup") or status.get("best_score"):
        lines.append("")
        lines.append("**Best Result:**")
        if status.get("best_speedup"):
            speedup = status["best_speedup"]
            if speedup >= 1.5:
                lines.append(f"  Speedup: [green]{speedup:.2f}x[/green]")
            elif speedup >= 1.0:
                lines.append(f"  Speedup: [yellow]{speedup:.2f}x[/yellow]")
            else:
                lines.append(f"  Speedup: [red]{speedup:.2f}x[/red]")
        if status.get("best_score"):
            lines.append(f"  Score: {status['best_score']:.4f}")
        if status.get("compile_success"):
            lines.append(f"  Compile: {'✓' if status['compile_success'] else '✗'}")
        if status.get("correct"):
            lines.append(f"  Correct: {'✓' if status['correct'] else '✗'}")

    # Error
    if status.get("error"):
        lines.append("")
        lines.append(f"[red]Error: {status['error']}[/red]")

    return "\n".join(lines)


def execute_status(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Check evolution progress."""
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
            yield Message("system", "No evolution runs found. Run evo_evolve first.")
            return

        runs = sorted(
            evokernel_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not runs:
            yield Message("system", "No evolution runs found.")
            return
        run_dir = str(runs[0])

    run_path = Path(run_dir)
    if not run_path.exists():
        yield Message("system", f"Run directory not found: {run_dir}")
        return

    # Get status
    try:
        status = get_evolution_status(run_path)
    except Exception as e:
        yield Message("system", f"Error reading status: {e}")
        return

    # Format with rich indicators
    output = format_status_rich(status, run_path)
    yield Message("system", output)


evo_status = ToolSpec(
    name="evo_status",
    desc="Check the progress of a running or completed evolution",
    instructions="""Use this tool to check evolution progress.

If no run directory is specified, it checks the most recent run.""",
    examples="""
### Check latest run

```evo_status
```

### Check specific run

```evo_status .evokernel/evolution/layernorm_20240101_120000
```
""",
    execute=execute_status,
    block_types=["evo_status"],
    parameters=[
        Parameter(
            name="run_dir",
            type="string",
            description="Path to evolution run directory",
            required=False,
        ),
    ],
)
