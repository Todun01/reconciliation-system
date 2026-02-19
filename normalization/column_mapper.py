from rapidfuzz import process

COLUMN_PATTERNS = {
    "name": ["customer (fullname)"],
    "date": ["date", "value date", "transaction date", "posting"],
    "amount": ["amount", "amount paid", "amt", "debit amount", "debit",  "debit amount paid", "value"],
    "description": ["description", "narration", "details"],
    "reference": ["reference", "ref", "transaction id"]
}

def find_best_match(patterns, columns):
    for pattern in patterns:
        match = process.extractOne(pattern, columns, score_cutoff=70)
        if match:
            return match[0]
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