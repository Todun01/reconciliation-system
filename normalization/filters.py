def remove_non_transactions(df):
    df = df.copy()

    # Remove rows where amount = 0
    df = df[df["amount"] != 0]

    # Remove rows with balance keywords
    keywords = ["opening balance", "closing balance", "balance forward"]

    df = df[~df["description"].str.lower().str.contains("|".join(keywords), na=False)]

    return df