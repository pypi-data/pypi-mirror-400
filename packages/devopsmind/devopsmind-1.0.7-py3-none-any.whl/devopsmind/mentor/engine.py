# src/devopsmind/mentor/engine.py

from devopsmind.mentor.providers.rule_based import RuleBasedMentor
from devopsmind.mentor.providers.paid_stub import PaidMentor
from devopsmind.mentor.providers.ember_stub import EmberMentor
from devopsmind.mentor.stagnation import detect_stagnation_once
from devopsmind.state import load_state


def get_mentor_advice():
    """
    Provider selector.
    This is the ONLY place where mentor intelligence is chosen.
    """

    state = load_state()

    ember_enabled = state.get("ember_enabled", False)
    paid_entitlement = state.get("paid_entitlement", False)

    if ember_enabled:
        provider = EmberMentor()
    elif paid_entitlement:
        provider = PaidMentor()
    else:
        provider = RuleBasedMentor()

    advice = provider.generate()

    # Inject stagnation signal (non-invasive)
    stagnation = detect_stagnation_once()
    if stagnation:
        advice["stagnation"] = stagnation

    return advice

