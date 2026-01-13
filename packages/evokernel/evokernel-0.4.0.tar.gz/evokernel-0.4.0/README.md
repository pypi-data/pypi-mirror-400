# EvoKernel

CUDA kernel optimization agent powered by OpenEvolve.

## Quick Start

```bash
# Install as CLI tool (requires Python 3.10-3.13)
pipx install evokernel
# or with uv
uv tool install evokernel

# Setup Modal (GPU evaluator)
modal setup

# Configure OpenRouter API key
evokernel setup

# Run in any project directory
evokernel
```

### Development Install

```bash
git clone https://github.com/haladir-ai/EvoKernel.git
cd EvoKernel
uv tool install .
```

## Usage

Just run `evokernel` in a directory with CUDA kernels and chat with the agent:

```
> optimize my_kernel.cu

> check status

> show the best result

> apply changes
```

## Current Features

- **Speedup optimization**: Maximizes kernel throughput via evolutionary search
- **EVOLVE markers**: Define which code regions to optimize
- **Modal GPU evaluation**: Compile and benchmark on cloud A100 (default)
- **Local GPU evaluation**: Run benchmarks on your own GPU (for codebases with dependencies)
- **LLM ensemble**: Uses Gemini, Claude, GPT via OpenRouter

## Evaluator Modes

| Mode | Use Case |
|------|----------|
| `modal` (default) | Self-contained kernels, no local GPU needed |
| `local` | Kernels with custom headers/dependencies |

## Roadmap (Not Yet Implemented)

- **Memory optimization goal**: Minimize memory usage instead of speedup
- **Target hardware selection**: Optimize for specific GPUs (A100, H100, V100)
- **Energy efficiency goal**: Minimize power consumption
