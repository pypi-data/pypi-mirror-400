"""Evaluator plugin system for EvoKernel."""

from .base import EvaluatorTemplate


class ModalTaskEvaluator(EvaluatorTemplate):
    """Modal cloud GPU evaluator with task-based correctness checking."""

    name = "modal_task"
    template_name = "modal_task.py.j2"


class ModalStandaloneEvaluator(EvaluatorTemplate):
    """Modal cloud GPU evaluator for standalone mode (no correctness check)."""

    name = "modal_standalone"
    template_name = "modal_standalone.py.j2"


class LocalTaskEvaluator(EvaluatorTemplate):
    """Local GPU evaluator with task-based correctness checking."""

    name = "local_task"
    template_name = "local_task.py.j2"


class LocalStandaloneEvaluator(EvaluatorTemplate):
    """Local GPU evaluator for standalone mode (no correctness check)."""

    name = "local_standalone"
    template_name = "local_standalone.py.j2"


# Registry mapping (mode, standalone) -> evaluator class
EVALUATORS = {
    ("modal", False): ModalTaskEvaluator,
    ("modal", True): ModalStandaloneEvaluator,
    ("local", False): LocalTaskEvaluator,
    ("local", True): LocalStandaloneEvaluator,
}


def get_evaluator(mode: str, standalone: bool) -> EvaluatorTemplate:
    """Get the appropriate evaluator template.

    Args:
        mode: "modal" for cloud GPU or "local" for local GPU
        standalone: True for standalone mode (no correctness check)

    Returns:
        Instantiated evaluator template
    """
    key = (mode, standalone)
    if key not in EVALUATORS:
        raise ValueError(f"Unknown evaluator: mode={mode}, standalone={standalone}")
    return EVALUATORS[key]()


__all__ = [
    "EvaluatorTemplate",
    "ModalTaskEvaluator",
    "ModalStandaloneEvaluator",
    "LocalTaskEvaluator",
    "LocalStandaloneEvaluator",
    "get_evaluator",
    "EVALUATORS",
]
