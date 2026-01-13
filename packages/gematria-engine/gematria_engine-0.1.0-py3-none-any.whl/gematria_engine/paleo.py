# Paleo-Hebrew (Ktav Ivri) mapping for each modern Hebrew letter.

PALEO_MAP = {
    "א": "𐤀",
    "ב": "𐤁",
    "ג": "𐤂",
    "ד": "𐤃",
    "ה": "𐤄",
    "ו": "𐤅",
    "ז": "𐤆",
    "ח": "𐤇",
    "ט": "𐤈",
    "י": "𐤉",

    "כ": "𐤊", "ך": "𐤊",
    "ל": "𐤋",
    "מ": "𐤌", "ם": "𐤌",
    "נ": "𐤍", "ן": "𐤍",
    "ס": "𐤎",
    "ע": "𐤏",
    "פ": "𐤐", "ף": "𐤐",
    "צ": "𐤑", "ץ": "𐤑",

    "ק": "𐤒",
    "ר": "𐤓",
    "ש": "𐤔",
    "ת": "𐤕",
}

def to_paleo(text: str) -> str:
    """Convert modern Hebrew text to Paleo-Hebrew."""
    return "".join(PALEO_MAP.get(ch, ch) for ch in text)