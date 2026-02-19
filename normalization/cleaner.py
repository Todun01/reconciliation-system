import pandas as pd
import re
from dateutil.parser import parse
from normalization.amount_handler import build_amount_column


def clean_date(value):
    try:
        return parse(str(value))  # KEEP FULL DATETIME
    except:
        return None

def clean_amount(value):
    """
    Converts amounts like:
    - "1,000,000.00"
    - "-500,000"
    - "NGN 200,000"
    into a float: 1000000.0, 500000.0, etc.
    """

    if pd.isna(value):
        return 0.0

    value = str(value)

    # Remove currency text and commas
    value = re.sub(r"[^\d\.-]", "", value)

    try:
        return float(value)
    except:
        return 0.0


def clean_dataframe(df, mapping, source_name):
    cleaned = pd.DataFrame()

    # SAFE DATE HANDLING
    if "date" in mapping and mapping["date"] in df.columns:
        cleaned["date"] = df[mapping["date"]].apply(clean_date)
    else:
        cleaned["date"] = None

    # Build Amount Column safely
    df = build_amount_column(df, mapping)
    cleaned["amount"] = df[mapping["amount"]].apply(clean_amount).abs()


    # Description
    # Extract and normalize customer name

    if "description" in mapping and mapping["description"] in df.columns:
        cleaned["description"] = df[mapping["description"]].astype(str)
    else:
        cleaned["description"] = ""
        
    if "name" in mapping and mapping["name"] in df.columns:
        # Ledger case → use name column directly
        cleaned["name"] = df[mapping["name"]].astype(str)
        
    else:
        # Bank case → extract from description
        cleaned["name"] = ""


    # Reference
    if "reference" in mapping and mapping["reference"] in df.columns:
        cleaned["reference"] = df[mapping["reference"]].astype(str)
    else:
        cleaned["reference"] = ""

    cleaned["source_file"] = source_name

    from normalization.filters import remove_non_transactions

    cleaned = remove_non_transactions(cleaned)
    return cleaned