import time
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

from devopsmind.update_check import check_for_update
from devopsmind.state import load_state, save_state

console = Console()

# Show update notice once every 24 hours
CHECK_INTERVAL = 24 * 60 * 60  # seconds


def maybe_notify_update():
    """
    Display update notification if:
    - update exists
    - last check was more than 24 hours ago
    """

    state = load_state()
    now = time.time()

    last_checked = state.get("last_update_check", 0)
    if now - last_checked < CHECK_INTERVAL:
        return

    try:
        info = check_for_update()
    except Exception:
        # Never break CLI due to update check
        return

    # --------------------------------------------------
    # SUPPORT BOTH tuple AND dict RETURNS (IMPORTANT)
    # --------------------------------------------------

    if isinstance(info, tuple):
        # Expected: (has_update, latest_version, notes)
        try:
            has_update, latest, notes = info
        except ValueError:
            return

    elif isinstance(info, dict):
        has_update = info.get("has_update")
        latest = info.get("latest")
        notes = info.get("notes", "")

    else:
        return

    if not has_update:
        state["last_update_check"] = now
        save_state(state)
        return

    console.print(
        Panel(
            Text(
                f"⬆ Update available: v{latest}\n\n"
                f"{notes}\n\n"
                "Run `pipx upgrade devopsmind` to update.",
                style="bold",
            ),
            title="What's New",
            border_style="cyan",
        )
    )

    state["last_update_check"] = now
    save_state(state)
