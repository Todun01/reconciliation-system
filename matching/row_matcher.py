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
    if ledger_dt.hour >= 23 and bank_day == ledger_day + timedelta(days=1):
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
                continue

            # Smart date matching (pass correct order: ledger, bank)
            if not dates_match(ledger_row["date"], bank_row["date"]):
                continue

            # Name similarity
            similarity = fuzz.token_sort_ratio(
                bank_row["name"].lower(),
                ledger_row["description"].lower()
            )

            # Only check similarity now (amount & date already validated)
            if similarity >= 90 or ledger_row["name"].lower() in bank_row["description"].lower():
                matches.append((i, j, similarity))
                df1.at[i, "matched"] = True
                df2.at[j, "matched"] = True
                break

    return matches, df1, df2
