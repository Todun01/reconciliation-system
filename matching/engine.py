# from matching.row_matcher import row_match
# from datetime import timedelta

# def dates_match(ledger_date, bank_date):
#     """
#     Matching rule:
#     - Match if same date
#     - OR if ledger time >= 11PM and bank date is next day
#     """

#     if ledger_date is None or bank_date is None:
#         return False

#     ledger_day = ledger_date.date()
#     bank_day = bank_date.date()

#     # Same day match
#     if ledger_day == bank_day:
#         return True

#     # Late night carry-over rule
#     if bank_date.hour >= 23:
#         if bank_day + timedelta(days=1) == ledger_day:
#             return True

#     return False

# def run_matching(df1, df2):

#     matches, df1, df2 = row_match(df1, df2)

#     matched_rows = []

#     for i, j, score in matches:
#         matched_rows.append({
#             "status": "Match",
#             "bank_index": i,
#             "ledger_index": j,
#             "bank_row": df1.loc[i].to_dict(),
#             "ledger_row": df2.loc[j].to_dict(),
#             "name_similarity": score
#         })
    

#     return {
#         "matches": matched_rows,
#         "unmatched_df1": df1[df1["matched"] == False],
#         "unmatched_df2": df2[df2["matched"] == False]
#     }
import re
from rapidfuzz import fuzz

# -----------------------------------
# BUZZWORDS
# -----------------------------------

BUZZWORDS = {
    "deposit", "payment", "transfer", "ngn",
    "ref", "reference", "trx", "txn", "trf",
    "credit", "debit", "for", "to", "from", 
    "echannel", "pos", "atm", "online", "bank", "card",
    "receipt", "invoice", "bill", "utility", "subscription",
    "mobile", "money", "momo", "cash", "withdrawal",
    "fee", "charges", "charge", "service", "pay",
    "received", "sent", "incoming", "outgoing",
    "salary", "wage", "payout", "instant", "settlement",
    "outward", "inward", "nibss", "purchase", "sale", "merchant", "ecommerce",
    "account", "electronic", "nip", "inflow", "outflow", "cr", "dr",
    "WD", "vat", "naira", "client", "frm", "ac", "zib", "meristem", "limited"
}
GROUP_BUZZWORDS = {
    "MSBL": {"stockbrokers"},
    "MWML": {"wealth", "management", "wealthmanagement"},
    "Trustees": {"trustees"},
    "Family Office": {"family", "office", "familyoffice"},
    "MRPSL": {"registrars", "probate", "services"},
    "Finance": {"finance"},
    "Capital": {"capital"},
}
# -----------------------------------
# LIGHT CLEAN (FOR NAME COLUMNS)
# -----------------------------------

def light_clean(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = text.replace("-", " ").replace(",", " ").replace("/", "")
    text = re.sub(r"[^a-z\s]", " ", text)

    tokens = text.split()

    return set(tokens)


# -----------------------------------
# HEAVY TOKEN CLEAN (FOR DESCRIPTION)
# -----------------------------------

def heavy_tokenize(text, group=None):
    
    if not isinstance(text, str):
        return set()

    text = text.lower()
    # Keep letters and spaces only
    text = re.sub(r"[^a-z\s]", " ", text)

    tokens = text.split()
    buzzwords = BUZZWORDS.copy()

    if group or group != "None":
        extra_buzzwords = GROUP_BUZZWORDS.get(group, set())
        buzzwords = buzzwords.union(extra_buzzwords)

    tokens = [
        t for t in tokens
        if len(t) > 2 and t not in buzzwords
    ]

    return set(tokens)


# -----------------------------------
# MAIN MATCHING ENGINE
# -----------------------------------

def run_matching(
    bank_df,
    ledger_df,
    group,
    bank_text_column,
    ledger_text_column,
    date_tolerance=2,
):

    matches = []
    unmatched_bank_indices = set(bank_df.index)
    unmatched_ledger_indices = set(ledger_df.index)

    bank_df = bank_df.copy()
    ledger_df = ledger_df.copy()
    used_ledger_indices = set()

    # -----------------------------------
    # DETERMINE MATCHING MODE
    # -----------------------------------

    use_token_logic = (
        bank_text_column == "description" or
        ledger_text_column == "description"
    )

    bank_check = bank_text_column == "name"
    ledger_check = ledger_text_column == "name"
    # -----------------------------------
    # PRECOMPUTE TEXT REPRESENTATIONS
    # -----------------------------------

    if use_token_logic:
        # Heavy cleaning for token logic
        if bank_check and not ledger_check:
            bank_df["text_tokens"] = bank_df[bank_text_column].apply(light_clean)
            ledger_df["text_tokens"] = ledger_df[ledger_text_column].apply(
                lambda x: heavy_tokenize(x, group)
            )
        elif ledger_check and not bank_check:
            bank_df["text_tokens"] = bank_df[bank_text_column].apply(
                lambda x: heavy_tokenize(x, group)
            )
            ledger_df["text_tokens"] = ledger_df[ledger_text_column].apply(light_clean)
        else:
            bank_df["text_tokens"] = bank_df[bank_text_column].apply(
                lambda x: heavy_tokenize(x, group)
            )
            ledger_df["text_tokens"] = ledger_df[ledger_text_column].apply(
                lambda x: heavy_tokenize(x, group)
            )
    else:
        # Light cleaning for direct fuzzy
        bank_df["text_tokens"] = bank_df[bank_text_column].apply(light_clean)
        ledger_df["text_tokens"] = ledger_df[ledger_text_column].apply(light_clean)

    # -----------------------------------
    # GROUP LEDGER BY AMOUNT
    # -----------------------------------

    ledger_groups = ledger_df.groupby("amount")

    # -----------------------------------
    # ITERATE BANK ROWS
    # -----------------------------------

    for bank_index, bank_row in bank_df.iterrows():

        bank_amount = bank_row["amount"]

        if bank_amount not in ledger_groups.groups:
            continue

        candidates = ledger_groups.get_group(bank_amount)

        # -----------------------------------
        # DATE FILTER
        # -----------------------------------

        candidates = candidates[
            (candidates["date"] - bank_row["date"]).abs().dt.days <= date_tolerance
        ]

        if candidates.empty:
            continue

        best_match = None
        best_score = 0

        # -----------------------------------
        # MATCHING LOOP
        # -----------------------------------

        for ledger_index, ledger_row in candidates.iterrows():

            if ledger_index in used_ledger_indices:
                continue
            if not use_token_logic:
                # -----------------------------
                # LIGHT FUZZY MODE
                # -----------------------------

                bank_text = bank_row["text_tokens"]
                ledger_text = ledger_row["text_tokens"]

                similarity = fuzz.ratio(bank_text, ledger_text)

                if similarity > best_score:
                    best_score = similarity
                    best_match = (ledger_index, ledger_row)
            
            else:
                # -----------------------------
                # TOKEN OVERLAP MODE
                # -----------------------------

                bank_tokens = bank_row["text_tokens"]
                ledger_tokens = ledger_row["text_tokens"]

                overlap = bank_tokens & ledger_tokens

                min_required = min(2, min(len(bank_tokens), len(ledger_tokens)))

                if len(overlap) >= min_required:
                    score = 100
                else:
                    # Fuzzy fallback (word-level)
                    score = 0

                    for b_word in bank_tokens:
                        for l_word in ledger_tokens:
                            similarity = fuzz.ratio(b_word, l_word)
                            if similarity >= 75:
                                score += 1

                    if score >= min_required:
                        score = 90
                    else:
                        score = 0

                if score > best_score:
                    best_score = score
                    best_match = (ledger_index, ledger_row)


        # -----------------------------------
        # SAVE BEST MATCH
        # -----------------------------------

        if best_match and best_score > 0:

            ledger_index, ledger_row = best_match

            matches.append({
                "status": "MATCHED",
                "ledger_index": ledger_index,
                "bank_index": bank_index,
                "ledger_row": ledger_row,
                "bank_row": bank_row,
                "name_similarity": best_score
            })
            used_ledger_indices.add(ledger_index)
            unmatched_bank_indices.discard(bank_index)
            unmatched_ledger_indices.discard(ledger_index)

    # -----------------------------------
    # BUILD UNMATCHED DATAFRAMES
    # -----------------------------------

    unmatched_df1 = bank_df.loc[list(unmatched_bank_indices)]
    unmatched_df2 = ledger_df.loc[list(unmatched_ledger_indices)]

    return {
        "matches": matches,
        "unmatched_df1": unmatched_df1,
        "unmatched_df2": unmatched_df2
    }