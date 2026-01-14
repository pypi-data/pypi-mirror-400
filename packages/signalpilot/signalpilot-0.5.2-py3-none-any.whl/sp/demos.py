"""Download demo notebooks and data files"""

import json
import threading
import urllib.parse
import urllib.request
from pathlib import Path

from rich.console import Console

console = Console()


def download_demo_files_background(demo_dir: Path, result_container: list):
    """Wrapper to download demo files in background thread and store result."""
    local_count, downloaded_count = download_demo_files(demo_dir)
    result_container.append((local_count, downloaded_count))


def start_demo_download(demo_dir: Path) -> tuple[threading.Thread, list]:
    """Start background download of demo files.

    Returns:
        tuple[threading.Thread, list]: (thread, result_container)
    """
    result_container = []
    thread = threading.Thread(
        target=download_demo_files_background,
        args=(demo_dir, result_container),
        daemon=True
    )
    thread.start()
    return thread, result_container


def get_remote_files(repo_path: str) -> list[str]:
    """Get list of files from GitHub repository path."""
    api_url = f"https://api.github.com/repos/SignalPilot-Labs/signalpilot-demos/contents/{repo_path}"

    try:
        with urllib.request.urlopen(api_url) as response:
            contents = json.loads(response.read())

        files = []
        for item in contents:
            if item["type"] == "file":
                # Return relative path from repo root
                files.append(f"{repo_path}/{item['name']}")
            elif item["type"] == "dir":
                # Recursively get files from subdirectories
                subfiles = get_remote_files(f"{repo_path}/{item['name']}")
                files.extend(subfiles)

        return files
    except Exception:
        # If we can't fetch, return empty list
        return []


def get_local_files(demo_dir: Path) -> set[str]:
    """Get set of relative file paths (as they appear in remote repo) that exist locally."""
    if not demo_dir.exists():
        return set()

    local_files = set()

    # Check for notebooks (stored directly in demo_dir, map to notebooks/ path)
    for notebook in demo_dir.glob("*.ipynb"):
        local_files.add(f"notebooks/{notebook.name}")

    # Check for data files (stored in data/ subdirectory)
    data_dir = demo_dir / "data"
    if data_dir.exists():
        for file in data_dir.rglob("*"):
            if file.is_file():
                # Get relative path from demo_dir (includes data/)
                rel_path = file.relative_to(demo_dir)
                local_files.add(str(rel_path))

    return local_files


def download_demo_files(demo_dir: Path) -> tuple[int, int]:
    """Download demo notebooks and data files that don't exist locally.

    Returns:
        tuple[int, int]: (local_files_count, downloaded_files_count)
    """
    base_url = "https://raw.githubusercontent.com/SignalPilot-Labs/signalpilot-demos/main"

    # Get remote file lists from GitHub API
    remote_notebooks = get_remote_files("notebooks")
    remote_data = get_remote_files("data")
    all_remote_files = remote_notebooks + remote_data

    # Get local file list
    local_files = get_local_files(demo_dir)
    local_count = len(local_files)

    # Filter to only files that don't exist locally
    files_to_download = [f for f in all_remote_files if f not in local_files]

    if not files_to_download:
        return (local_count, 0)  # All files already present

    # Create data directory
    data_dir = demo_dir / "data"
    data_dir.mkdir(exist_ok=True, parents=True)

    downloaded_count = 0

    for file_path in files_to_download:
        try:
            # URL-encode the file path to handle spaces and special characters
            encoded_path = urllib.parse.quote(file_path)
            url = f"{base_url}/{encoded_path}"

            # Determine destination path
            if file_path.startswith("notebooks/"):
                dest = demo_dir / Path(file_path).name
            else:
                # For data files, preserve the data/ directory structure
                dest = demo_dir / file_path

            dest.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, dest)
            downloaded_count += 1
        except Exception:
            # Silently continue if download fails
            pass

    return (local_count, downloaded_count)
