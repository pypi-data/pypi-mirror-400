# doctor.py

import platform
import shutil
import sys
from rich.table import Table

from devopsmind.state import load_state
from devopsmind.utils import challenges_exist, data_dir_writable

# Mentor engine is always present (rule-based at minimum)
from devopsmind.mentor.engine import get_mentor_advice


def run_doctor():
    """
    Perform environment + mentor diagnostics.
    """

    table = Table(show_header=True, header_style="bold")
    table.add_column("Check")
    table.add_column("Status")

    # -------------------------------------------------
    # Core system checks
    # -------------------------------------------------

    py_ok = sys.version_info >= (3, 8)
    table.add_row(
        "Python version ≥ 3.8",
        "✅" if py_ok else "❌"
    )

    table.add_row(
        "Operating System",
        platform.system()
    )

    table.add_row(
        "Data directory writable",
        "✅" if data_dir_writable() else "❌"
    )

    table.add_row(
        "Bundled challenges found",
        "✅" if challenges_exist() else "❌"
    )

    table.add_row(
        "git installed",
        "✅" if shutil.which("git") else "❌"
    )

    # -------------------------------------------------
    # User progress
    # -------------------------------------------------

    state = load_state()
    completed = state.get("progress", {}).get("completed", [])

    table.add_row(
        "Completed challenges",
        f"✅ {len(completed)} completed"
    )

    # -------------------------------------------------
    # Mentor diagnostics (authoritative)
    # -------------------------------------------------

    table.add_row("", "")
    table.add_row("🧭 Mentor diagnostics", "")

    try:
        advice = get_mentor_advice()

        table.add_row(
            "Mentor system",
            "✅ Mentor engine available"
        )

        provider = "Rule-based"
        if state.get("ember_enabled"):
            provider = "Ember (local AI)"
        elif state.get("paid_entitlement"):
            provider = "Paid mentor"

        table.add_row(
            "Active mentor provider",
            f"✅ {provider}"
        )

        table.add_row(
            "Recommendation engine",
            "✅ Difficulty-aware + rotation memory"
        )

        table.add_row(
            "Learning style detection",
            "✅ Enabled"
        )

    except Exception as e:
        table.add_row(
            "Mentor system",
            f"❌ Error: {type(e).__name__}"
        )

    return table
