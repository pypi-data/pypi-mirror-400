"""EvoKernel dashboard - Live web UI for evolution monitoring."""

from .server import create_app, run_server

__all__ = ["create_app", "run_server"]
