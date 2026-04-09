"""OpenClaw integration for browser automation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    from .config import Settings

console = Console()


class OpenClawError(Exception):
    """Base exception for OpenClaw errors."""


class OpenClawNotInstalledError(OpenClawError):
    """Raised when OpenClaw is not installed."""


class OpenClawGatewayError(OpenClawError):
    """Raised when Gateway is not running or unhealthy."""


class RunMode(str, Enum):
    """Bot execution modes."""

    DRY_RUN = "dry_run"
    LIVE = "live"


@dataclass
class TaskResult:
    """Result of an OpenClaw task execution."""

    success: bool
    return_code: int
    message: str | None = None


def check_openclaw_installed() -> Path:
    """Check if OpenClaw is installed and return its path.

    Raises:
        OpenClawNotInstalledError: If OpenClaw is not found.
    """
    openclaw_path = shutil.which("openclaw")
    if not openclaw_path:
        raise OpenClawNotInstalledError(
            "OpenClaw is not installed. Install with: npm install -g openclaw@latest"
        )
    return Path(openclaw_path)


def check_gateway_health() -> bool:
    """Check if OpenClaw Gateway is healthy.

    Returns:
        True if gateway is healthy, False otherwise.
    """
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "--status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def setup_skill(skill_source: Path) -> Path:
    """Link skill to OpenClaw's skill directory.

    Args:
        skill_source: Path to the skill directory.

    Returns:
        Path to the linked skill in OpenClaw's workspace.
    """
    skill_name = skill_source.name
    skill_target = Path.home() / ".openclaw" / "workspace" / "skills" / skill_name

    # Ensure parent directory exists
    skill_target.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing link/directory if it exists
    if skill_target.is_symlink():
        skill_target.unlink()
    elif skill_target.exists():
        shutil.rmtree(skill_target)

    # Create symlink
    skill_target.symlink_to(skill_source.resolve())
    return skill_target


def update_openclaw_config(config_path: Path, settings: Settings) -> None:
    """Update OpenClaw configuration with current settings.

    Args:
        config_path: Path to openclaw.json
        settings: Application settings
    """
    config = {
        "agent": {
            "model": "google/gemini-2.0-flash",
        },
        "browser": {
            "enabled": True,
            "headless": settings.headless,
        },
        "agents": {
            "defaults": {
                "workspace": "./workspace",
            },
        },
    }

    config_path.write_text(json.dumps(config, indent=2))


def build_task_message(settings: Settings, mode: RunMode) -> str:
    """Build the task message for OpenClaw agent.

    Args:
        settings: Application settings
        mode: Execution mode (dry_run or live)

    Returns:
        Formatted task message string.
    """
    search_terms = " or ".join(f'"{term}"' for term in settings.search_terms)
    price_limit = f"€{settings.max_price_eur:.2f}"
    credentials = (
        f"email: {settings.amazon_nl_username} and "
        f"password: {settings.amazon_nl_password.get_secret_value()}"
    )

    base_instructions = f"""
Go to {settings.amazon_url}.
Accept any cookie consent dialogs.
Search for {search_terms}.
Find a product that meets ALL these criteria:
- Price is UNDER {price_limit} (including shipping if shown)
- Has at least {settings.min_rating} star rating (if visible)
- Is currently in stock
- Ships to Netherlands

Click on the product to view details.
Verify the total price is under {price_limit}.
Add it to cart.
Proceed to checkout.
Login with {credentials}.
Select the default delivery address or the first available option.
Choose the cheapest shipping option available.
"""

    if mode == RunMode.DRY_RUN:
        return f"""DRY RUN MODE - DO NOT COMPLETE THE PURCHASE.

{base_instructions}
Review the order summary.
STOP HERE - DO NOT click "Place Order" or any purchase confirmation button.

Report back:
1. Product name and description
2. Product price
3. Shipping cost
4. Total order cost
5. Estimated delivery date
6. Whether the total is under {price_limit}

DO NOT PROCEED WITH THE ACTUAL PURCHASE."""
    else:
        return f"""{base_instructions}
Review the order and confirm the total is under {price_limit}.
If total exceeds {price_limit}, STOP and report the issue.
If everything looks correct, place the order.

Report back:
1. Order confirmation number (if successful)
2. Product purchased
3. Total amount charged
4. Expected delivery date

STOP IMMEDIATELY if:
- Total exceeds {price_limit}
- SMS/email verification is required (report and wait)
- Any captcha or security check appears
- No suitable product is found
"""


def run_agent(
    message: str,
    config_path: Path,
    timeout: int | None = None,
) -> TaskResult:
    """Run OpenClaw agent with the given task.

    Args:
        message: Task message for the agent.
        config_path: Path to openclaw.json configuration.
        timeout: Optional timeout in seconds.

    Returns:
        TaskResult with execution outcome.
    """
    cmd = [
        "openclaw",
        "agent",
        "--message",
        message,
        "--config",
        str(config_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            timeout=timeout,
        )
        return TaskResult(
            success=result.returncode == 0,
            return_code=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return TaskResult(
            success=False,
            return_code=-1,
            message="Task timed out",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Task cancelled by user[/yellow]")
        sys.exit(130)
