# src/devopsmind/mentor/stagnation.py

from devopsmind.state import load_state, save_state

STUCK_THRESHOLD = 3  # attempts before gentle intervention


def detect_stagnation_once():
    """
    Detect if the user is stuck on a challenge.
    This message is shown ONLY ONCE per challenge.
    """

    state = load_state()

    failures = state.get("validation_failures", {})
    completed = set(state.get("progress", {}).get("completed", []))

    mentor_state = state.setdefault("mentor", {})
    shown = mentor_state.setdefault("stagnation_shown", {})

    for challenge_id, attempts in failures.items():
        if attempts < STUCK_THRESHOLD:
            continue

        if challenge_id in completed:
            continue

        # Already shown once → never repeat
        if shown.get(challenge_id):
            continue

        # Mark as shown (confidence boost, not nagging)
        shown[challenge_id] = True
        save_state(state)

        return {
            "challenge_id": challenge_id,
            "attempts": attempts,
        }

    return None
