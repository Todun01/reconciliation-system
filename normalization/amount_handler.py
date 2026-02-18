def parse_amount(value):
    if value is None:
        return 0

    value = str(value).replace(",", "").strip()

    if "(" in value and ")" in value:
        return -float(value.replace("(", "").replace(")", ""))

    try:
        return float(value)
    except:
        return 0


def build_amount_column(df, mapping):
    import pandas as pd

    if "debit" in mapping and "credit" in mapping:
        debit_col = mapping["debit"]
        credit_col = mapping["credit"]

        df["amount"] = (
            df[credit_col].apply(parse_amount)
            - df[debit_col].apply(parse_amount)
        )

    elif "amount" in mapping:
        df["amount"] = df[mapping["amount"]].apply(parse_amount)

    else:
        df["amount"] = 0

    return df