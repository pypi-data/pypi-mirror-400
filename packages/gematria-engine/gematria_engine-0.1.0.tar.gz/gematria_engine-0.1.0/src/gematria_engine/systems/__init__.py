from . import standard, gadol, katan, ordinal, atbash


SYSTEMS = {
    "standard": standard.value,
    "gadol": gadol.value,
    "katan": katan.value,
    "ordinal": ordinal.value,
    "atbash": atbash.value,

}

def list_systems():
    return list(SYSTEMS.keys())