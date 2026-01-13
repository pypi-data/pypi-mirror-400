"""EvoKernel CLI - CUDA kernel optimization agent."""

import logging
import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

sys.path.insert(0, str(Path(__file__).parent.parent))

from gptme.cli import main as gptme_main

from . import __version__
from .prompts import EVOKERNEL_SYSTEM_PROMPT

logging.getLogger("gptme").setLevel(logging.WARNING)

CONFIG_DIR = Path.home() / ".config" / "evokernel"
ENV_FILE = CONFIG_DIR / ".env"


def print_banner():
    console = Console()
    banner = Text()
    banner.append("  EvoKernel ", style="bold cyan")
    banner.append("v" + __version__, style="dim cyan")
    banner.append("\n")
    banner.append("  CUDA Kernel Optimization Agent\n", style="white")
    banner.append("  Powered by ", style="dim")
    banner.append("OpenEvolve", style="dim yellow")
    banner.append(" + ", style="dim")
    banner.append("Modal GPU", style="dim green")
    console.print(Panel(banner, border_style="cyan", padding=(0, 1)))
    console.print()


def register_evokernel_tools():
    current_modules = os.environ.get("TOOL_MODULES", "gptme.tools")
    if "evokernel.tools" not in current_modules:
        os.environ["TOOL_MODULES"] = f"{current_modules},evokernel.tools"


def check_setup():
    console = Console()
    if not ENV_FILE.exists():
        console.print("[yellow]EvoKernel is not set up yet.[/yellow]")
        console.print("Run [cyan]evokernel setup[/cyan] to configure your API key.\n")
        return False
    from dotenv import dotenv_values

    config = dotenv_values(ENV_FILE)
    if not config.get("OPENROUTER_API_KEY"):
        console.print("[yellow]OPENROUTER_API_KEY not found in config.[/yellow]")
        console.print("Run [cyan]evokernel setup[/cyan] to configure.\n")
        return False
    return True


def run_setup():
    console = Console()
    console.print(
        Panel.fit(
            "[bold cyan]EvoKernel Setup[/bold cyan]\n\n"
            "EvoKernel uses OpenRouter for LLM access during evolution.\n"
            "Get a free API key at: [link=https://openrouter.ai/]https://openrouter.ai/[/link]",
            border_style="cyan",
        )
    )
    console.print()
    existing_key = None
    if ENV_FILE.exists():
        from dotenv import dotenv_values

        config = dotenv_values(ENV_FILE)
        existing_key = config.get("OPENROUTER_API_KEY")
        if existing_key:
            masked = existing_key[:8] + "..." + existing_key[-4:]
            console.print(f"Current key: [dim]{masked}[/dim]\n")
    key = click.prompt(
        "Enter your OpenRouter API key",
        default=existing_key or "",
        hide_input=False,
        show_default=False,
    )
    if not key:
        console.print("[red]No key provided. Setup cancelled.[/red]")
        return
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(f"OPENROUTER_API_KEY={key}\n")
    console.print(f"\n[green]OK[/green] API key saved to [cyan]{ENV_FILE}[/cyan]")
    console.print(
        "\nYou're all set! Run [cyan]evokernel[/cyan] to start optimizing kernels."
    )


@click.command()
@click.version_option(__version__, prog_name="evokernel")
@click.option("-m", "--model", default=None, help="Model to use")
@click.option("-w", "--workspace", default=".", help="Workspace directory")
@click.option("-r", "--resume", is_flag=True, help="Resume last conversation")
@click.option("-y", "--no-confirm", is_flag=True, help="Skip confirmations")
@click.option("-n", "--name", default="random", help="Conversation name")
@click.argument("prompts", nargs=-1)
def main(prompts, model, workspace, resume, no_confirm, name):
    """EvoKernel - CUDA kernel optimization agent.

    \b
    Examples:
        evokernel                         # start interactive session
        evokernel "optimize my kernel"    # start with initial prompt
        evokernel setup                   # configure API key
        evokernel -r                      # resume last conversation

    \b
    In the chat, you can use:
        @file.cu                       # include file contents
        /dashboard                     # open evolution dashboard
        /help                          # show commands
    """
    if prompts and prompts[0] == "setup":
        run_setup()
        return

    print_banner()

    if not check_setup():
        return

    register_evokernel_tools()

    args = ["--system", EVOKERNEL_SYSTEM_PROMPT]

    # Enable gptme's interactive choice and form tools for task selection
    args.extend(["-t", "+choice", "-t", "+form"])

    if model:
        args.extend(["-m", model])
    if workspace:
        args.extend(["-w", workspace])
    if resume:
        args.append("-r")
    if no_confirm:
        args.append("-y")
    if name != "random":
        args.extend(["--name", name])

    args.extend(prompts)

    sys.argv = ["evokernel"] + args
    gptme_main(standalone_mode=False)


if __name__ == "__main__":
    main()
