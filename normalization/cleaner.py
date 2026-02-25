import pandas as pd
import re
from dateutil.parser import parse
from normalization.name_extractor import extract_name
from normalization.name_extractor import generate_regex_from_sample
from normalization.name_extractor import validate_pattern
from normalization.filters import remove_non_transactions
from normalization.adaptive_name_extractor import extract_name_adaptive

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

def build_amount_from_config(df, config):

    mode = config["mode"]

    def clean(value):
        if pd.isna(value):
            return 0.0
        value = str(value)
        value = re.sub(r"[^\d\.-]", "", value)
        try:
            return abs(float(value))
        except:
            return 0.0

    if mode == "amount":
        return df[config["amount_col"]].apply(clean)

    elif mode == "debit":
        return df[config["debit_col"]].apply(clean)

    elif mode == "credit":
        return df[config["credit_col"]].apply(clean)

    elif mode == "combine":
        debit = df[config["debit_col"]].apply(clean)
        credit = df[config["credit_col"]].apply(clean)
        return debit + credit

    else:
        raise ValueError("Invalid amount mode")

def clean_dataframe(df, mapping, source_name, amount_config):
    cleaned = pd.DataFrame()
    # SAFE DATE HANDLING
    if "date" in mapping and mapping["date"] in df.columns:
        cleaned["date"] = df[mapping["date"]].apply(clean_date)

    # Build Amount Column safely
    cleaned["amount"] = build_amount_from_config(df, amount_config)

    # if "credit" in mapping and mapping["credit"] in df.columns:
    #     cleaned["credit"] = df[mapping["credit"]].apply(clean_amount).abs()
    
    # if "debit" in mapping and mapping["debit"] in df.columns:
    #     cleaned["debit"] = df[mapping["debit"]].apply(clean_amount).abs()

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
        cleaned["name"] = None


    # Reference
    if "reference" in mapping and mapping["reference"] in df.columns:
        cleaned["reference"] = df[mapping["reference"]].astype(str)
    
    else: 
        cleaned["reference"] = ""

    cleaned["source_file"] = source_name
    cleaned = remove_non_transactions(cleaned)

    # Adaptive pattern generation and extraction
    # current_pattern = None
    # compiled_pattern = None

    # for idx, desc in cleaned["description"].items():
    #     if desc.strip():
    #         current_pattern = generate_regex_from_sample(desc)
    #         compiled_pattern = re.compile(current_pattern, re.IGNORECASE)
    #         break


    # extracted_names = []

    # for desc in cleaned["description"]:

    #     if not compiled_pattern:
    #         extracted_names.append("")
    #         continue

    #     match = compiled_pattern.search(desc)

    #     # SUCCESS → use existing pattern
    #     if match:
    #         extracted_names.append(match.group(1).strip())
    #         continue

    #     # FAIL → generate new pattern ONLY now
    #     new_pattern = generate_regex_from_sample(desc)

    #     try:
    #         compiled_pattern = re.compile(new_pattern, re.IGNORECASE)
    #         match = compiled_pattern.search(desc)

    #         if match:
    #             extracted_names.append(match.group(1).strip())
    #         else:
    #             extracted_names.append("")

    #     except:
    #         extracted_names.append("")


    # cleaned["extracted_name"] = extracted_names

    # One generated pattern for all
    sample_row = cleaned["description"].iloc[0]
    pattern = generate_regex_from_sample(sample_row)
    if not validate_pattern(pattern):
        raise ValueError("Generated regex is not Python-compatible.")


    cleaned["extracted_name"] = cleaned["description"].apply(
        lambda x: extract_name(x, pattern)
        )
    if cleaned["name"].isna().all():
        cleaned["name"] = cleaned["extracted_name"]
    return cleaned