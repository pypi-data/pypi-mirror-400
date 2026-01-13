"""Cost tracking for EvoKernel evolution runs."""

import json
from dataclasses import dataclass
from pathlib import Path

# GPU hourly rates (approximate Modal pricing in USD)
GPU_HOURLY_RATES = {
    "t4": 0.59,
    "l4": 0.80,
    "a10g": 1.10,
    "a100": 3.00,
    "a100-80gb": 4.00,
    "l40s": 1.40,
    "h100": 4.76,
    "h200": 6.00,
    "b200": 8.00,
}

# OpenRouter pricing per 1M tokens (approximate)
LLM_PRICING = {
    "input": 1.0,   # $1 per 1M input tokens (average)
    "output": 3.0,  # $3 per 1M output tokens (average)
}


@dataclass
class CostTracker:
    """Track costs for an evolution run."""
    
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    gpu_seconds: float = 0.0
    gpu_type: str = "a100"
    run_dir: Path | None = None
    
    def add_llm_usage(self, input_tokens: int, output_tokens: int):
        """Add LLM token usage."""
        self.llm_input_tokens += input_tokens
        self.llm_output_tokens += output_tokens
        self._save()
    
    def add_gpu_time(self, seconds: float):
        """Add GPU execution time."""
        self.gpu_seconds += seconds
        self._save()
    
    def estimate_cost(self) -> dict:
        """Estimate total cost breakdown."""
        llm_input_cost = (self.llm_input_tokens / 1_000_000) * LLM_PRICING["input"]
        llm_output_cost = (self.llm_output_tokens / 1_000_000) * LLM_PRICING["output"]
        llm_cost = llm_input_cost + llm_output_cost
        
        hourly_rate = GPU_HOURLY_RATES.get(self.gpu_type, GPU_HOURLY_RATES["a100"])
        gpu_cost = (self.gpu_seconds / 3600) * hourly_rate
        
        return {
            "llm_cost": llm_cost,
            "gpu_cost": gpu_cost,
            "total": llm_cost + gpu_cost,
            "llm_input_tokens": self.llm_input_tokens,
            "llm_output_tokens": self.llm_output_tokens,
            "gpu_seconds": self.gpu_seconds,
            "gpu_type": self.gpu_type,
        }
    
    def _save(self):
        """Save costs to file."""
        if self.run_dir:
            cost_path = self.run_dir / "costs.json"
            cost_path.write_text(json.dumps(self.estimate_cost(), indent=2))
    
    @classmethod
    def load(cls, run_dir: Path) -> "CostTracker":
        """Load cost tracker from run directory."""
        cost_path = run_dir / "costs.json"
        tracker = cls(run_dir=run_dir)
        
        if cost_path.exists():
            try:
                data = json.loads(cost_path.read_text())
                tracker.llm_input_tokens = data.get("llm_input_tokens", 0)
                tracker.llm_output_tokens = data.get("llm_output_tokens", 0)
                tracker.gpu_seconds = data.get("gpu_seconds", 0.0)
                tracker.gpu_type = data.get("gpu_type", "a100")
            except Exception:
                pass
        
        # Try to get GPU type from process info
        info_path = run_dir / "process_info.json"
        if info_path.exists():
            try:
                info = json.loads(info_path.read_text())
                if info.get("gpu_type"):
                    tracker.gpu_type = info["gpu_type"]
            except Exception:
                pass
        
        return tracker
