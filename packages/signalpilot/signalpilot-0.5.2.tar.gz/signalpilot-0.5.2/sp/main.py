"""SignalPilot CLI - Simple init command"""

import subprocess
import sys
import urllib.request
from pathlib import Path

import typer
from rich.console import Console
from rich.tree import Tree

from sp.demos import start_demo_download

app = typer.Typer(
    name="sp",
    help="SignalPilot CLI - Bootstrap your data analysis workspace",
)

console = Console()

LOGO = """   ┌───┐
   │ ↗ │  ╔═╗┬┌─┐┌┐┌┌─┐┬  ╔═╗┬┬  ┌─┐┌┬┐
   │▓▓▓│  ╚═╗││ ┬│││├─┤│  ╠═╝││  │ │ │
   │▓░░│  ╚═╝┴└─┘┘└┘┴ ┴┴─┘╩  ┴┴─┘└─┘ ┴
   └───┘  Your Trusted CoPilot for Data Analysis"""


def check_uv() -> bool:
    """Check if uv is installed"""
    try:
        subprocess.run(
            ["uv", "--version"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_file(url: str, dest_path: Path):
    """Download a file from URL to destination path. Exits on failure."""
    try:
        console.print(f"  → Downloading {dest_path.name}...", style="dim")
        urllib.request.urlretrieve(url, dest_path)
    except Exception as e:
        console.print(f"  ✗ Failed to download {dest_path.name}: {e}", style="bold red")
        sys.exit(1)


def print_directory_tree(base_path: Path):
    """Print a nice directory structure"""
    tree = Tree(
        f"[bold cyan]{base_path.name}/[/bold cyan]",
        guide_style="dim"
    )

    # Add subdirectories
    tree.add("[cyan]user-skills/[/cyan]")
    tree.add("[cyan]user-rules/[/cyan]")
    tree.add("[cyan]team-workspace/[/cyan]")
    tree.add("[cyan]demo-project/[/cyan]")

    console.print(tree)


def optimize_jupyter_cache(home_dir: Path):
    """Warm up Jupyter to initialize caches for faster startup"""
    console.print("\n→ Optimizing Jupyter for fast startup...", style="bold cyan")
    console.print("  (This may take 30-40 seconds)\n", style="dim")

    try:
        venv_jupyter = home_dir / ".venv" / "bin" / "jupyter"

        # Disable announcements extension
        subprocess.run(
            [str(venv_jupyter), "labextension", "disable", "@jupyterlab/apputils-extension:announcements"],
            cwd=home_dir,
            capture_output=True,
            check=False,  # Don't fail if already disabled
        )

        # Lock announcements extension
        subprocess.run(
            [str(venv_jupyter), "labextension", "lock", "@jupyterlab/apputils-extension:announcements"],
            cwd=home_dir,
            capture_output=True,
            check=False,  # Don't fail if already locked
        )

        # Warm-up run: start Jupyter to initialize caches
        jupyter_process = subprocess.Popen(
            [str(venv_jupyter), "lab", "--no-browser", "--allow-root", "--port=19999"],
            cwd=home_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for Jupyter to be ready (up to 30 seconds)
        import time
        max_wait = 25
        jupyter_ready = False

        for i in range(max_wait):
            # Check if process is still running
            if jupyter_process.poll() is not None:
                console.print("  → Jupyter process exited early", style="yellow")
                break

            try:
                import urllib.request
                urllib.request.urlopen("http://localhost:19999/api", timeout=1)
                jupyter_ready = True
                console.print("  ✓ Jupyter cache initialized (100%)", style="green")
                break
            except Exception:
                progress = int((i + 1) / max_wait * 100)
                console.print(f"  → Warming up... {progress}%", style="dim", end="\r")
                time.sleep(1)

        if not jupyter_ready:
            console.print("  → Optimized Jupyter cache", style="yellow")

        # Shutdown Jupyter
        try:
            jupyter_process.terminate()
            jupyter_process.wait(timeout=5)
        except Exception:
            jupyter_process.kill()

    except Exception as e:
        console.print(f"  → Skipping optimization: {e}", style="yellow")
        # Don't fail the entire process if optimization fails


def run_init(dev: bool = False):
    """Main init logic"""
    # Check for uv
    console.print("→ Checking for uv...", style="dim")
    if not check_uv():
        console.print("✗ uv is not installed", style="bold red")
        console.print("\nPlease install uv first:", style="yellow")
        console.print("  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        console.print("  Windows:     powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        console.print("  Or via package manager: brew install uv")
        sys.exit(1)

    console.print("✓ uv found", style="green")

    # Create directory structure
    home_dir = Path.home() / "SignalPilotHome"
    console.print(f"\n→ Setting up workspace at [bold]{home_dir}[/bold]", style="dim")

    # Create main directory and subdirectories
    home_dir.mkdir(exist_ok=True)
    (home_dir / "user-skills").mkdir(exist_ok=True)
    (home_dir / "user-rules").mkdir(exist_ok=True)
    (home_dir / "team-workspace").mkdir(exist_ok=True)
    (home_dir / "demo-project").mkdir(exist_ok=True)

    console.print("\n✓ Directory structure created:", style="green")
    print_directory_tree(home_dir)

    # Check for existing pyproject.toml
    pyproject_path = home_dir / "pyproject.toml"
    download_pyproject = True

    if pyproject_path.exists():
        response = typer.prompt(
            "\npyproject.toml already exists. Overwrite? y/n",
            default="y",
            show_default=True,
        )
        download_pyproject = response.lower() in ["y", "yes"]

    # Download files from GitHub
    base_url = "https://raw.githubusercontent.com/SignalPilot-Labs/signalpilot-cli/refs/heads/main/defaultSignalPilotHome/"

    console.print("\n→ Downloading workspace files...", style="dim")

    # Always download start-here.ipynb
    download_file(base_url + "start-here.ipynb", home_dir / "start-here.ipynb")

    # Download pyproject.toml if approved
    if download_pyproject:
        if dev:
            console.print("  → Using dev configuration (signalpilot-ai-internal)", style="cyan")
            # Download dev-pyproject.toml but save as pyproject.toml
            download_file(base_url + "dev-pyproject.toml", pyproject_path)
        else:
            download_file(base_url + "pyproject.toml", pyproject_path)
    else:
        console.print("  → Keeping existing pyproject.toml", style="yellow")

    console.print("\n✓ Files downloaded successfully", style="green")

    # Download demo files in background (non-blocking)
    demo_dir = home_dir / "demo-project"
    demo_thread = None
    demo_result = []

    demo_thread, demo_result = start_demo_download(demo_dir)

    # Create venv with specific Python version
    console.print("\n→ Creating Python virtual environment...", style="bold cyan")
    console.print("  (Using Python 3.12)\n", style="dim")

    try:
        subprocess.run(
            ["uv", "venv", "--clear", "--seed", "--python", "3.12"],
            cwd=home_dir,
            check=True,
        )
        console.print("\n✓ Virtual environment created", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"\n✗ uv venv failed with exit code {e.returncode}", style="bold red")
        console.print("\nTry running manually:", style="yellow")
        console.print(f"  cd {home_dir}")
        console.print("  uv venv --seed --python 3.12")
        sys.exit(1)

    # Install dependencies using uv pip install
    console.print("\n→ Installing dependencies...", style="bold cyan")
    console.print("  (This may take a minute)\n", style="dim")

    try:
        # Don't capture output - show everything to the user
        subprocess.run(
            ["uv", "pip", "install", "-r", "pyproject.toml"],
            cwd=home_dir,
            check=True,
        )
        console.print("\n✓ Dependencies installed successfully", style="bold green")
    except subprocess.CalledProcessError as e:
        console.print(f"\n✗ uv pip install failed with exit code {e.returncode}", style="bold red")
        console.print("\nTry running manually:", style="yellow")
        console.print(f"  cd {home_dir}")
        console.print("  uv pip install -r pyproject.toml")
        sys.exit(1)

    # Optimize Jupyter cache
    optimize_jupyter_cache(home_dir)

    # Wait for demo downloads to complete and show result
    if demo_thread:
        console.print("\n→ Finalizing demo files...", style="dim")
        demo_thread.join(timeout=30)  # Wait up to 30 seconds
        if demo_result:
            local_count, downloaded_count = demo_result[0]
            total_count = local_count + downloaded_count
            if total_count > 0:
                console.print(f"✓ Demo files ready ({total_count} files)", style="green")
            else:
                console.print("→ Demo files unavailable", style="yellow")
        else:
            console.print("→ Demo files still downloading in background", style="yellow")

    # Get version information from the venv
    python_version = "unknown"
    try:
        result = subprocess.run(
            [str(home_dir / ".venv" / "bin" / "python"), "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Output is like "Python 3.12.7"
        python_version = result.stdout.strip().split()[1]
    except Exception:
        pass

    # Get SignalPilot version from installed packages
    sp_version = "unknown"
    package_name = "signalpilot-ai-internal" if dev else "signalpilot-ai"
    try:
        result = subprocess.run(
            [str(home_dir / ".venv" / "bin" / "pip"), "show", package_name],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.split("\n"):
            if line.startswith("Version:"):
                sp_version = line.split(":", 1)[1].strip()
                break
    except Exception:
        pass

    # Success message with logo and versions
    console.print("\n" + "="*60, style="white")
    console.print(LOGO, style="cyan")
    console.print("\n✓ SignalPilotHome created successfully!", style="bold green")
    console.print(f"  SignalPilot: v{sp_version} | Python: {python_version}", style="dim")
    console.print("="*60, style="white")

    console.print("\n[bold red]HOW TO START JUPYTER LAB[/bold red]")
    console.print("\n[bold cyan]Option 1: Easy way (anytime later)[/bold cyan]")
    console.print(f"[green]  → uvx signalpilot lab[/green]")

    console.print("\n[bold cyan]Option 2: Manual activation[/bold cyan]")
    console.print(f"[green]  → cd {home_dir} && source .venv/bin/activate[/green]")
    console.print(f"[green]  → jupyter lab[/green]")

    console.print("\n[bold cyan]Option 3: Start NOW! 👇[/bold cyan]")
    console.print("="*60 + "\n", style="white")

    # Ask if user wants to start Jupyter Lab now
    try:
        console.print("[bold yellow]Start SignalPilot in Jupyter Lab NOW? y/n[/bold yellow] ", end="")
        response = typer.prompt("", default="y", show_default=True)
        if response.lower() in ["y", "yes"]:
            console.print("\n" + "="*60, style="white")
            console.print(LOGO, style="cyan")
            console.print("\n→ Starting Jupyter Lab", style="bold green")
            console.print(f"  Workspace: {home_dir}", style="dim")
            console.print(f"  Environment: {home_dir / '.venv'}", style="dim")
            console.print("="*60 + "\n", style="white")

            venv_jupyter = home_dir / ".venv" / "bin" / "jupyter"
            subprocess.run(
                [str(venv_jupyter), "lab", "--IdentityProvider.token=''"],
                cwd=home_dir,
            )
    except (KeyboardInterrupt, EOFError):
        console.print("\n\n→ Setup complete! Run 'uvx signalpilot lab' when ready.\n", style="dim")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    dev: bool = typer.Option(False, "--dev", help="Use dev configuration (signalpilot-ai-internal)"),
):
    """SignalPilot CLI - Bootstrap your data analysis workspace"""
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
    run_init(dev=dev)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def lab(
    ctx: typer.Context,
    here: bool = typer.Option(False, "--here", help="Open in current folder with default .venv"),
    project: bool = typer.Option(False, "--project", help="Open in current folder with local .venv"),
):
    """Start Jupyter Lab in SignalPilotHome (pass extra args to jupyter lab)"""

    # Validate mutually exclusive flags
    if here and project:
        console.print("✗ Cannot use --here and --project together", style="bold red")
        sys.exit(1)

    # Determine workspace and venv based on flags
    if project:
        # Use current folder and local .venv
        workspace_dir = Path.cwd()
        venv_dir = workspace_dir / ".venv"

        if not venv_dir.exists():
            console.print("✗ No .venv found in current directory", style="bold red")
            console.print("\nCreate a virtual environment first:", style="yellow")
            console.print("  uv venv --seed --python 3.12", style="dim")
            console.print("  uv pip install jupyterlab signalpilot-ai", style="dim")
            sys.exit(1)

    elif here:
        # Use current folder but default .venv from SignalPilotHome
        workspace_dir = Path.cwd()
        home_dir = Path.home() / "SignalPilotHome"
        venv_dir = home_dir / ".venv"

        if not home_dir.exists():
            console.print("✗ SignalPilotHome not found", style="bold red")
            console.print("\nRun 'uvx signalpilot init' first to set up your workspace", style="yellow")
            sys.exit(1)

    else:
        # Default: Use SignalPilotHome for both workspace and venv
        home_dir = Path.home() / "SignalPilotHome"
        workspace_dir = home_dir
        venv_dir = home_dir / ".venv"

        if not home_dir.exists():
            console.print("✗ SignalPilotHome not found", style="bold red")
            console.print("\nRun 'uvx signalpilot init' first to set up your workspace", style="yellow")
            sys.exit(1)

    # Check if jupyter exists in the venv
    venv_jupyter = venv_dir / "bin" / "jupyter"
    if not venv_jupyter.exists():
        console.print("✗ Jupyter not found in virtual environment", style="bold red")
        if project or here:
            console.print("\nInstall Jupyter in the environment:", style="yellow")
            console.print("  uv pip install jupyterlab", style="dim")
        else:
            console.print("\nRun 'uvx signalpilot init' to set up your environment", style="yellow")
        sys.exit(1)

    # Show welcome message with logo
    console.print("\n" + "="*60, style="white")
    console.print(LOGO, style="cyan")
    console.print("\n→ Starting Jupyter Lab", style="bold green")
    console.print(f"  Workspace: {workspace_dir}", style="dim")
    console.print(f"  Environment: {venv_dir}", style="dim")
    if ctx.args:
        console.print(f"  Extra args: {' '.join(ctx.args)}", style="dim")
    console.print("="*60 + "\n", style="white")

    try:
        # Don't capture output - show everything to the user
        # Pass any extra arguments to jupyter lab
        # Start with null token by default (user args can override)
        subprocess.run(
            [str(venv_jupyter), "lab", "--IdentityProvider.token=''"] + list(ctx.args),
            cwd=workspace_dir,
        )
    except KeyboardInterrupt:
        console.print("\n\n→ Jupyter Lab stopped", style="dim")


if __name__ == "__main__":
    app()
