from matching.row_matcher import row_match
from datetime import timedelta

def dates_match(ledger_date, bank_date):
    """
    Matching rule:
    - Match if same date
    - OR if ledger time >= 11PM and bank date is next day
    """

    if ledger_date is None or bank_date is None:
        return False

    ledger_day = ledger_date.date()
    bank_day = bank_date.date()

    # Same day match
    if ledger_day == bank_day:
        return True

    # Late night carry-over rule
    if bank_date.hour >= 23:
        if bank_day + timedelta(days=1) == ledger_day:
            return True

    return False

def run_matching(df1, df2):

    matches, df1, df2 = row_match(df1, df2)

    matched_rows = []

    for i, j, score in matches:
        matched_rows.append({
            "status": "Match",
            "bank_index": i,
            "ledger_index": j,
            "bank_row": df1.loc[i].to_dict(),
            "ledger_row": df2.loc[j].to_dict(),
            "name_similarity": score
        })
    

    return {
        "matches": matched_rows,
        "unmatched_df1": df1[df1["matched"] == False],
        "unmatched_df2": df2[df2["matched"] == False]
    }
