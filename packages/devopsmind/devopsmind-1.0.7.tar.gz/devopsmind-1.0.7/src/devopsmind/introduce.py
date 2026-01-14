import os
import platform
from datetime import datetime
from pathlib import Path

import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from devopsmind.constants import VERSION
from devopsmind.state import load_state

console = Console()

# -------------------------------------------------
# Relay endpoint
# -------------------------------------------------
# Default: official DevOpsMind relay
# Override allowed via env for dev/testing
INTRODUCE_URL = os.environ.get(
    "DEVOPSMIND_RELAY_URL",
    "https://devopsmind-relay.infraforgelabs.workers.dev/introduce",
)

# Local marker to prevent re-introduce
INTRODUCED_FLAG = Path.home() / ".devopsmind" / ".introduced"


def run_introduce():
    # -------------------------------------------------
    # Already introduced
    # -------------------------------------------------
    if INTRODUCED_FLAG.exists():
        console.print(
            Panel(
                Text(
                    "You’ve already introduced yourself.\n\nThank you ❤️",
                    style="green",
                ),
                title="Introduce",
                border_style="green",
            )
        )
        return

    # -------------------------------------------------
    # Explain clearly (explicit opt-in)
    # -------------------------------------------------
    console.print(
        Panel(
            Text(
                "DevOpsMind works fully offline by default.\n\n"
                "This command lets you optionally introduce yourself to the "
                "DevOpsMind community.\n\n"
                "No email. No password. No tracking.\n\n"
                "We will send:\n"
                "- your local username\n"
                "- your handle\n"
                "- app version & OS\n\n"
                "Proceed?",
                style="white",
            ),
            title="Introduce Yourself",
            border_style="cyan",
        )
    )

    answer = input("Continue? [y/N]: ").strip().lower()
    if answer != "y":
        console.print("❌ Cancelled.", style="dim")
        return

    # -------------------------------------------------
    # Load local profile
    # -------------------------------------------------
    state = load_state()
    profile = state.get("profile", {})

    payload = {
        "event": "offline_introduce",
        "tool": "devopsmind",
        "username": profile.get("username"),
        "handle": profile.get("gamer"),
        "version": VERSION,
        "os": platform.system().lower(),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    # -------------------------------------------------
    # Send (single explicit attempt)
    # -------------------------------------------------
    try:
        resp = requests.post(
            INTRODUCE_URL,
            json=payload,
            timeout=5,
        )
        resp.raise_for_status()
    except Exception as e:
        console.print(
            Panel(
                Text(
                    "Failed to send introduction.\n\n"
                    f"{e}",
                    style="red",
                ),
                title="Error",
                border_style="red",
            )
        )
        return

    # -------------------------------------------------
    # Mark locally (no retries)
    # -------------------------------------------------
    INTRODUCED_FLAG.parent.mkdir(parents=True, exist_ok=True)
    INTRODUCED_FLAG.write_text("1")

    console.print(
        Panel(
            Text(
                "Thank you for introducing yourself ❤️",
                style="bold green",
            ),
            title="Done",
            border_style="green",
        )
    )

