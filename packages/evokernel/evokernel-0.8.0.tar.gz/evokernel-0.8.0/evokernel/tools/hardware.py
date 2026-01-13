"""evo_hardware tool - Detect local GPU hardware."""

from collections.abc import Generator

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, ToolSpec

from ..openevolve_integration.runner import detect_local_gpu


def execute_hardware(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Detect local GPU hardware."""

    gpu_info = detect_local_gpu()

    if gpu_info["gpu_available"]:
        yield Message(
            "system",
            f"""**Local GPU Detected**

| Property | Value |
|----------|-------|
| GPU | {gpu_info["gpu_name"]} |
| Memory | {gpu_info["memory_gb"]:.1f} GB |
| Compute Capability | {gpu_info["compute_capability"]} |
| CUDA Version | {gpu_info["cuda_version"]} |

You can use `evaluator: local` for evolution runs on this GPU.
""",
        )
    else:
        yield Message(
            "system",
            """**No Local GPU Detected**

nvidia-smi not found or no GPU available.

Use `evaluator: modal` (default) to run benchmarks on Modal cloud GPU.
""",
        )


evo_hardware = ToolSpec(
    name="evo_hardware",
    desc="Detect local GPU hardware to determine if local evaluation is possible",
    instructions="""Use this tool to check if the user has a local GPU for evaluation.

If a GPU is detected, the user can use `evaluator: local` in evo_evolve to:
- Run benchmarks on their own GPU
- Use kernels with custom dependencies/headers
- Avoid Modal cloud costs

If no GPU is detected, they should use the default `evaluator: modal`.""",
    examples="""
### Check for local GPU

```evo_hardware
```
""",
    execute=execute_hardware,
    block_types=["evo_hardware"],
    parameters=[],
)
