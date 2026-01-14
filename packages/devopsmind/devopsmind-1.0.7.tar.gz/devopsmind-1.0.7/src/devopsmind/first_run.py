from rich.panel import Panel
from rich.text import Text
from rich.console import Console
import getpass
import random

from devopsmind.state import (
    is_first_run,
    save_state,
    load_state,
    mark_session_unlocked,
    get_restore_decision,
    set_restore_decision,
)
from devopsmind.snapshot import snapshot_exists, restore_snapshot
from devopsmind.remote import authenticate_with_worker
from devopsmind.cloud_restore import maybe_prompt_cloud_restore

# 🔹 Fire-and-forget telemetry (anonymous counters)
from devopsmind.telemetry import send_event

console = Console()


def suggest_handles(base: str) -> list[str]:
    """
    Generate handle suggestions based on user input
    """
    suffixes = [
        "_dev",
        "_ops",
        "_infra",
        "_cloud",
        "_sec",
        "_x",
        f"_{random.randint(1,99)}",
        f"{random.randint(1,99)}",
    ]

    return [f"{base}{s}" for s in suffixes][:5]


def ensure_first_run(force: bool = False) -> bool:
    if not force and not is_first_run():
        return True

    console.print(
        Panel(
            Text(
                "Welcome to DevOpsMind 🚀\n\n"
                "DevOpsMind works fully offline by default.\n"
                "You decide if and when anything goes online.",
                justify="center",
            ),
            title="🧠 First Run Setup",
            border_style="cyan",
        )
    )

    choice = input("Enable ONLINE mode now? [y/N]: ").strip().lower()

    # =================================================
    # OFFLINE MODE (FIRST RUN)
    # =================================================
    if choice != "y":
        username = input("👤 Choose a local username: ").strip()
        handle = input("🎮 Choose a handle: ").strip()

        state = {
            "mode": "offline",
            "auth": {"lock_enabled": False},
            "profile": {
                "username": username,
                "gamer": handle,
            },
        }

        save_state(state)

        # 🔹 Telemetry: offline first run
        send_event("first_run_offline")

        console.print(
            Panel(
                Text(
                    "You are now in OFFLINE mode.\n\n"
                    "Nothing has been sent online.\n"
                    "No account was created.\n\n"
                    "If you ever choose to introduce yourself to the "
                    "DevOpsMind community, you can do so explicitly by running:\n\n"
                    "  devopsmind introduce\n\n"
                    "This is optional and will never happen automatically.",
                    justify="center",
                ),
                title="📴 Offline Mode",
                border_style="green",
            )
        )

        return True

    # =================================================
    # ONLINE MODE
    # =================================================
    console.print(
        Panel(
            Text(
                "Online account options:\n\n"
                "1) Login / Signup\n"
                "2) Reset password (Recovery key)\n\n"
                "👉 For Email OTP reset, please use the website.",
                justify="center",
            ),
            title="🔐 Online Account",
            border_style="cyan",
        )
    )

    action = input("Choose [1/2]: ").strip()
    if action not in ("1", "2"):
        console.print(Panel(Text("❌ Invalid option"), border_style="red"))
        return False

    email = input("📧 Email: ").strip().lower()

    # =================================================
    # PASSWORD RESET
    # =================================================
    if action == "2":
        recovery_key = getpass.getpass("🔑 Recovery key: ")
        new_password = getpass.getpass("🔒 New password: ")

        result = authenticate_with_worker(
            email=email,
            mode="reset",
            recovery_key=recovery_key,
            new_password=new_password,
        )

        if not result or not result.get("ok"):
            console.print(Panel(Text("❌ Password reset failed"), border_style="red"))
            return False

        console.print(Panel(Text("✔ Password reset successful"), border_style="green"))
        return False

    # =================================================
    # LOGIN / SIGNUP
    # =================================================
    password = getpass.getpass("🔒 Password: ")

    result = authenticate_with_worker(
        email=email,
        password=password,
        mode="login",
    )

    # ---------------- LOGIN SUCCESS ----------------
    if result and result.get("ok"):
        email_hash = result["email_hash"]
        user_public_id = result["user_public_id"]
        username = result["username"]
        handle = result["handle"]

    # ---------------- SIGNUP FLOW ----------------
    elif result and result.get("error") == "account not found":
        console.print(
            Panel(Text("🆕 No account found. Creating one now."), border_style="green")
        )

        username = input("👤 Choose a public username: ").strip()
        base_handle = input("🎮 Choose a handle: ").strip().lower()
        handle = base_handle

        while True:
            signup = authenticate_with_worker(
                email=email,
                password=password,
                username=username,
                handle=handle,
                mode="signup",
            )

            if signup and signup.get("ok"):
                email_hash = signup["email_hash"]
                user_public_id = signup["user_public_id"]
                username = signup["username"]
                handle = signup["handle"]

                if "recovery_key" in signup:
                    console.print(
                        Panel(
                            Text(
                                "SAVE THIS RECOVERY KEY (ONCE)\n\n"
                                f"{signup['recovery_key']}",
                                justify="center",
                            ),
                            title="🔑 Recovery Key",
                            border_style="yellow",
                        )
                    )
                    input("Press Enter after saving the recovery key...")
                break

            if signup and signup.get("error") == "handle already taken":
                suggestions = suggest_handles(base_handle)
                console.print(
                    Panel(
                        Text(
                            "❌ Handle already taken.\n\nSuggestions:\n"
                            + "\n".join(f"  • {s}" for s in suggestions)
                        ),
                        border_style="yellow",
                    )
                )
                handle = input("🎮 Try another handle: ").strip().lower()
                continue

            console.print(
                Panel(
                    Text(f"❌ Signup failed: {signup.get('error')}"),
                    border_style="red",
                )
            )
            return False

    # ---------------- OTHER LOGIN ERROR ----------------
    else:
        console.print(
            Panel(
                Text(f"❌ {result.get('error', 'Login failed')}"),
                border_style="red",
            )
        )
        return False

    # =================================================
    # MERGE STATE
    # =================================================
    snapshot_existed = snapshot_exists(user_public_id)

    state = load_state()
    state["mode"] = "online"
    state.setdefault("auth", {})["lock_enabled"] = True
    state["profile"] = {
        "username": username,
        "gamer": handle,
        "email_hash": email_hash,
        "user_public_id": user_public_id,
    }

    save_state(state)
    mark_session_unlocked()

    maybe_prompt_cloud_restore(user_public_id)

    if snapshot_existed:
        decision = get_restore_decision(user_public_id)
        if decision is None:
            decision = (
                input("Restore cloud progress? [Y/n]: ").strip().lower()
                in ("", "y", "yes")
            )
            set_restore_decision(user_public_id, decision)
        if decision:
            restore_snapshot(user_public_id)

    console.print(
        Panel(Text("✔ Online login successful"), border_style="green")
    )

    # 🔹 Telemetry: online first run + first login
    send_event("first_run_online")
    send_event("first_login_online")

    return True
