# Mispar Gadol (final letters get extended values)

VALUES = {
    "א": 1,  "ב": 2,  "ג": 3,  "ד": 4,  "ה": 5,
    "ו": 6,  "ז": 7,  "ח": 8,  "ט": 9,

    "י": 10, "כ": 20, "ך": 500, "ל": 30,
    "מ": 40, "ם": 600, "נ": 50, "ן": 700,
    "ס": 60, "ע": 70, "פ": 80, "ף": 800,
    "צ": 90, "ץ": 900,

    "ק": 100, "ר": 200, "ש": 300, "ת": 400
}

def value(text: str) -> int:
    return sum(VALUES.get(ch, 0) for ch in text)