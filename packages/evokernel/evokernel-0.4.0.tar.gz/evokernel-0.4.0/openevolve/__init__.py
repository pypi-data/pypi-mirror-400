"""
OpenEvolve: An open-source implementation of AlphaEvolve
"""

from openevolve._version import __version__
from openevolve.api import (
    EvolutionResult,
    evolve_algorithm,
    evolve_code,
    evolve_function,
    run_evolution,
)
from openevolve.controller import OpenEvolve

__all__ = [
    "OpenEvolve",
    "__version__",
    "run_evolution",
    "evolve_function",
    "evolve_algorithm",
    "evolve_code",
    "EvolutionResult",
]
