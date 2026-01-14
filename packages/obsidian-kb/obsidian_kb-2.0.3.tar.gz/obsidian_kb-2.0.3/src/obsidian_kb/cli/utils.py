"""Shared CLI utilities."""

import logging
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from obsidian_kb.service_container import ServiceContainer, get_service_container

console = Console()
logger = logging.getLogger(__name__)

# Service container singleton
_services: ServiceContainer | None = None


def get_services() -> ServiceContainer:
    """Get the service container instance."""
    global _services
    if _services is None:
        _services = get_service_container()
    return _services


# Constants for service management
PLIST_NAME = "com.obsidian-kb.plist"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"

# Constants for Claude Desktop
CLAUDE_CONFIG_DIR = Path.home() / "Library" / "Application Support" / "Claude"
CLAUDE_CONFIG_FILE = CLAUDE_CONFIG_DIR / "claude_desktop_config.json"


# plist templates
PLIST_TEMPLATE_DEV = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.obsidian-kb</string>

    <key>ProgramArguments</key>
    <array>
        <string>{uv_path}</string>
        <string>run</string>
        <string>--project</string>
        <string>{project_root}</string>
        <string>python</string>
        <string>-m</string>
        <string>obsidian_kb.mcp_server</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{project_root}</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/obsidian-kb.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/obsidian-kb.error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{home_dir}/.local/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>OBSIDIAN_KB_DB_PATH</key>
        <string>{home_dir}/.obsidian-kb/lancedb</string>
    </dict>

    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
"""

PLIST_TEMPLATE_INSTALLED = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.obsidian-kb</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>-m</string>
        <string>obsidian_kb.mcp_server</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{home_dir}</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/obsidian-kb.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/obsidian-kb.error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{home_dir}/.local/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>OBSIDIAN_KB_DB_PATH</key>
        <string>{home_dir}/.obsidian-kb/lancedb</string>
    </dict>

    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
"""


def get_uv_path() -> str:
    """Find path to uv."""
    candidates = [
        Path.home() / ".local" / "bin" / "uv",
        Path.home() / ".cargo" / "bin" / "uv",
        Path("/usr/local/bin/uv"),
        Path("/opt/homebrew/bin/uv"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)

    result = subprocess.run(["which", "uv"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()

    raise RuntimeError("uv не найден. Установите: curl -LsSf https://astral.sh/uv/install.sh | sh")


def get_python_path() -> str:
    """Find path to Python interpreter used to run obsidian-kb."""
    python_path = sys.executable

    if Path(python_path).exists():
        return python_path

    candidates = [
        Path("/usr/local/bin/python3"),
        Path("/opt/homebrew/bin/python3"),
        Path("/usr/bin/python3"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)

    result = subprocess.run(["which", "python3"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()

    return python_path


def find_project_root(start_path: Path | None = None) -> Path | None:
    """Find project root by looking for pyproject.toml upward."""
    if start_path is None:
        start_path = Path.cwd()

    current = Path(start_path).resolve()

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            try:
                import tomllib
                with open(current / "pyproject.toml", "rb") as f:
                    data = tomllib.load(f)
                    if data.get("project", {}).get("name") == "obsidian-kb":
                        return current
            except Exception:
                if (current / "src" / "obsidian_kb").exists():
                    return current
        current = current.parent

    return None


def find_project_in_common_locations() -> Path | None:
    """Search for obsidian-kb project in common locations."""
    home = Path.home()
    common_locations = [
        home / "CursorProjects" / "obsidian-kb",
        home / "Projects" / "obsidian-kb",
        home / "Development" / "obsidian-kb",
        home / "dev" / "obsidian-kb",
        home / "code" / "obsidian-kb",
        home / "workspace" / "obsidian-kb",
        Path("/opt") / "obsidian-kb",
        Path("/usr/local") / "obsidian-kb",
    ]

    for location in common_locations:
        if location.exists() and (location / "pyproject.toml").exists():
            try:
                import tomllib
                with open(location / "pyproject.toml", "rb") as f:
                    data = tomllib.load(f)
                    if data.get("project", {}).get("name") == "obsidian-kb":
                        return location
            except Exception:
                if (location / "src" / "obsidian_kb").exists():
                    return location

    return None


def is_development_mode() -> bool:
    """Check if package is running in development mode."""
    package_path = Path(__file__).parent.parent.parent
    if (package_path / "pyproject.toml").exists():
        try:
            import tomllib
            with open(package_path / "pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                if data.get("project", {}).get("name") == "obsidian-kb":
                    if (package_path / "src" / "obsidian_kb").exists():
                        return True
        except Exception:
            if (package_path / "src" / "obsidian_kb").exists():
                return True

    return False


def find_plist_file_and_project() -> tuple[str, Path | None, bool]:
    """Find plist file and determine project root.

    Returns:
        tuple[str, Path | None, bool]: (plist content, project root or None, is_dev_mode)
    """
    project_root_dev = Path(__file__).parent.parent.parent
    plist_dev = project_root_dev / "scripts" / PLIST_NAME
    if plist_dev.exists() and (project_root_dev / "pyproject.toml").exists():
        return plist_dev.read_text(encoding="utf-8"), project_root_dev, True

    cwd = Path.cwd()
    plist_cwd = cwd / "scripts" / PLIST_NAME
    if plist_cwd.exists() and (cwd / "pyproject.toml").exists():
        return plist_cwd.read_text(encoding="utf-8"), cwd, True

    is_dev = is_development_mode()

    if is_dev:
        project_root = find_project_root(cwd)
        if project_root:
            return PLIST_TEMPLATE_DEV, project_root, True

        package_path = Path(__file__).parent.parent.parent
        if (package_path / "pyproject.toml").exists():
            try:
                import tomllib
                with open(package_path / "pyproject.toml", "rb") as f:
                    data = tomllib.load(f)
                    if data.get("project", {}).get("name") == "obsidian-kb":
                        if (package_path / "src" / "obsidian_kb").exists():
                            return PLIST_TEMPLATE_DEV, package_path, True
            except Exception:
                if (package_path / "src" / "obsidian_kb").exists():
                    return PLIST_TEMPLATE_DEV, package_path, True

        project_root = find_project_in_common_locations()
        if project_root:
            return PLIST_TEMPLATE_DEV, project_root, True

        env_project = os.environ.get("OBSIDIAN_KB_PROJECT_ROOT")
        if env_project:
            env_path = Path(env_project)
            if env_path.exists() and (env_path / "pyproject.toml").exists():
                return PLIST_TEMPLATE_DEV, env_path, True

    return PLIST_TEMPLATE_INSTALLED, None, False
