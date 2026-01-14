# mentor/mentor.py

from rich.panel import Panel
from rich.text import Text
from rich.console import Console, Group

from devopsmind.mentor.engine import get_mentor_advice

console = Console()


def run_mentor():
    advice = get_mentor_advice()
    body = []

    body.append(Text("A mentor’s role is to guide direction, not give answers.\n"))

    # -------------------------------------------------
    # Recommended challenges (ID + title + stack + difficulty)
    # -------------------------------------------------
    body.append(Text("🧭 Recommended next challenges\n", style="bold"))

    for c in advice.get("recommendations", []):
        stack = c.get("stack", "unknown").title()
        difficulty = c.get("difficulty", "—")

        body.append(
            Text(
                f"▶ {c['id']} — {c['title']} "
                f"[{stack} · {difficulty}]",
                style="cyan",
            )
        )

    body.append(Text("\nWhy these challenges:\n", style="bold"))
    body.append(
        Text(
            "They sit in a stack where your confidence is still forming, "
            "and their difficulty nudges growth without overwhelming you.\n"
        )
    )

    # -------------------------------------------------
    # Confidence snapshot
    # -------------------------------------------------
    body.append(Text("\nConfidence snapshot:\n", style="bold"))

    for stack, data in advice.get("confidence", {}).items():
        body.append(
            Text(
                f"• {stack.title():12} → {data['label']} "
                f"({data['completed']} / {data['total']})"
            )
        )

    # -------------------------------------------------
    # Learning style insight
    # -------------------------------------------------
    style = advice.get("learning_style", {})
    body.append(Text("\nLearning style insight:\n", style="bold"))
    body.append(Text(style.get("label", "—")))
    body.append(Text(style.get("explanation", "")))

    # -------------------------------------------------
    # Weekly cadence
    # -------------------------------------------------
    body.append(Text("\nWeekly cadence suggestion:\n", style="bold"))
    body.append(Text(advice.get("cadence", "—")))

    console.print(
        Panel(
            Group(*body),
            title="🧭 DevOpsMind Mentor",
            border_style="cyan",
        )
    )
