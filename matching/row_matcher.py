from rapidfuzz import fuzz
from datetime import timedelta

def dates_match(ledger_dt, bank_dt):
    if not ledger_dt or not bank_dt:
        return False

    ledger_day = ledger_dt.date()
    bank_day = bank_dt.date()

    # Case 1: Same day
    if ledger_day == bank_day:
        return True

    # Case 2: Ledger late-night → next day bank
    if bank_dt.hour >= 23 and ledger_day == bank_day + timedelta(days=1):
        return True

    return False


def row_match(df1, df2):
    """
    df1 = Bank
    df2 = Ledger
    """
    matches = []

    df1 = df1.copy()
    df2 = df2.copy()

    df1["matched"] = False
    df2["matched"] = False

    for i, bank_row in df1.iterrows():
        for j, ledger_row in df2.iterrows():

            if ledger_row["matched"]:
                continue

            # Amount must match
            if bank_row["amount"] != ledger_row["amount"]:
                # print(f"{bank_row["amount"]} did not match {ledger_row["amount"]}")
                continue

            # Smart date matching (pass correct order: ledger, bank)
            if not dates_match(ledger_row["date"], bank_row["date"]):
                # print("date not matched")
                continue

            # Name similarity
            similarity = fuzz.token_sort_ratio(
                bank_row["name"].lower(),
                ledger_row["extracted_name"].lower()
            )
            bank_words = bank_row["name"].lower().split()
            ledger_words = ledger_row["extracted_name"].lower().split()
            similarity_index = 80
            if len(bank_words) > 2 or len(ledger_words) > 2:
                similarity_index = 70
            # print(f"similarity for {bank_row["name"].lower()} and {ledger_row["description"].lower()} is {similarity}")
            # Only check similarity now (amount & date already validated)
            if similarity >= similarity_index:
                matches.append((i, j, similarity))
                df1.at[i, "matched"] = True
                df2.at[j, "matched"] = True
                break

    return matches, df1, df2
