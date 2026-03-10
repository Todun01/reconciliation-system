from rapidfuzz import process

COLUMN_PATTERNS = {
    "name": ["customer (fullname)", "recipient name", "recipient a/c name"],
    "date": ["value date", "transfer date", "transaction date", "difference"],
    "amount": ["amount", "amt"],
    "debit": ["debit", "DR", "withdrawal", "withdrawals"],
    "credit": ["credit", "CR", "deposit", "deposits"],
    "description": ["description", "narration", "details", "remarks"],
    "reference": ["reference", "ref", "transaction id"]
}

def find_best_match(patterns, columns):
    for pattern in patterns:
        match = process.extractOne(pattern, columns, score_cutoff=80)
        if match:
            return match[0]
    return None

def map_columns(df):
    mapped = {}
    lower_cols = [c.lower() for c in df.columns]

    for col in lower_cols:
        for standard_col, patterns in COLUMN_PATTERNS.items():
            match = process.extractOne(col, patterns, score_cutoff=80)
            if match:
                mapped[standard_col] = df.columns[lower_cols.index(col)]

    return mapped