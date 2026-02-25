import re
from normalization.name_extractor import generate_regex_from_sample

# Pattern memory (in-memory cache)
PATTERN_CACHE = []


def is_valid_name(name: str):
    """
    Validate extracted name so we don't store bad patterns.
    """

    if not name:
        return False

    name = name.strip()

    # Too short
    if len(name) < 2 or len(name) > 3:
        return False

    # Must contain letters
    if not re.search(r"[A-Za-z]", name):
        return False

    # Reject numeric garbage
    if re.fullmatch(r"[0-9 ,.-]+", name):
        return False

    return True


def try_extract_with_pattern(text, pattern):
    """
    Try extracting name using an existing regex pattern.
    """

    try:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            if is_valid_name(name):
                return name
    except:
        pass

    return None


def extract_name_adaptive(text):
    """
    Smart adaptive extractor that learns patterns on the fly.
    """

    # STEP 1 — Try existing patterns first
    for pattern in PATTERN_CACHE:
        name = try_extract_with_pattern(text, pattern)
        if name:
            return name

    # STEP 2 — No pattern worked → generate new one using AI
    new_pattern = generate_regex_from_sample(text)

    if new_pattern:
        PATTERN_CACHE.append(new_pattern)

        name = try_extract_with_pattern(text, new_pattern)
        if name:
            return name

    # STEP 3 — Final fallback
    return ""