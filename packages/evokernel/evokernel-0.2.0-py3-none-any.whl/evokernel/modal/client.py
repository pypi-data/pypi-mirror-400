"""Client for calling the EvoKernel Modal endpoint."""

import modal


def evaluate_kernel(cuda_code: str, task: str = "layernorm", **kwargs) -> dict:
    """Evaluate a CUDA kernel using the Modal endpoint.
    
    Args:
        cuda_code: CUDA kernel source code
        task: Task name (layernorm, mnist_linear, etc.)
        **kwargs: Additional arguments passed to verify_kernel
    
    Returns:
        Dict with evaluation results
    """
    verify_fn = modal.Function.from_name("evokernel-verify", "verify_kernel")
    
    return verify_fn.remote(
        cuda_code=cuda_code,
        task=task,
        **kwargs,
    )


async def evaluate_kernel_async(cuda_code: str, task: str = "layernorm", **kwargs) -> dict:
    """Async version of evaluate_kernel."""
    verify_fn = modal.Function.from_name("evokernel-verify", "verify_kernel")
    
    return await verify_fn.remote.aio(
        cuda_code=cuda_code,
        task=task,
        **kwargs,
    )
