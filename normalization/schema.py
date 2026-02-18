import pandas as pd

STANDARD_COLUMNS = [
    "date",
    "amount",
    "description",
    "reference",
    "source_file"
]

def create_empty_schema():
    return pd.DataFrame(columns=STANDARD_COLUMNS)