import requests
from packaging.version import Version
from devopsmind.constants import VERSION

VERSION_META_URL = (
    "https://raw.githubusercontent.com/"
    "InfraForgeLabs/infraforgelabs.github.io/"
    "main/meta/devopsmind/version.json"
)

def check_for_update(timeout: int = 5):
    """
    Returns:
      (update_available: bool, latest_version: str | None, notes: str | None)
    """
    try:
        r = requests.get(VERSION_META_URL, timeout=timeout)
        r.raise_for_status()
        meta = r.json()

        latest = meta.get("latest_version")
        notes = meta.get("notes", "")

        if not latest:
            return False, None, None

        if Version(latest) > Version(VERSION):
            return True, latest, notes

    except Exception:
        return False, None, None

    return False, None, None
