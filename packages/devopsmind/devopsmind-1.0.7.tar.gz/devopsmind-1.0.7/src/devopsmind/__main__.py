import argparse
import sys
import shutil
from pathlib import Path
from rich.console import Console, Group
from rich.text import Text
from rich.panel import Panel

from devopsmind.first_run import ensure_first_run
from devopsmind.state import (
    load_state,
    reset_session,
)
from devopsmind.mode import set_mode_online, set_mode_offline

from .cli import frame
from .engine import play, validate_only, stats as render_stats
from .list import list_challenges, search_challenges
from .profiles import show_profile, list_profiles
from .hint import show_hint
from .describe import describe_challenge
from .doctor import run_doctor
from .leaderboard import show_leaderboards
from .sync import sync_default
from .submit import submit_pending
from .constants import XP_LEVELS, VERSION
from devopsmind.stacks import show_my_stack_progress
from devopsmind.ui import show_validation_result
from .stats import stats as load_stats
from devopsmind.achievements import list_badges
from devopsmind.introduce import run_introduce
from devopsmind.update_notify import maybe_notify_update

# 🧭 Mentor
from devopsmind.mentor.mentor import run_mentor

# 🔐 Auth
from devopsmind.auth_recovery import rotate_recovery_key

# 📖 Help
from devopsmind.help import show_help

console = Console()


# -------------------------------------------------
# 🔥 Logout purge helper (ADDITIVE)
# -------------------------------------------------

def confirm_and_purge_local_state():
    """
    Warn user and delete ~/.devopsmind across OSes.
    """
    devopsmind_dir = Path.home() / ".devopsmind"

    if not devopsmind_dir.exists():
        return True

    console.print(
        Panel(
            Text(
                "⚠️ You are about to log out.\n\n"
                "This will DELETE all local DevOpsMind data:\n\n"
                f"  {devopsmind_dir}\n\n"
                "Including:\n"
                "- progress\n"
                "- XP\n"
                "- achievements\n"
                "- offline state\n\n"
                "You may back up this directory before continuing.\n",
                style="yellow",
            ),
            title="Logout Warning",
            border_style="yellow",
        )
    )

    answer = input("Continue? [y/N]: ").strip().lower()
    if answer != "y":
        console.print("❌ Logout cancelled.", style="dim")
        return False

    try:
        shutil.rmtree(devopsmind_dir)
        console.print("🗑️ Local DevOpsMind data removed.", style="green")
        return True
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to delete {devopsmind_dir}\n\n{e}", style="red"),
                title="Logout Error",
                border_style="red",
            )
        )
        return False


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def compute_rank(xp: int) -> str:
    rank = XP_LEVELS[0][1]
    for threshold, name in XP_LEVELS:
        if xp >= threshold:
            rank = name
    return rank


def profile_bar():
    state = load_stats()
    profile = state.get("profile", {})
    xp = state.get("xp", 0)

    mode = state.get("mode", "offline")
    mode_label = "🌐 ONLINE" if mode == "online" else "📴 OFFLINE"
    mode_style = "green" if mode == "online" else "dim"

    text = (
        f"🎮 {profile.get('gamer', '—')} · "
        f"👤 {profile.get('username', '—')} · "
        f"🏅 {compute_rank(xp)} · "
        f"🧠 XP {xp} · "
        f"{mode_label}"
    )

    return Text(text, style=mode_style)


def boxed(title: str, body):
    return frame(
        title,
        Group(profile_bar(), Text(""), body),
    )


def welcome_screen():
    return Group(
        Text(f"DevOpsMind v{VERSION}", style="bold green"),
        Text(""),
        Text("Get started:", style="bold"),
        Text("• introduce        → optionally introduce yourself"),
        Text("• mentor           → guided next-step suggestions"),
        Text("• play <id>        → start a challenge"),
        Text("• search <term>    → find challenges"),
        Text("• stacks           → view stack progress"),
        Text("• profile show     → view your profile"),
        Text("• stats            → view XP and progress"),
        Text("• doctor           → diagnose setup issues"),
        Text(""),
        Text("Tip: DevOpsMind works fully offline by default.", style="dim"),
    )


def cancelled():
    console.print(
        Panel(
            Text("❌ Command cancelled", style="red"),
            title="Cancelled",
            border_style="red",
        )
    )
    sys.exit(0)


def resolve_badge_line(line: str) -> str:
    if "ach_" not in line:
        return line

    try:
        badges = list_badges(raw=True)
        badge_map = {b["id"]: b for b in badges}

        for badge_id, meta in badge_map.items():
            if badge_id in line:
                return f"{meta.get('icon','🏅')} New badge unlocked: {meta.get('name', badge_id)}"
    except Exception:
        pass

    return line


# -------------------------------------------------
# Main
# -------------------------------------------------

def main():
    try:
        cmd = sys.argv[1] if len(sys.argv) > 1 else ""

        if not (len(sys.argv) >= 2 and sys.argv[1] == "login"):
            ensure_first_run()

        if cmd == "login":
            ensure_first_run(force=True)
            return

        # ---------------- ARGPARSE ----------------

        parser = argparse.ArgumentParser(prog="devopsmind", add_help=False)
        parser.add_argument("--help", action="store_true")
        parser.add_argument("--version", action="store_true")
        parser.add_argument("--stack", help="Filter by stack")
        sub = parser.add_subparsers(dest="cmd")

        # Core commands
        for c in [
            "introduce",
            "mentor",
            "auth",
            "logout",
            "stats",
            "leaderboard",
            "doctor",
            "badges",
            "submit",
            "sync",
            "stacks",
            "my-stacks",
            "mode",
        ]:
            sub.add_parser(c)

        sub.add_parser("play").add_argument("id")
        sub.add_parser("validate").add_argument("id")
        sub.add_parser("describe").add_argument("id")
        sub.add_parser("hint").add_argument("id")
        sub.add_parser("search").add_argument("term")

        # Profile
        p_profile = sub.add_parser("profile")
        profile_sub = p_profile.add_subparsers(dest="action", required=True)
        profile_sub.add_parser("show")
        profile_sub.add_parser("list")

        # Mode
        p_mode = sub.choices["mode"]
        mode_sub = p_mode.add_subparsers(dest="action", required=True)
        mode_sub.add_parser("online")
        mode_sub.add_parser("offline")

        # Auth
        p_auth = sub.choices["auth"]
        auth_sub = p_auth.add_subparsers(dest="action", required=True)
        auth_sub.add_parser("rotate-recovery")

        args = parser.parse_args()

        # ---------------- UPDATE NOTIFICATION (THROTTLED) ----------------

        UPDATE_AWARE_COMMANDS = {
            "",             # devopsmind
            "stacks",
            "my-stacks",
            "stats",
            "profile",
            "doctor",
        }

        cmd_name = args.cmd or ""

        if cmd_name in UPDATE_AWARE_COMMANDS:
            maybe_notify_update()

        # ---------------- HELP / VERSION ----------------

        if args.help:
            show_help()
            return

        if args.version:
            console.print(
                boxed("ℹ️ Version", Text(f"DevOpsMind v{VERSION}", style="bold green"))
            )
            return

        if args.stack:
            console.print(
                boxed(f"📦 Stack · {args.stack}", list_challenges(stack=args.stack))
            )
            return

        if not args.cmd:
            console.print(boxed("👋 Welcome to DevOpsMind", welcome_screen()))
            return

        # ---------------- MODE ----------------

        if args.cmd == "mode":
            if args.action == "online":
                set_mode_online()
            elif args.action == "offline":
                set_mode_offline()
            return

        # ---------------- INTRODUCE ----------------

        if args.cmd == "introduce":
            run_introduce()
            return

        # ---------------- MENTOR ----------------

        if args.cmd == "mentor":
            run_mentor()
            return

        # ---------------- AUTH ----------------

        if args.cmd == "auth":
            if args.action == "rotate-recovery":
                rotate_recovery_key()
            return

        # ---------------- LOGOUT ----------------

        if args.cmd == "logout":
            if confirm_and_purge_local_state():
                console.print(
                    Panel(
                        Text(
                            "You have been logged out.\n\n"
                            "All local DevOpsMind data has been removed.\n"
                            "Run `devopsmind login` to start fresh.",
                            style="green",
                        ),
                        title="Logged Out",
                        border_style="green",
                    )
                )
            return

        # ---------------- VALIDATE ----------------

        if args.cmd == "validate":
            result = validate_only(args.id)

            if isinstance(result, dict) and result.get("error"):
                body = [Text(result["error"], style="red")]

                attempts = result.get("attempts")
                limit = result.get("fail_limit")
                if attempts and limit:
                    body.append(Text(f"\nAttempts: {attempts}/{limit}", style="yellow"))

                if result.get("auto_hint"):
                    hint = result["auto_hint"]
                    body.append(
                        hint if isinstance(hint, Text) else Text(hint, style="cyan")
                    )

                console.print(boxed("❌ Validation Failed", Group(*body)))
                return

            console.print(
                boxed(
                    f"🧪 Validate · {args.id}",
                    show_validation_result(**result),
                )
            )
            return

        # ---------------- OTHER COMMANDS ----------------

        if args.cmd == "play":
            console.print(boxed(f"🎮 Play · {args.id}", play(args.id)))
            return

        if args.cmd == "describe":
            console.print(boxed(f"📖 Describe · {args.id}", describe_challenge(args.id)))
            return

        if args.cmd == "hint":
            console.print(boxed(f"💡 Hint · {args.id}", show_hint(args.id)))
            return

        if args.cmd == "search":
            console.print(boxed("🔍 Search", search_challenges(args.term)))
            return

        if args.cmd == "stats":
            console.print(boxed("📊 Stats", render_stats()))
            return

        if args.cmd == "leaderboard":
            console.print(boxed("🏆 Leaderboard", show_leaderboards()))
            return

        if args.cmd == "doctor":
            console.print(boxed("🩺 Doctor", run_doctor()))
            return

        if args.cmd == "badges":
            console.print(boxed("🏅 Badges", list_badges()))
            return

        if args.cmd in ("stacks", "my-stacks"):
            console.print(boxed("📦 My Stacks & Progress", show_my_stack_progress()))
            return

        if args.cmd == "sync":
            console.print(boxed("🔄 Sync", sync_default()))
            return

        if args.cmd == "submit":
            console.print(boxed("📤 Submit", submit_pending()))
            return

        if args.cmd == "profile":
            if args.action == "show":
                console.print(boxed("👤 Profile", show_profile()))
            else:
                console.print(boxed("👤 Profiles", list_profiles()))
            return

    except KeyboardInterrupt:
        cancelled()


if __name__ == "__main__":
    main()
