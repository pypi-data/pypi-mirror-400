"""Mock utilities for testing upgrade system without network calls"""

import json
from unittest.mock import Mock, patch
from contextlib import contextmanager


# Mock PyPI JSON responses
MOCK_PYPI_RESPONSES = {
    "signalpilot": {
        "0.5.3": {
            "info": {"version": "0.5.3"},
        },
        "0.5.4": {
            "info": {"version": "0.5.4"},
        },
        "0.6.0": {
            "info": {"version": "0.6.0"},
        },
    },
    "signalpilot-ai": {
        "0.11.2": {
            "info": {"version": "0.11.2"},
        },
        "0.11.3": {
            "info": {"version": "0.11.3"},
        },
        "0.12.0": {
            "info": {"version": "0.12.0"},
        },
        "1.0.0": {
            "info": {"version": "1.0.0"},
        },
    },
    "signalpilot-ai-internal": {
        "0.11.7": {
            "info": {"version": "0.11.7"},
        },
        "0.11.8": {
            "info": {"version": "0.11.8"},
        },
        "0.12.0": {
            "info": {"version": "0.12.0"},
        },
        "1.0.0": {
            "info": {"version": "1.0.0"},
        },
    },
}


def mock_urlopen(url, timeout=None):
    """Mock urllib.request.urlopen for PyPI API calls"""
    # Extract package name from URL
    # URL format: https://pypi.org/pypi/{package_name}/json
    if "/pypi/" not in url:
        raise ValueError(f"Invalid PyPI URL: {url}")

    package_name = url.split("/pypi/")[1].replace("/json", "")

    # Get mock response for package
    if package_name not in MOCK_PYPI_RESPONSES:
        # Simulate 404 for unknown packages (like signalpilot-ai-internal on public PyPI)
        from urllib.error import HTTPError
        raise HTTPError(url, 404, "Not Found", {}, None)

    # Get latest version for package
    versions = MOCK_PYPI_RESPONSES[package_name]
    latest_version = max(versions.keys())
    response_data = versions[latest_version]

    # Create mock response object
    mock_response = Mock()
    mock_response.read.return_value = json.dumps(response_data).encode('utf-8')
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)

    return mock_response


@contextmanager
def mock_pypi_responses(package_versions: dict = None):
    """Context manager to mock PyPI responses.

    Args:
        package_versions: Optional dict to override versions
            Example: {"signalpilot": "0.5.4", "signalpilot-ai-internal": "0.11.8"}

    Usage:
        with mock_pypi_responses({"signalpilot": "0.5.4"}):
            version = get_pypi_version("signalpilot")
            # Returns "0.5.4" without network call
    """
    # Update mock responses if custom versions provided
    if package_versions:
        for package, version in package_versions.items():
            if package not in MOCK_PYPI_RESPONSES:
                MOCK_PYPI_RESPONSES[package] = {}
            MOCK_PYPI_RESPONSES[package][version] = {
                "info": {"version": version}
            }

    # Patch urllib.request.urlopen
    with patch('urllib.request.urlopen', side_effect=mock_urlopen):
        yield


@contextmanager
def mock_network_failure():
    """Context manager to simulate network failures.

    Usage:
        with mock_network_failure():
            version = get_pypi_version("signalpilot")
            # Returns None (network timeout)
    """
    from urllib.error import URLError

    def failing_urlopen(*args, **kwargs):
        raise URLError("Network unreachable")

    with patch('urllib.request.urlopen', side_effect=failing_urlopen):
        yield


def set_mock_version(package_name: str, version: str):
    """Set a specific version for a package in mock responses.

    Args:
        package_name: Package name (e.g., "signalpilot")
        version: Version string (e.g., "0.5.4")
    """
    if package_name not in MOCK_PYPI_RESPONSES:
        MOCK_PYPI_RESPONSES[package_name] = {}

    MOCK_PYPI_RESPONSES[package_name][version] = {
        "info": {"version": version}
    }
