# Atbash gematria (apply Atbash, then standard gematria)

ATBASH_MAP = {
    "א": "ת", "ב": "ש", "ג": "ר", "ד": "ק", "ה": "צ",
    "ו": "פ", "ז": "ע", "ח": "ס", "ט": "נ",
    "י": "מ", "כ": "ל", "ך": "ל",
    "ל": "כ", "מ": "י", "ם": "י",
    "נ": "ט", "ן": "ט", "ס": "ח", "ע": "ז",
    "פ": "ו", "ף": "ו", "צ": "ה", "ץ": "ה",
    "ק": "ד", "ר": "ג", "ש": "ב", "ת": "א"
}

STANDARD = {
    "א": 1,  "ב": 2,  "ג": 3,  "ד": 4,  "ה": 5,
    "ו": 6,  "ז": 7,  "ח": 8,  "ט": 9,
    "י": 10, "כ": 20, "ך": 20, "ל": 30,
    "מ": 40, "ם": 40, "נ": 50, "ן": 50,
    "ס": 60, "ע": 70, "פ": 80, "ף": 80,
    "צ": 90, "ץ": 90,
    "ק": 100, "ר": 200, "ש": 300, "ת": 400
}

def atbash(text: str) -> str:
    return "".join(ATBASH_MAP.get(ch, ch) for ch in text)

def value(text: str) -> int:
    transformed = atbash(text)
    return sum(STANDARD.get(ch, 0) for ch in transformed)