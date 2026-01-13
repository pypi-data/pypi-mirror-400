"""Modal app for CUDA kernel verification with multi-GPU support.

Deploy with: modal deploy evokernel/modal/app.py
"""

import modal

# Image with CUDA and robust-kbench
image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.4.0-devel-ubuntu22.04",
        add_python="3.11",
    )
    .entrypoint([])
    .apt_install("git", "build-essential", "python3-dev", "ninja-build")
    .pip_install(
        "torch",
        "torchvision",
        "torchaudio",
        index_url="https://download.pytorch.org/whl/cu124",
    )
    .pip_install("numpy", "pydantic", "ninja", "dotmap", "backoff")
    .run_commands(
        "git clone https://github.com/SakanaAI/robust-kbench.git /app/robust-kbench",
        "cd /app/robust-kbench && pip install --no-deps -e .",
    )
    .env({
        "PYTHONPATH": "/app/robust-kbench:$PYTHONPATH",
        "TORCH_CUDA_ARCH_LIST": "7.5;8.0;8.6;9.0",
    })
    .pip_install("fastapi[standard]")
)

app = modal.App("evokernel-verify")


class KernelVerifierBase:
    """Base class with all verification logic."""
    
    def _verify_standalone(
        self,
        cuda_code: str,
        warmup_time: int = 25,
        rep_time: int = 100,
        baseline_time_ms: float | None = None,
    ) -> dict:
        """Standalone verification: compile and benchmark only."""
        import os
        import tempfile
        import time
        import traceback
        import uuid

        import numpy as np
        import torch
        from torch.utils.cpp_extension import load

        result = {
            "success": False,
            "compile_success": False,
            "correct": True,
            "standalone_mode": True,
            "speedup_vs_baseline": None,
            "cuda_timing": None,
            "error": None,
            "warning": "Standalone mode: correctness not verified.",
        }

        cuda_path = None

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cu', delete=False) as f:
                f.write(cuda_code)
                cuda_path = f.name

            try:
                module_name = f"kernel_{uuid.uuid4().hex[:8]}"
                cuda_module = load(
                    name=module_name,
                    sources=[cuda_path],
                    extra_cuda_cflags=["-O3", "--use_fast_math"],
                    verbose=False,
                )
                result["compile_success"] = True
            except Exception as e:
                result["error"] = f"Compilation failed: {str(e)}"
                return result

            if not hasattr(cuda_module, 'forward'):
                result["error"] = "Compiled module missing 'forward' function"
                return result

            cuda_fn = cuda_module.forward
            torch.cuda.synchronize()

            try:
                for _ in range(warmup_time):
                    try:
                        cuda_fn()
                    except TypeError:
                        result["error"] = "Standalone mode requires kernel to be callable without arguments"
                        return result
                torch.cuda.synchronize()
            except Exception as e:
                result["error"] = f"Warmup failed: {str(e)}"
                return result

            cuda_times = []
            for _ in range(rep_time):
                torch.cuda.synchronize()
                start = time.perf_counter()
                cuda_fn()
                torch.cuda.synchronize()
                cuda_times.append((time.perf_counter() - start) * 1000)

            cuda_mean = float(np.mean(cuda_times))
            cuda_std = float(np.std(cuda_times))

            result["cuda_timing"] = {"mean_ms": cuda_mean, "std_ms": cuda_std}

            if baseline_time_ms is not None and baseline_time_ms > 0:
                result["speedup_vs_baseline"] = baseline_time_ms / cuda_mean

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()

        finally:
            if cuda_path and os.path.exists(cuda_path):
                try:
                    os.unlink(cuda_path)
                except OSError:
                    pass

        return result

    def _verify_impl(
        self,
        cuda_code: str,
        task: str | None = "layernorm",
        forward: bool = True,
        op_atol: float = 1e-3,
        op_rtol: float = 1e-3,
        warmup_time: int = 25,
        rep_time: int = 100,
        baseline_time_ms: float | None = None,
    ) -> dict:
        """Core verification implementation."""
        import os
        import tempfile
        import time
        import traceback
        import uuid

        import numpy as np
        import torch
        from torch.utils.cpp_extension import load

        if task is None:
            return self._verify_standalone(
                cuda_code=cuda_code,
                warmup_time=warmup_time,
                rep_time=rep_time,
                baseline_time_ms=baseline_time_ms,
            )

        task_dir = f"/app/robust-kbench/tasks/{task}"

        result = {
            "success": False,
            "compile_success": False,
            "correct": False,
            "speedup_vs_torch": 0.0,
            "cuda_timing": None,
            "torch_timing": None,
            "error": None,
        }

        cuda_path = None

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cu', delete=False) as f:
                f.write(cuda_code)
                cuda_path = f.name

            from robust_kbench import KernelTask

            kernel_task = KernelTask(
                task_dir,
                multi_input_settings=False,
                multi_init_settings=False,
                forward=forward,
            )

            try:
                module_name = f"kernel_{uuid.uuid4().hex[:8]}"
                cuda_module = load(
                    name=module_name,
                    sources=[cuda_path],
                    extra_cuda_cflags=["-O3", "--use_fast_math"],
                    verbose=False,
                )
                result["compile_success"] = True
            except Exception as e:
                result["error"] = f"Compilation failed: {str(e)}"
                return result

            if not hasattr(cuda_module, 'forward'):
                result["error"] = "Compiled module missing 'forward' function"
                return result

            cuda_fn = cuda_module.forward

            init_configs = kernel_task.get_init_settings()
            input_configs = kernel_task.get_input_settings()

            Model = kernel_task.model
            get_inputs = kernel_task.get_inputs

            init_config = init_configs[0]
            input_config = input_configs[0]

            torch.manual_seed(42)
            torch.cuda.manual_seed(42)

            model = Model(**init_config).cuda()
            inputs = [x.cuda() for x in get_inputs(**input_config)]
            x = inputs[0]

            with torch.no_grad():
                ref_output = model(x)

                try:
                    cuda_output = model.forward(x, fn=cuda_fn)
                except Exception as e:
                    result["error"] = f"Execution failed: {str(e)}"
                    return result

                is_close = torch.allclose(cuda_output, ref_output, atol=op_atol, rtol=op_rtol)
                max_diff = float((cuda_output - ref_output).abs().max().item())

                result["correct"] = bool(is_close)
                result["max_diff"] = max_diff

                if not is_close:
                    result["error"] = f"Correctness check failed. Max diff: {max_diff}"
                    return result

            for _ in range(warmup_time):
                with torch.no_grad():
                    _ = model.forward(x, fn=cuda_fn)
            torch.cuda.synchronize()

            cuda_times = []
            for _ in range(rep_time):
                torch.cuda.synchronize()
                start = time.perf_counter()
                with torch.no_grad():
                    _ = model.forward(x, fn=cuda_fn)
                torch.cuda.synchronize()
                cuda_times.append((time.perf_counter() - start) * 1000)

            for _ in range(warmup_time):
                with torch.no_grad():
                    _ = model(x)
            torch.cuda.synchronize()

            torch_times = []
            for _ in range(rep_time):
                torch.cuda.synchronize()
                start = time.perf_counter()
                with torch.no_grad():
                    _ = model(x)
                torch.cuda.synchronize()
                torch_times.append((time.perf_counter() - start) * 1000)

            cuda_mean = float(np.mean(cuda_times))
            torch_mean = float(np.mean(torch_times))
            speedup = torch_mean / cuda_mean if cuda_mean > 0 else 0.0

            result["cuda_timing"] = {"mean_ms": cuda_mean, "std_ms": float(np.std(cuda_times))}
            result["torch_timing"] = {"mean_ms": torch_mean, "std_ms": float(np.std(torch_times))}
            result["speedup_vs_torch"] = speedup
            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()

        finally:
            if cuda_path and os.path.exists(cuda_path):
                try:
                    os.unlink(cuda_path)
                except OSError:
                    pass

        return result


# GPU-specific wrapper classes
@app.cls(image=image, gpu="T4", timeout=600)
class VerifierT4(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="L4", timeout=600)
class VerifierL4(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="A10G", timeout=600)
class VerifierA10G(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="A100", timeout=600)
class VerifierA100(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="A100-80GB", timeout=600)
class VerifierA100_80GB(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="L40S", timeout=600)
class VerifierL40S(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="H100", timeout=600)
class VerifierH100(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="H200", timeout=600)
class VerifierH200(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


@app.cls(image=image, gpu="B200", timeout=600)
class VerifierB200(KernelVerifierBase):
    @modal.method()
    def verify(self, **kwargs) -> dict:
        return self._verify_impl(**kwargs)


# Registry for GPU verifiers
GPU_VERIFIERS = {
    "t4": VerifierT4,
    "l4": VerifierL4,
    "a10g": VerifierA10G,
    "a100": VerifierA100,
    "a100-80gb": VerifierA100_80GB,
    "l40s": VerifierL40S,
    "h100": VerifierH100,
    "h200": VerifierH200,
    "b200": VerifierB200,
}
