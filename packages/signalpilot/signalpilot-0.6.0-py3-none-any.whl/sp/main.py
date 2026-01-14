"""SignalPilot CLI - Main entry point"""

import typer

from sp.commands.init import init_command, run_init
from sp.commands.lab import lab_command, home_command
from sp.commands.upgrade import upgrade_command

app = typer.Typer(
    name="sp",
    help="SignalPilot CLI - Bootstrap your data analysis workspace",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    dev: bool = typer.Option(False, "--dev", help="Use dev configuration (signalpilot-ai-internal)"),
):
    """SignalPilot CLI - Bootstrap your data analysis workspace.

    Run without arguments to initialize SignalPilotHome.
    """
    # If a subcommand was invoked, don't run init
    if ctx.invoked_subcommand is not None:
        return

    # Run init by default
    run_init(dev=dev)


@app.command()
def init(
    dev: bool = typer.Option(False, "--dev", help="Use dev configuration (signalpilot-ai-internal)"),
):
    """Initialize SignalPilot workspace at ~/SignalPilotHome"""
    init_command(dev=dev)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def lab(
    ctx: typer.Context,
    home: bool = typer.Option(False, "--home", help="Use SignalPilotHome workspace + venv"),
    project: bool = typer.Option(False, "--project", help="Use current folder + local .venv (fail if missing)"),
):
    """Start Jupyter Lab (default: current folder + home .venv)"""
    lab_command(ctx, home=home, project=project)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def home(ctx: typer.Context):
    """Start Jupyter Lab in SignalPilotHome (shortcut for 'lab --home')"""
    home_command(ctx)


@app.command()
def upgrade(
    project: bool = typer.Option(False, "--project", help="Upgrade project .venv instead of home"),
):
    """Upgrade SignalPilot CLI and library"""
    upgrade_command(project=project)


if __name__ == "__main__":
    app()
