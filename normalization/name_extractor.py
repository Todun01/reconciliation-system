import re

def extract_name(description):
    if not description:
        return ""

    text = description.upper()

    # Common patterns
    patterns = [
        r"FOR\s+([A-Z][A-Z\-\.'\s]+?)\s+NGN",
        r"FROM\s+([A-Z][A-Z\-\.'\s]+?)\s+NGN",
        r"BY\s+([A-Z][A-Z\-\.'\s]+?)\s+NGN"
    ]


    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return ""
