"""evo_apply tool - Apply evolved kernel to codebase."""

import shutil
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..openevolve_integration.runner import get_best_kernel_code, get_evolution_status


def execute_apply(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Apply evolved kernel to the codebase."""

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

        runs = sorted(
            evokernel_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not runs:
            yield Message("system", "No evolution runs found.")
            return
        run_dir = str(runs[0])

    run_path = Path(run_dir)

    # Get best kernel code using helper
    best_code = get_best_kernel_code(run_path)

    if not best_code:
        # Fallback: check standard paths
        for path in [run_path / "best_program.cu", run_path / "best.cu"]:
            if path.exists():
                best_code = path.read_text()
                break

    if not best_code:
        yield Message("system", f"No best program found in {run_dir}")
        return

    # Find original path
    original_path_file = run_path / "original_path.txt"
    if original_path_file.exists():
        target_path = Path(original_path_file.read_text().strip())
    else:
        yield Message("system", "Original file path not found. Cannot apply.")
        return

    if not target_path.exists():
        yield Message("system", f"Original file no longer exists: {target_path}")
        return

    # Get status for info
    status = get_evolution_status(run_path)
    speedup = status.get("best_speedup", 0)

    # Confirm
    preview = best_code[:500] + "..." if len(best_code) > 500 else best_code
    speedup_info = f" ({speedup:.2f}x speedup)" if speedup else ""

    if not confirm(
        f"Apply evolved kernel{speedup_info} to {target_path}?\n\nPreview:\n```cuda\n{preview}\n```"
    ):
        yield Message("system", "Apply cancelled.")
        return

    # Create backup
    backup_dir = Path.cwd() / ".evokernel" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{target_path.name}.{timestamp}.backup"
    shutil.copy(target_path, backup_path)

    # Apply
    target_path.write_text(best_code)

    yield Message(
        "system",
        f"""Applied evolved kernel!

**Target:** `{target_path}`
**Backup:** `{backup_path}`

The original file has been backed up. You can restore it with:
```bash
cp {backup_path} {target_path}
```
""",
    )


evo_apply = ToolSpec(
    name="evo_apply",
    desc="Apply the evolved kernel to the original file in your codebase",
    instructions="""Use this tool to write the optimized kernel back to your codebase.

The original file is backed up to .evokernel/backups/ before overwriting.""",
    examples="""
### Apply latest evolution result

```evo_apply
```

### Apply specific run

```evo_apply .evokernel/evolution/layernorm_20240101_120000
```
""",
    execute=execute_apply,
    block_types=["evo_apply"],
    parameters=[
        Parameter(
            name="run_dir",
            type="string",
            description="Path to evolution run directory",
            required=False,
        ),
    ],
)
