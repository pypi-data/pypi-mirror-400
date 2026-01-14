from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def show_help():
    console.print(
        Panel(
            Text(
                "DevOpsMind — Offline-first DevOps learning CLI\n\n"
                "Usage:\n"
                "  devopsmind <command> [options]\n\n"
                "Getting started:\n"
                "  login              Onboard in offline or online mode (explicit)\n"
                "  logout             Delete ALL local DevOpsMind data (destructive)\n"
                "  introduce          Optionally introduce yourself to the community\n\n"
                "Core commands:\n"
                "  play <id>          Start a challenge\n"
                "  validate <id>      Validate your solution\n"
                "  search <term>      Search challenges\n"
                "  describe <id>      View challenge details\n"
                "  hint <id>          Get a hint\n"
                "  mentor             Guided next-step suggestions\n\n"
                "Progress & profile:\n"
                "  stats              View XP and progress\n"
                "  stacks             View stack progress\n"
                "  profile show       View your profile\n"
                "  badges             View earned badges\n"
                "  leaderboard        View public leaderboard\n\n"
                "Utilities:\n"
                "  doctor             Diagnose setup issues\n"
                "  sync               Sync progress and leaderboard data\n"
                "  submit             Submit completed challenges\n"
                "  auth               Recovery key rotation\n\n"
                "Modes:\n"
                "  mode online        Enable online mode\n"
                "  mode offline       Switch back to offline mode\n\n"
                "Other:\n"
                "  --version          Show version\n"
                "  --help             Show this help\n\n"
                "Privacy & data:\n"
                "  • DevOpsMind works fully offline by default.\n"
                "  • `introduce` is optional and never automatic.\n"
                "  • `logout` permanently deletes local progress and identity.\n",
                style="white",
            ),
            title="Help",
            border_style="cyan",
        )
    )
