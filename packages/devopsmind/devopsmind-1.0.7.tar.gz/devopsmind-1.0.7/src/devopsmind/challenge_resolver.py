from pathlib import Path
import yaml


def find_challenge_by_id(challenge_id: str) -> Path | None:
    """
    Find a challenge directory by `id` from challenge.yaml.
    Searches recursively under devopsmind/challenges/.
    """
    base = Path(__file__).parent / "challenges"

    for meta in base.rglob("challenge.yaml"):
        try:
            data = yaml.safe_load(meta.read_text()) or {}
        except Exception:
            continue

        if data.get("id") == challenge_id:
            return meta.parent

    return None


def get_all_challenges() -> list[dict]:
    """
    Load metadata for ALL challenges.

    This is intentionally read-only and offline-safe.
    Used by mentor, stats, diagnostics, and future providers.
    """
    base = Path(__file__).parent / "challenges"
    challenges = []

    for meta in base.rglob("challenge.yaml"):
        try:
            data = yaml.safe_load(meta.read_text()) or {}
        except Exception:
            continue

        if not data.get("id"):
            continue

        challenges.append({
            "id": data.get("id"),
            "title": data.get("title", data.get("id")),
            "stack": data.get("stack", "unknown"),
            "difficulty": data.get("difficulty", "Unknown"),
            "xp": data.get("xp", 0),
            "path": str(meta.parent),
        })

    return challenges


def list_all_challenges() -> list[dict]:
    """
    Alias for backward / forward compatibility.
    """
    return get_all_challenges()
