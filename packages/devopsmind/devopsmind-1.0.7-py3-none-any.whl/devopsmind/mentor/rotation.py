from pathlib import Path
import json
import hashlib

from devopsmind.state import load_state, save_state


# ---------------------------------------------------------
# Rotation memory is stored inside existing state.json
# ---------------------------------------------------------

ROTATION_KEY = "mentor_rotation_memory"


def _hash_recommendations(recs: list[str]) -> str:
    """
    Create a stable hash for a set of recommended challenge IDs.
    Order-independent.
    """
    normalized = sorted(recs)
    raw = ",".join(normalized)
    return hashlib.sha256(raw.encode()).hexdigest()


def load_rotation_memory() -> set[str]:
    """
    Load previously used recommendation hashes.
    """
    state = load_state()
    memory = state.get(ROTATION_KEY, [])
    return set(memory)


def save_rotation_memory(recommended_ids: list[str]) -> None:
    """
    Save the current recommendation set so it is never repeated.
    """
    state = load_state()
    memory = set(state.get(ROTATION_KEY, []))

    memory.add(_hash_recommendations(recommended_ids))

    state[ROTATION_KEY] = list(memory)
    save_state(state)


def has_seen_recommendation(recommended_ids: list[str]) -> bool:
    """
    Check if this recommendation set was already shown before.
    """
    memory = load_rotation_memory()
    rec_hash = _hash_recommendations(recommended_ids)
    return rec_hash in memory
