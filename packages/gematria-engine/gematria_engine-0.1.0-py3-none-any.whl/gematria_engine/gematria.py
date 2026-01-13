from .systems import SYSTEMS, list_systems

def gematria_value(text: str, system: str = "standard") -> int:
    """
    Compute the gematria value of a Hebrew string using the specified system.
    """
    if system not in SYSTEMS:
        raise ValueError(f"Unknown system '{system}'. Use one of: {list_systems()}")
    return SYSTEMS[system](text)

def breakdown(text: str, system: str = "standard"):
    """
    Return a list of (letter, value) pairs for the given system.
    """
    if system not in SYSTEMS:
        raise ValueError(f"Unknown system '{system}'. Use one of: {list_systems()}")

    func = SYSTEMS[system]
    return [(ch, func(ch)) for ch in text]