"""Generate OpenEvolve configuration for EvoKernel evolution runs."""

import os
from pathlib import Path

import yaml

DEFAULT_SYSTEM_MESSAGE = """You are an expert CUDA kernel developer optimizing code for maximum performance.

# OPTIMIZATION STRATEGIES:

**1. Algorithmic:**
- Fused operations to reduce memory bandwidth
- Better algorithms (e.g., Welford's for mean/variance)
- Reduced synchronization

**2. Memory Access:**
- __ldg() for read-only cache
- Coalesced access patterns
- Register caching
- Vectorized loads (float4)

**3. Parallelism:**
- Optimal block sizes (256, 512, 1024)
- Multiple elements per thread (ILP)
- Warp shuffle reductions
- Cooperative groups

**4. CUDA Specific:**
- #pragma unroll for critical loops
- __restrict__ on pointers
- Fast math intrinsics (rsqrtf, fmaf)

# CONSTRAINTS:
- MUST maintain the forward() function signature
- MUST use PYBIND11_MODULE for Python binding
- MUST pass correctness tests

Focus on targeted improvements to specific parts of the kernel."""


DEFAULT_MODELS = [
    {"name": "anthropic/claude-opus-4.5", "weight": 0.5},
    {"name": "anthropic/claude-sonnet-4.5", "weight": 0.5},
]


def build_openevolve_config(
    output_dir: Path,
    task: str = "layernorm",
    iterations: int = 100,
    goal: str = "speedup",
    population_size: int = 100,
    exploration_ratio: float = 0.25,
    system_message: str | None = None,
    models: list[dict] | None = None,
) -> Path:
    """Build OpenEvolve config.yaml for an EvoKernel run.

    Args:
        output_dir: Directory for this evolution run
        task: Task name (layernorm, mnist_linear, etc.)
        iterations: Number of evolution iterations
        goal: Optimization goal (speedup, memory)
        population_size: Size of the population pool
        exploration_ratio: How aggressively to explore (0.0-1.0, higher = more exploration)
        system_message: Custom system message for the LLM
        models: List of model configs, each with 'name' and 'weight' keys

    Returns:
        Path to the generated config.yaml

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set
    """
    from dotenv import load_dotenv

    # Load .env from standard config location: ~/.config/evokernel/.env
    config_dir = Path.home() / ".config" / "evokernel"
    env_file = config_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    # Get API key from environment
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            f"OPENROUTER_API_KEY not set.\n\n"
            f"Create {env_file} with:\n"
            f"  mkdir -p {config_dir}\n"
            f"  echo 'OPENROUTER_API_KEY=your_key' > {env_file}\n\n"
            "Get a key at https://openrouter.ai/"
        )

    config = {
        "max_iterations": iterations,
        "random_seed": 42,
        "checkpoint_interval": max(10, iterations // 10),
        "max_code_length": 15000,
        "diff_based_evolution": False,  # Full rewrites for CUDA
        # Early stopping
        "early_stopping_patience": max(50, iterations // 3),
        "convergence_threshold": 0.01,
        "early_stopping_metric": goal,
        # LLM configuration - use OpenRouter
        "llm": {
            "api_base": "https://openrouter.ai/api/v1",
            "api_key": api_key,
            "models": models if models else DEFAULT_MODELS,
            "evaluator_models": [
                {"name": "anthropic/claude-sonnet-4.5", "weight": 1.0},
            ],
            "temperature": 0.9,
            "max_tokens": 16000,
            "timeout": 120,
        },
        # Prompt configuration
        "prompt": {
            "num_top_programs": 4,
            "num_diverse_programs": 2,
            "include_artifacts": True,
            "system_message": system_message or DEFAULT_SYSTEM_MESSAGE,
        },
        # MAP-Elites database
        "database": {
            "num_islands": 5,
            "population_size": population_size,
            "feature_dimensions": [goal],
            "feature_bins": 20,
            "migration_interval": 25,
            "migration_rate": 0.15,
            "elite_selection_ratio": 0.15,
            "exploration_ratio": exploration_ratio,
            "exploitation_ratio": round(1.0 - exploration_ratio - 0.15, 2),
            "similarity_threshold": 0.95,
        },
        # Evaluator
        "evaluator": {
            "timeout": 300,
            "cascade_evaluation": False,
            "parallel_evaluations": 8,
            "use_llm_feedback": True,
            "llm_feedback_weight": 0.1,
        },
    }

    config_path = output_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    return config_path
