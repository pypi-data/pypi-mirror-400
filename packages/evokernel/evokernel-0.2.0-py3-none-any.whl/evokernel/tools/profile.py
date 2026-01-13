"""evo_profile tool - Profile CUDA kernel performance."""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

from gptme.message import Message
from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec


def check_profiling_tools() -> dict:
    """Check which profiling tools are available."""
    tools = {
        "ncu": shutil.which("ncu"),  # Nsight Compute
        "nsys": shutil.which("nsys"),  # Nsight Systems
        "nvprof": shutil.which("nvprof"),  # Legacy profiler
        "nvcc": shutil.which("nvcc"),  # CUDA compiler
    }
    return tools


def run_ncu_profile(kernel_path: Path, include_dirs: list[str] | None = None) -> dict:
    """Run Nsight Compute profiler on a kernel."""
    result = {
        "success": False,
        "metrics": {},
        "error": None,
        "raw_output": "",
    }

    # Compile the kernel first
    with tempfile.TemporaryDirectory() as tmpdir:
        exe_path = Path(tmpdir) / "kernel_test"

        # Build compile command
        compile_cmd = ["nvcc", "-o", str(exe_path), str(kernel_path)]
        if include_dirs:
            for d in include_dirs:
                compile_cmd.extend(["-I", d])

        try:
            compile_result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            if compile_result.returncode != 0:
                result["error"] = f"Compilation failed: {compile_result.stderr}"
                return result
        except Exception as e:
            result["error"] = f"Compilation error: {e}"
            return result

        # Run ncu profiler
        ncu_cmd = [
            "ncu",
            "--metrics", "sm__throughput.avg.pct_of_peak_sustained_elapsed,"
                        "dram__throughput.avg.pct_of_peak_sustained_elapsed,"
                        "gpu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed,"
                        "sm__warps_active.avg.pct_of_peak_sustained_active",
            "--csv",
            str(exe_path)
        ]

        try:
            ncu_result = subprocess.run(
                ncu_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            result["raw_output"] = ncu_result.stdout + ncu_result.stderr

            if ncu_result.returncode == 0:
                result["success"] = True
                # Parse CSV output
                lines = ncu_result.stdout.strip().split('\n')
                for line in lines:
                    if ',' in line and not line.startswith('"'):
                        parts = line.split(',')
                        if len(parts) >= 2:
                            metric_name = parts[0].strip().strip('"')
                            metric_value = parts[-1].strip().strip('"')
                            try:
                                result["metrics"][metric_name] = float(metric_value)
                            except ValueError:
                                result["metrics"][metric_name] = metric_value
            else:
                result["error"] = ncu_result.stderr or "ncu failed"

        except subprocess.TimeoutExpired:
            result["error"] = "Profiling timed out"
        except Exception as e:
            result["error"] = f"Profiling error: {e}"

    return result


def run_basic_analysis(kernel_path: Path) -> dict:
    """Run basic static analysis on a CUDA kernel."""
    result = {
        "success": True,
        "analysis": {},
    }

    content = kernel_path.read_text()

    # Count various CUDA constructs
    result["analysis"]["shared_memory"] = len(re.findall(r'__shared__', content))
    result["analysis"]["global_loads"] = len(re.findall(r'\[\s*\w+\s*\]', content))
    result["analysis"]["syncthreads"] = len(re.findall(r'__syncthreads\(\)', content))
    result["analysis"]["atomics"] = len(re.findall(r'atomic\w+\(', content))
    result["analysis"]["warps"] = len(re.findall(r'__shfl|__ballot|__any|__all', content))
    result["analysis"]["math_intrinsics"] = len(re.findall(r'__f\w+|__exp|__log|__sqrt|__rsqrt', content))
    result["analysis"]["tensor_cores"] = len(re.findall(r'wmma::|mma::', content))

    # Estimate register pressure
    float_vars = len(re.findall(r'\bfloat\s+\w+', content))
    int_vars = len(re.findall(r'\bint\s+\w+', content))
    result["analysis"]["estimated_registers"] = float_vars + int_vars

    return result


def execute_profile(
    code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Profile a CUDA kernel."""
    kwargs = kwargs or {}

    filepath = kwargs.get("file") or (args[0] if args else None)
    if not filepath and code:
        filepath = code.strip().split()[0]

    if not filepath:
        yield Message("system", "Error: No file path provided. Use: evo_profile kernel.cu")
        return

    path = Path(filepath).expanduser()
    if not path.exists():
        yield Message("system", f"Error: File not found: {path}")
        return

    # Check available tools
    tools = check_profiling_tools()

    lines = [f"**Kernel Profile: {path.name}**", ""]

    # Run static analysis (always available)
    analysis = run_basic_analysis(path)
    if analysis["success"]:
        lines.append("## Static Analysis")
        a = analysis["analysis"]
        lines.append(f"- Shared memory usage: {a['shared_memory']} declarations")
        lines.append(f"- Global memory accesses: ~{a['global_loads']} loads/stores")
        lines.append(f"- Synchronization points: {a['syncthreads']} __syncthreads()")
        lines.append(f"- Atomic operations: {a['atomics']}")
        lines.append(f"- Warp intrinsics: {a['warps']}")
        lines.append(f"- Math intrinsics: {a['math_intrinsics']}")
        lines.append(f"- Tensor core ops: {a['tensor_cores']}")
        lines.append(f"- Estimated register pressure: ~{a['estimated_registers']} vars")
        lines.append("")

    # Try runtime profiling if ncu available
    if tools["ncu"]:
        include_dirs_str = kwargs.get("include_dirs", "")
        include_dirs = [d.strip() for d in include_dirs_str.split(",") if d.strip()] if include_dirs_str else None

        lines.append("## Runtime Profile (ncu)")
        profile = run_ncu_profile(path, include_dirs)

        if profile["success"] and profile["metrics"]:
            for metric, value in profile["metrics"].items():
                if isinstance(value, float):
                    lines.append(f"- {metric}: {value:.1f}%")
                else:
                    lines.append(f"- {metric}: {value}")
        elif profile["error"]:
            lines.append(f"[dim]Could not run ncu: {profile['error']}[/dim]")
        lines.append("")
    else:
        lines.append("[dim]Note: Install Nsight Compute (ncu) for runtime profiling[/dim]")
        lines.append("")

    # Optimization suggestions
    lines.append("## Optimization Suggestions")
    a = analysis.get("analysis", {})

    if a.get("shared_memory", 0) == 0:
        lines.append("- Consider using shared memory for data reuse")
    if a.get("syncthreads", 0) > 5:
        lines.append("- Many sync points detected - consider reducing synchronization")
    if a.get("atomics", 0) > 0:
        lines.append("- Atomic operations detected - may cause contention")
    if a.get("tensor_cores", 0) == 0 and "matmul" in path.name.lower():
        lines.append("- Consider using Tensor Cores (wmma) for matrix ops")
    if a.get("warps", 0) == 0:
        lines.append("- No warp-level primitives - consider shuffle for reductions")

    yield Message("system", "\n".join(lines))


evo_profile = ToolSpec(
    name="evo_profile",
    desc="Profile a CUDA kernel to identify performance characteristics and hotspots",
    instructions="""Use this tool to analyze kernel performance before evolution.

It provides:
- Static analysis (always available): memory patterns, sync points, register pressure
- Runtime profiling (requires ncu): throughput, occupancy, memory bandwidth

Use the results to understand bottlenecks before running evolution.""",
    examples="""
### Profile a kernel

```evo_profile src/layernorm.cu
```

### Profile with include directories

```evo_profile
file: src/kernel.cu
include_dirs: ./include, ./third_party
```
""",
    execute=execute_profile,
    block_types=["evo_profile"],
    parameters=[
        Parameter(name="file", type="string", description="Path to CUDA kernel file", required=True),
        Parameter(name="include_dirs", type="string", description="Extra include directories (comma-separated)", required=False),
    ],
)
