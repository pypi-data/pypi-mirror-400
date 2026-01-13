"""evo_evolve tool - Launch OpenEvolve optimization."""

import shutil
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec

from ..openevolve_integration.config import build_openevolve_config
from ..openevolve_integration.runner import detect_local_gpu, spawn_openevolve


def execute_evolve(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Launch kernel evolution using OpenEvolve."""

    import yaml

    kwargs = kwargs or {}
    parsed_yaml = None

    # Parse YAML-style content from code block if kwargs is empty
    if code and not kwargs:
        try:
            parsed_yaml = yaml.safe_load(code)
            if isinstance(parsed_yaml, dict):
                kwargs = {
                    k: str(v) if not isinstance(v, list) else v
                    for k, v in parsed_yaml.items()
                }
        except yaml.YAMLError:
            # Not YAML, might be a simple path
            if code.strip() and not code.strip().startswith("#"):
                args = [code.strip()]

    target = kwargs.get("target") or (args[0] if args else None)
    if not target:
        yield Message(
            "system",
            "Error: No target kernel specified. Use: evo_evolve path/to/kernel.cu",
        )
        return

    target_path = Path(target).expanduser()
    if not target_path.exists():
        yield Message("system", f"Error: Target file not found: {target_path}")
        return

    # Get parameters
    task_raw = kwargs.get("task", "layernorm")
    # Handle standalone mode
    if task_raw.lower() in ("standalone", "none", "null"):
        task = None  # Standalone mode
    else:
        task = task_raw

    iterations = int(kwargs.get("iterations", "100"))
    goal = kwargs.get("goal", "speedup")
    population_size = int(kwargs.get("population_size", "100"))
    exploration_ratio = float(kwargs.get("exploration_ratio", "0.25"))
    evaluator = kwargs.get("evaluator", "modal")
    gpu_type = kwargs.get("gpu", "a100").lower()

    # Parse include_dirs (comma-separated or YAML list)
    include_dirs_raw = kwargs.get("include_dirs", "")
    if isinstance(include_dirs_raw, list):
        include_dirs = include_dirs_raw
    elif include_dirs_raw:
        include_dirs = [d.strip() for d in include_dirs_raw.split(",") if d.strip()]
    else:
        include_dirs = []

    # Parse models (YAML list of dicts with 'name' and 'weight')
    models_raw = kwargs.get("models")
    if isinstance(models_raw, list):
        models = models_raw
    elif isinstance(models_raw, str):
        models = yaml.safe_load(models_raw)
    elif parsed_yaml and "models" in parsed_yaml:
        models = parsed_yaml["models"]
    else:
        models = None

    # Validate evaluator mode and GPU selection
    valid_gpus = [
        "t4",
        "l4",
        "a10g",
        "a100",
        "a100-80gb",
        "l40s",
        "h100",
        "h200",
        "b200",
    ]
    if evaluator == "local":
        gpu_info = detect_local_gpu()
        if not gpu_info["gpu_available"]:
            yield Message(
                "system",
                "Error: Local evaluator requested but no GPU detected. Use evaluator: modal instead.",
            )
            return
        gpu_desc = f"{gpu_info['gpu_name']} ({gpu_info['memory_gb']:.1f}GB, CUDA {gpu_info['cuda_version']})"
    else:
        evaluator = "modal"
        if gpu_type not in valid_gpus:
            yield Message(
                "system",
                f"Error: Invalid GPU type '{gpu_type}'. Valid options: {', '.join(valid_gpus)}",
            )
            return
        gpu_desc = f"Modal cloud GPU ({gpu_type.upper()})"

    # Set up output directory
    workspace = Path.cwd() / ".evokernel"
    workspace.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = workspace / "evolution" / f"{target_path.stem}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Copy initial kernel
    initial_path = run_dir / "initial.cu"
    shutil.copy(target_path, initial_path)

    # Save original path for later
    (run_dir / "original_path.txt").write_text(str(target_path.absolute()))

    # Build config
    try:
        config_path = build_openevolve_config(
            output_dir=run_dir,
            task=task,
            iterations=iterations,
            goal=goal,
            population_size=population_size,
            exploration_ratio=exploration_ratio,
            models=models,
        )
    except Exception as e:
        yield Message("system", f"Error building config: {e}")
        return

    # Standalone mode warning
    task_display = task if task else "standalone"
    if task is None:
        yield Message(
            "system",
            """⚠️ **STANDALONE MODE WARNING**

You're running without a matching task. This means:
- **No correctness checking** - the evolved kernel may produce wrong results
- Speedup is measured against the initial kernel (iteration 0)
- **You must verify the output yourself!**

Make sure to test the evolved kernel's correctness before using it in production.
""",
        )

    # Confirm before starting
    confirm_msg = f"Start evolution for {target_path.name}? ({iterations} iterations, task={task_display}, evaluator={evaluator})"
    if task is None:
        confirm_msg += "\n⚠️ STANDALONE MODE - No correctness verification!"
    if not confirm(confirm_msg):
        yield Message("system", "Evolution cancelled.")
        return

    # Spawn OpenEvolve
    try:
        process_info = spawn_openevolve(
            initial_program=initial_path,
            config_path=config_path,
            output_dir=run_dir,
            task=task,
            evaluator_mode=evaluator,
            include_dirs=include_dirs if evaluator == "local" else None,
            gpu_type=gpu_type,
        )
    except Exception as e:
        yield Message("system", f"Error starting evolution: {e}")
        return

    standalone_note = (
        "\n⚠️ **STANDALONE MODE** - No correctness verification. Verify output manually!"
        if task is None
        else ""
    )
    yield Message(
        "system",
        f"""Evolution started!

**Run directory:** `{run_dir}`
**Task:** {task_display}
**Iterations:** {iterations}
**Evaluator:** {evaluator} ({gpu_desc})
**PID:** {process_info.get("pid", "unknown")}{standalone_note}

Use `evo_status {run_dir}` to check progress.

**Tip:** Type `/dashboard` to open a live web dashboard.
""",
    )


evo_evolve = ToolSpec(
    name="evo_evolve",
    desc="Launch evolutionary optimization of a CUDA kernel using OpenEvolve",
    instructions="""Start kernel evolution. The target kernel MUST have EVOLVE_START/EVOLVE_END markers.

## Model Configuration (ASK USER FIRST)

Before starting evolution, ask the user which models they want to use.

**Explain to user:**
- Evolution uses an ensemble of LLMs that propose kernel improvements
- Each model has a weight (0.0-1.0) determining how often it's selected
- Higher weight = used more often
- Mix of models provides diverse optimization strategies

**Default models** (via OpenRouter):
- google/gemini-2.5-flash (weight: 0.4) - fast, good for iteration
- anthropic/claude-sonnet-4 (weight: 0.4) - strong reasoning
- openai/gpt-4.1 (weight: 0.2) - alternative perspective

**Ask user:** "Which models would you like to use for evolution? You can use defaults or specify custom models with weights."

## GPU Selection (ASK USER FIRST when using Modal)

Before starting evolution with Modal, ask the user which GPU they want to use:

**Available GPUs:**
| GPU      | Use Case                                      | Cost |
|----------|-----------------------------------------------|------|
| t4       | Budget option, good for small kernels        | $    |
| l4       | Good balance of cost and performance         | $    |
| a10g     | Good for medium kernels                       | $$   |
| a100     | Default, excellent for most workloads        | $$$  |
| a100-80gb| Large kernels requiring more memory          | $$$$ |
| l40s     | Good for inference workloads                 | $$$  |
| h100     | Premium, best for large/complex kernels      | $$$$$ |
| h200     | Top tier, massive memory                      | $$$$$ |
| b200     | Cutting edge (if available)                   | $$$$$ |

**Ask user:** "Which GPU would you like to use? (default: a100)"

Use the `choice` tool to let the user select:
```choice
Select GPU for kernel benchmarking:
- t4: Budget option for small kernels
- l4: Good balance of cost and performance
- a100: Default, excellent for most workloads (recommended)
- h100: Premium, best for complex kernels
```

## Available Parameters

| Parameter         | Required | Default     | Description |
|-------------------|----------|-------------|-------------|
| target            | YES      | -           | Path to CUDA kernel file |
| task              | no       | "layernorm" | Task name or "standalone" for custom kernels |
| iterations        | no       | 100      | Number of evolution iterations |
| population_size   | no       | 100      | Size of the population pool (more = more diversity) |
| exploration_ratio | no       | 0.25     | How aggressively to explore new variants (0.0-0.8) |
| evaluator         | no       | "modal"  | Where to run benchmarks: "modal" (cloud) or "local" (user's GPU) |
| gpu               | no       | "a100"   | GPU type for modal: t4, l4, a10g, a100, a100-80gb, l40s, h100, h200, b200 |
| include_dirs      | no       | -        | Extra include directories for local mode (comma-separated) |
| models            | no       | (see above) | List of models with weights for the LLM ensemble |

## Task Modes

Available tasks: layernorm, llama_ffw, llama_rmsnorm, mnist_conv_relu_pool, mnist_cross_entropy,
mnist_linear, mnist_linear_relu, mnist_pool, resnet_block, unet_conv2d, unet_linear

**Standalone mode** (task: standalone): Use when kernel doesn't match any task.
- No correctness checking - evolved kernel may produce wrong results
- Speedup measured against iteration 0 (baseline)
- User MUST verify output manually

## Evaluator Modes

- **modal** (default): Benchmarks run on Modal cloud GPU (A100). Kernel must be self-contained.
- **local**: Benchmarks run on user's local GPU. Supports codebases with dependencies.

When user has a kernel with custom headers or is part of a larger codebase, use evaluator: local.

## What happens

1. Copies target kernel to .evokernel/evolution/
2. Generates OpenEvolve config with LLM ensemble (Gemini, Claude, GPT via OpenRouter)
3. Spawns OpenEvolve as background process
4. Benchmarks each variant (Modal cloud or local GPU)
5. Returns run directory for status checking""",
    examples="""
### Cloud GPU (Modal) - default for self-contained kernels

```evo_evolve src/kernels/layernorm.cu
```

### Local GPU - for kernels with dependencies

```evo_evolve
target: src/kernels/my_kernel.cu
task: attention
evaluator: local
include_dirs: ./include, ./third_party/cutlass/include
iterations: 100
```

### Standalone mode - for custom kernels without matching task

```evo_evolve
target: src/kernels/custom_fused_op.cu
task: standalone
iterations: 50
```

### Using H100 GPU for complex kernels

```evo_evolve
target: src/kernels/large_kernel.cu
gpu: h100
iterations: 100
```

### Budget option with T4 for simple kernels

```evo_evolve
target: src/kernels/simple_op.cu
gpu: t4
iterations: 50
```

### Custom model configuration

```evo_evolve
target: src/kernels/layernorm.cu
iterations: 100
models:
  - name: anthropic/claude-sonnet-4
    weight: 0.6
  - name: google/gemini-2.5-flash
    weight: 0.4
```

### Single model (faster, less diverse)

```evo_evolve
target: src/kernels/layernorm.cu
models:
  - name: google/gemini-2.5-flash
    weight: 1.0
```
""",
    execute=execute_evolve,
    block_types=["evo_evolve"],
    parameters=[
        Parameter(
            name="target",
            type="string",
            description="Path to CUDA kernel file (required)",
            required=True,
        ),
        Parameter(
            name="task",
            type="string",
            description="Task name (default: layernorm)",
            required=False,
        ),
        Parameter(
            name="iterations",
            type="integer",
            description="Number of evolution iterations (default: 100)",
            required=False,
        ),
        Parameter(
            name="population_size",
            type="integer",
            description="Size of population pool (default: 100)",
            required=False,
        ),
        Parameter(
            name="exploration_ratio",
            type="number",
            description="Exploration vs exploitation 0.0-0.8 (default: 0.25)",
            required=False,
        ),
        Parameter(
            name="evaluator",
            type="string",
            description="'modal' (cloud) or 'local' (user's GPU) (default: modal)",
            required=False,
        ),
        Parameter(
            name="gpu",
            type="string",
            description="GPU type for modal: t4, l4, a10g, a100, a100-80gb, l40s, h100, h200, b200 (default: a100)",
            required=False,
        ),
        Parameter(
            name="include_dirs",
            type="string",
            description="Extra include directories for local mode (comma-separated)",
            required=False,
        ),
        Parameter(
            name="models",
            type="array",
            description="List of models with 'name' and 'weight' for the LLM ensemble",
            required=False,
        ),
    ],
)
