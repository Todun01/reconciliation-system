from rapidfuzz import process

COLUMN_PATTERNS = {
    "name": ["customer (fullname)", "recipient name", "recipient a/c name"],
    "date": ["value date", "transfer date", "transaction date", "date", "difference"],
    "amount": ["amount", "amt", "amount paid"],
    "debit": ["debit", "DR", "withdrawal"],
    "credit": ["credit", "CR", "deposit"],
    "description": ["description", "narration", "details", "remarks"],
    "reference": ["reference", "ref", "transaction id"]
}

from rapidfuzz import process, fuzz

def find_best_match(patterns, columns):
    best_match = None
    best_score = 0

    for pattern in patterns:
        match = process.extractOne(pattern, columns, scorer=fuzz.WRatio)
        if match and match[1] > best_score:
            best_match = match[0]
            best_score = match[1]

    if best_score >= 80:
        return best_match

    return None

def map_columns(df):
    mapped = {}

    # Create lowercase lookup map
    col_map = {col.lower(): col for col in df.columns}
    lower_cols = list(col_map.keys())

    for standard_col, patterns in COLUMN_PATTERNS.items():
        match = find_best_match(patterns, lower_cols)
        if match:
            mapped[standard_col] = col_map[match]  # return ORIGINAL name

    return mapped