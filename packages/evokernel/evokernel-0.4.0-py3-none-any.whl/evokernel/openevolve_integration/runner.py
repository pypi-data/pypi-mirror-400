"""Spawn and manage OpenEvolve processes."""

import json
import os
import subprocess
import sys
from pathlib import Path


def detect_local_gpu() -> dict:
    """Detect local GPU hardware using nvidia-smi.

    Returns:
        Dict with gpu_available, gpu_name, cuda_version, memory_gb
    """
    result = {
        "gpu_available": False,
        "gpu_name": None,
        "cuda_version": None,
        "memory_gb": None,
        "compute_capability": None,
    }

    try:
        output = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,compute_cap",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if output.returncode == 0:
            line = output.stdout.strip().split("\n")[0]
            parts = [p.strip() for p in line.split(",")]
            result["gpu_available"] = True
            result["gpu_name"] = parts[0] if len(parts) > 0 else None
            result["memory_gb"] = float(parts[1]) / 1024 if len(parts) > 1 else None
            result["compute_capability"] = parts[2] if len(parts) > 2 else None

        cuda_output = subprocess.run(
            ["nvcc", "--version"], capture_output=True, text=True, timeout=10
        )
        if cuda_output.returncode == 0:
            import re

            match = re.search(r"release (\d+\.\d+)", cuda_output.stdout)
            if match:
                result["cuda_version"] = match.group(1)
    except Exception:
        pass

    return result


def spawn_openevolve(
    initial_program: Path,
    config_path: Path,
    output_dir: Path,
    task: str | None = "layernorm",
    evaluator_mode: str = "modal",
    include_dirs: list[str] | None = None,
    gpu_type: str = "a100",
) -> dict:
    """Spawn OpenEvolve as a subprocess.

    Args:
        initial_program: Path to initial CUDA kernel
        config_path: Path to config.yaml
        output_dir: Output directory for evolution
        task: Task name for the evaluator, or None for standalone mode
        evaluator_mode: "modal" (cloud GPU) or "local" (local GPU)
        include_dirs: Extra include directories for local mode
        gpu_type: GPU type for modal mode (a100, h100, etc.)

    Returns:
        Dict with process info (pid, etc.)
    """
    from evokernel.evaluators import get_evaluator

    evaluator_path = output_dir / "evaluator.py"
    standalone = task is None

    # Get evaluator and render template
    evaluator = get_evaluator(mode=evaluator_mode, standalone=standalone)

    # Common template parameters
    template_params = {
        "op_atol": 1e-3,
        "op_rtol": 1e-3,
        "warmup_time": 25,
        "rep_time": 100,
    }

    if evaluator_mode == "modal":
        template_params["gpu_type"] = gpu_type
        if not standalone:
            template_params["task"] = task
    else:
        template_params["include_dirs"] = include_dirs or []
        template_params["workspace_dir"] = str(Path.cwd())
        if not standalone:
            template_params["task"] = task

    evaluator.write_to(evaluator_path, **template_params)

    # Build command
    cmd = [
        sys.executable,
        "-m",
        "openevolve.cli",
        str(initial_program),
        str(evaluator_path),
        "--config",
        str(config_path),
        "--output",
        str(output_dir),
    ]

    env = os.environ.copy()
    if task is not None:
        env["EVOKERNEL_TASK"] = task

    log_file = output_dir / "openevolve.log"
    with open(log_file, "w") as log:
        process = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=str(output_dir),
        )

    info = {
        "pid": process.pid,
        "cmd": cmd,
        "log_file": str(log_file),
        "task": task,
        "standalone_mode": standalone,
        "evaluator_mode": evaluator_mode,
        "gpu_type": gpu_type if evaluator_mode == "modal" else None,
    }

    info_path = output_dir / "process_info.json"
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)

    return info


def get_evolution_status(run_dir: Path) -> dict:
    """Read evolution status from a run directory."""
    status = {
        "running": False,
        "completed": False,
        "iteration": 0,
        "max_iterations": 0,
        "best_score": 0.0,
        "best_speedup": 0.0,
        "programs_evaluated": 0,
    }

    info_path = run_dir / "process_info.json"
    if info_path.exists():
        with open(info_path) as f:
            info = json.load(f)

        pid = info.get("pid")
        if pid:
            try:
                os.kill(pid, 0)
                status["running"] = True
            except OSError:
                status["running"] = False

    best_path = run_dir / "best_program.cu"
    if best_path.exists():
        status["completed"] = True

    config_path = run_dir / "config.yaml"
    if config_path.exists():
        try:
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)
            status["max_iterations"] = config.get("max_iterations", 0)
        except Exception:
            pass

    checkpoint_dir = run_dir / "checkpoints"
    if checkpoint_dir.exists():
        checkpoints = sorted(checkpoint_dir.glob("checkpoint_*"))
        if checkpoints:
            latest_checkpoint = checkpoints[-1]

            best_info_path = latest_checkpoint / "best_program_info.json"
            if best_info_path.exists():
                try:
                    with open(best_info_path) as f:
                        best_info = json.load(f)
                    status["iteration"] = best_info.get("current_iteration", 0)
                    metrics = best_info.get("metrics", {})
                    status["best_score"] = metrics.get("combined_score", 0.0)
                    status["best_speedup"] = metrics.get("speedup", 0.0)
                    status["compile_success"] = metrics.get("compile_success", 0.0)
                    status["correct"] = metrics.get("correct", 0.0)
                except Exception:
                    pass

            elif (latest_checkpoint / "metadata.json").exists():
                try:
                    with open(latest_checkpoint / "metadata.json") as f:
                        meta = json.load(f)
                    status["iteration"] = meta.get("last_iteration", 0)
                except Exception:
                    pass

    log_path = run_dir / "openevolve.log"
    if log_path.exists():
        try:
            import re

            log_content = log_path.read_text()
            lines = log_content.strip().split("\n")

            max_iter = 0
            for line in lines:
                match = re.search(r"Iteration\s+(\d+):", line)
                if match:
                    max_iter = max(max_iter, int(match.group(1)))
            if max_iter > 0:
                status["iteration"] = max_iter

            for line in reversed(lines):
                if "New best program" in line:
                    match = re.search(r"combined_score:\s*[\d.]+\s*→\s*([\d.]+)", line)
                    if match:
                        status["best_score"] = float(match.group(1))
                        break

            best_idx = -1
            for i, line in enumerate(lines):
                if "New best solution found" in line:
                    best_idx = i

            if best_idx >= 0:
                for i in range(best_idx - 1, max(0, best_idx - 5), -1):
                    if "Metrics:" in lines[i]:
                        match = re.search(r"speedup=([\d.]+)", lines[i])
                        if match:
                            status["best_speedup"] = float(match.group(1))
                        match = re.search(r"combined_score=([\d.]+)", lines[i])
                        if match:
                            status["best_score"] = float(match.group(1))
                        break

            if status["best_speedup"] == 0.0:
                for line in lines:
                    if "Metrics:" in line:
                        match = re.search(r"speedup=([\d.]+)", line)
                        if match:
                            speedup = float(match.group(1))
                            if speedup > status["best_speedup"]:
                                status["best_speedup"] = speedup

            if "Error" in log_content or "Exception" in log_content:
                error_lines = [
                    line
                    for line in lines[-30:]
                    if "Error" in line or "Exception" in line or "Traceback" in line
                ]
                if error_lines:
                    status["error"] = error_lines[-1][:200]

            if "Evolution complete" in log_content:
                status["completed"] = True
                status["running"] = False

        except Exception:
            pass

    return status


def get_best_kernel_code(run_dir: Path) -> str | None:
    """Get the best kernel code from an evolution run."""
    best_path = run_dir / "best_program.cu"
    if best_path.exists():
        return best_path.read_text()

    checkpoint_dir = run_dir / "checkpoints"
    if checkpoint_dir.exists():
        checkpoints = sorted(checkpoint_dir.glob("checkpoint_*"))
        if checkpoints:
            latest_checkpoint = checkpoints[-1]
            meta_path = latest_checkpoint / "metadata.json"
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                    best_id = meta.get("best_program_id")
                    if best_id:
                        code_path = latest_checkpoint / "programs" / f"{best_id}.cu"
                        if code_path.exists():
                            return code_path.read_text()
                        if "programs" in meta and best_id in meta["programs"]:
                            return meta["programs"][best_id].get("code")
                except Exception:
                    pass

    return None
