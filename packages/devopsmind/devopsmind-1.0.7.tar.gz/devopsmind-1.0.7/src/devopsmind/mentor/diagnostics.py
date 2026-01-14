# mentor/diagnostics.py

from devopsmind.state import load_state
from devopsmind.mentor.stagnation import detect_stagnation


def run_mentor_diagnostics(table):
    """
    Adds mentor-related diagnostics to the Doctor table.
    This file NEVER prints directly.
    """

    state = load_state()
    mode = state.get("mode", "offline")

    # Mentor engine availability
    table.add_row(
        "Mentor system",
        "✅ Mentor engine is available",
    )

    # Mode info
    if mode == "offline":
        table.add_row(
            "Offline mode",
            "ℹ️ Running in offline mode",
        )
    else:
        table.add_row(
            "Offline mode",
            "ℹ️ Running in online mode",
        )

    # User progress presence
    completed = state.get("progress", {}).get("completed", [])
    table.add_row(
        "User progress",
        f"✅ {len(completed)} challenges completed",
    )

    # Stagnation detection
    stagnation = detect_stagnation()
    if stagnation:
        table.add_row(
            "Stagnation detected",
            f"⚠️ Repeated failures on {stagnation['challenge_id']}",
        )
    else:
        table.add_row(
            "Stagnation detected",
            "✅ No repeated failure patterns",
        )

    # Provider (informational only)
    table.add_row(
        "Mentor provider",
        "✅ Rule-based mentor would be used",
    )
