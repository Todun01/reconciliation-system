def normalize_name(name):
    if not name:
        return ""

    return " ".join(name.upper().split())
