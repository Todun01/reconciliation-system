from rapidfuzz import process

COLUMN_PATTERNS = {
    "name": ["customer (fullname)"],
    "date": ["date", "transaction date", "value date", "posting"],
    "debit": ["debit", "debit amount", "debit amount paid","withdrawal", "outflow"],
    "credit": ["credit", "credit amount", "credit amount paid", "deposit", "inflow"],
    "amount": ["amount", "amount paid", "amt", "value"],
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