import pandas as pd
from normalization.name_extractor import extract_date_period
from datetime import datetime
def calculate_group_variance(bank_charges, ledger_charges, period):

    bank = bank_charges.copy()
    ledger = ledger_charges.copy()

    bank["period"] = bank["date"].dt.to_period(period)
    ledger["period"] = ledger["date"].dt.to_period(period)

    bank_totals = bank.groupby("period")["amount"].sum()
    ledger_totals = ledger.groupby("period")["amount"].sum()

    all_periods = set(bank_totals.index).union(set(ledger_totals.index))

    total_difference = 0

    for p in all_periods:
        bank_val = bank_totals.get(p, 0)
        ledger_val = ledger_totals.get(p, 0)

        total_difference += abs(bank_val - ledger_val)

    return total_difference
def detect_best_charge_grouping(bank_charges, ledger_charges):

    weekly_score = calculate_group_variance(
        bank_charges,
        ledger_charges,
        "W"
    )

    monthly_score = calculate_group_variance(
        bank_charges,
        ledger_charges,
        "M"
    )

    if weekly_score <= monthly_score:
        return "Weekly"
    else:
        return "Monthly"
    
def get_mwml_week(date):

    # Monday = 0, Sunday = 6
    weekday = date.weekday()

    # If Sunday → push to next week Monday
    if weekday == 6:
        date = date + pd.Timedelta(days=1)
        weekday = 0

    # Get Monday
    start = date - pd.Timedelta(days=weekday)

    # Saturday = Monday + 5 days
    end = start + pd.Timedelta(days=5)

    return f"{start.date()} to {end.date()}"

# def reconcile_mwml_charges(bank_charges, ledger_charges, grouping="AUTO"):
#     if grouping == "AUTO":
#         grouping = detect_best_charge_grouping(bank_charges, ledger_charges)
#     bank_charges = bank_charges.copy()
#     ledger_charges = ledger_charges.copy()

#     # -----------------------------------
#     # CREATE PERIOD COLUMN
#     # -----------------------------------

#     if grouping == "Weekly":
#         bank_charges["period"] = bank_charges["date"].dt.to_period("W")
#         ledger_charges["period"] = ledger_charges["date"].dt.to_period("W")
#     else:
#         bank_charges["period"] = bank_charges["date"].dt.to_period("M")
#         ledger_charges["period"] = ledger_charges["date"].dt.to_period("M")

#     # -----------------------------------
#     # GROUP BANK CHARGES
#     # -----------------------------------

#     bank_groups = bank_charges.groupby("period")
#     ledger_groups = ledger_charges.groupby("period")

#     matches = []

#     unmatched_bank_periods = []
#     unmatched_ledger_periods = []

#     # -----------------------------------
#     # MATCH PERIODS
#     # -----------------------------------

#     for period, bank_group in bank_groups:

#         bank_total = bank_group["amount"].sum()
#         #print(bank_total)
#         bank_rows = bank_group.index.tolist()
#         #print(bank_rows)
#         if period in ledger_groups.groups:
#             #print(str(period))
#             ledger_group = ledger_groups.get_group(period)

#             ledger_total = ledger_group["amount"].sum()
#             ledger_rows = ledger_group.index.tolist()
#             #print(ledger_total)
#             #print(ledger_rows)
#             if abs(bank_total - ledger_total) < 1:

#                 matches.append({
#                     "status": "MATCHED",
#                     "period": str(period),
#                     "bank_total": bank_total,
#                     "ledger_total": ledger_total,
#                     "bank_rows": bank_rows,
#                     "ledger_rows": ledger_rows
#                 })

#             else:

#                 unmatched_bank_periods.append({
#                     "period": str(period),
#                     "bank_total": bank_total,
#                     "bank_rows": bank_rows
#                 })

#                 unmatched_ledger_periods.append({
#                     "period": str(period),
#                     "ledger_total": ledger_total,
#                     "ledger_rows": ledger_rows
#                 })

#         else:

#             unmatched_bank_periods.append({
#                 "period": str(period),
#                 "bank_total": bank_total,
#                 "bank_rows": bank_rows
#             })

#     # -----------------------------------
#     # FIND LEDGER PERIODS WITHOUT BANK
#     # -----------------------------------

#     for period, ledger_group in ledger_groups:

#         if period not in bank_groups.groups:

#             unmatched_ledger_periods.append({
#                 "period": str(period),
#                 "ledger_total": ledger_group["amount"].sum(),
#                 "ledger_rows": ledger_group.index.tolist()
#             })

#     # -----------------------------------
#     # BUILD RESULT
#     # -----------------------------------

#     return {
#         "matches": matches,
#         "unmatched_bank": unmatched_bank_periods,
#         "unmatched_ledger": unmatched_ledger_periods,
#         "total_matches": len(matches),
#         "total_unmatched_bank": len(unmatched_bank_periods),
#         "total_unmatched_ledger": len(unmatched_ledger_periods),
#         "grouping_used": grouping
#     }
# def reconcile_mwml_charges(bank_charges, ledger_charges):

#     bank = bank_charges.sort_values("date").copy()
#     ledger = ledger_charges.sort_values("date").copy()

#     matches = []
#     unmatched_ledger = []
#     used_bank_rows = set()

#     previous_date = None

#     for ledger_idx, ledger_row in ledger.iterrows():

#         ledger_date = ledger_row["date"]
#         ledger_amount = ledger_row["amount"]

#         # -----------------------------------
#         # DETERMINE PERIOD START
#         # -----------------------------------

#         if previous_date is None:
#             # start of month
#             period_start = ledger_date.replace(day=1)
#         else:
#             period_start = previous_date + pd.Timedelta(days=1)

#         period_end = ledger_date

#         # -----------------------------------
#         # GET BANK ROWS IN PERIOD
#         # -----------------------------------

#         period_rows = bank[
#             (bank["date"] >= period_start) &
#             (bank["date"] <= period_end)
#         ]

#         # remove already used rows
#         period_rows = period_rows[~period_rows.index.isin(used_bank_rows)]

#         bank_total = period_rows["amount"].sum()

#         # -----------------------------------
#         # MATCH CHECK
#         # -----------------------------------

#         if abs(bank_total - ledger_amount) < 1:

#             matches.append({
#                 "status": "MATCHED",
#                 "ledger_index": ledger_idx,
#                 "ledger_amount": ledger_amount,
#                 "bank_total": bank_total,
#                 "difference": bank_total - ledger_amount,
#                 "bank_rows": period_rows.index.tolist(),
#                 "period_start": period_start,
#                 "period_end": period_end
#             })

#             used_bank_rows.update(period_rows.index)

#         else:

#             unmatched_ledger.append({
#                 "ledger_index": ledger_idx,
#                 "ledger_amount": ledger_amount,
#                 "bank_total": bank_total,
#                 "difference": bank_total - ledger_amount,
#                 "period_start": period_start,
#                 "period_end": period_end,
#                 "bank_rows": period_rows.index.tolist()
#             })


#         previous_date = ledger_date

#     # -----------------------------------
#     # UNMATCHED BANK ROWS
#     # -----------------------------------

#     # unmatched_bank = bank.index.difference(list(used_bank_rows)).tolist()
#     for m in matches:
#         print(m["period_start"], "→", m["period_end"], "=", m["bank_total"])
#     return {
#         "matches": matches,
#         "unmatched_ledger": unmatched_ledger,
#         "total_matches": len(matches),
#         "total_unmatched": len(unmatched_ledger),
#     }

# def reconcile_mwml_charges(bank_charges, ledger_charges):

#     bank = bank_charges.sort_values("date").copy()
#     ledger = ledger_charges.sort_values("date").copy()

#     matches = []
#     unmatched_ledger = []
#     used_bank_rows = set()

#     previous_date = None
#     for ledger_idx, ledger_row in ledger.iterrows():

#         ledger_date = extract_date_period(ledger_row["description"])
#         print("Extracted date:", ledger_date)
#         ledger_amount = ledger_row["amount"]

#         if ledger_date is None:
#             ledger_date = ledger_row["date"]

#         ledger_date = pd.to_datetime(ledger_date)
#         # -----------------------------------
#         # DEFINE 7-DAY WINDOW
#         # -----------------------------------

#         period_end = ledger_date
#         if previous_date is None:
#             # start of month
#             period_start = ledger_date.replace(day=1)
#         else:
#             period_start = ledger_date - pd.Timedelta(days=6)
        

#         # -----------------------------------
#         # GET BANK ROWS IN WINDOW
#         # -----------------------------------

#         period_rows = bank[
#             (bank["date"] >= period_start) &
#             (bank["date"] <= period_end)
#         ]

#         # optional: avoid reuse
#         period_rows = period_rows[~period_rows.index.isin(used_bank_rows)]

#         bank_total = period_rows["amount"].sum()
#         # -----------------------------------
#         # MATCH CHECK
#         # -----------------------------------

#         if abs(bank_total - ledger_amount) < 1:

#             matches.append({
#                 "status": "MATCHED",
#                 "ledger_index": ledger_idx,
#                 "ledger_amount": ledger_amount,
#                 "bank_total": bank_total,
#                 "difference": bank_total - ledger_amount,
#                 "bank_rows": period_rows.index.tolist(),
#                 "period_start": period_start,
#                 "period_end": period_end
#             })

#             used_bank_rows.update(period_rows.index)

#         else:

#             unmatched_ledger.append({
#                 "ledger_index": ledger_idx,
#                 "ledger_amount": ledger_amount,
#                 "bank_total": bank_total,
#                 "difference": bank_total - ledger_amount,
#                 "bank_rows": period_rows.index.tolist(),
#                 "period_start": period_start,
#                 "period_end": period_end
#             })

#         previous_date = ledger_date
#     # -----------------------------------
#     # UNMATCHED BANK ROWS
#     # -----------------------------------

#     unmatched_bank = bank.index.difference(list(used_bank_rows)).tolist()

#     return {
#         "matches": matches,
#         "unmatched_ledger": unmatched_ledger,
#         "unmatched_bank": unmatched_bank,
#         "total_matches": len(matches),
#         "total_unmatched_ledger": len(unmatched_ledger),
#         "total_unmatched_bank": len(unmatched_bank)
#     }
def assign_period(date, periods_df):
    match = periods_df[
        (periods_df["start"] <= date) &
        (periods_df["end"] >= date)
    ]
    return match["period_id"].values[0] if not match.empty else None

def reconcile_mwml_charges(bank_charges, ledger_charges, grouping="Weekly"):
    
    bank = bank_charges.sort_values("date").copy()
    ledger = ledger_charges.sort_values("date").copy()

    periods = []

    if grouping == "Weekly":
        
        previous_date = None

        # idenitifes periods from ledger
        for i, row in ledger.iterrows():

            ledger_date = extract_date_period(row["description"]) or row["date"]
            ledger_date = pd.to_datetime(ledger_date)

            if previous_date is None:
                period_start = ledger_date.replace(day=1)
            else:
                period_start = ledger_date - pd.Timedelta(days=6)

            period_end = ledger_date

            periods.append({
                "period_id": len(periods),
                "start": period_start,
                "end": period_end
            })

            previous_date = ledger_date


        periods_df = pd.DataFrame(periods)

        # assign period ids to bank and ledger
        bank["period_id"] = bank["date"].apply(lambda d: assign_period(d, periods_df))
        ledger["period_id"] = ledger["date"].apply(lambda d: assign_period(d, periods_df))

        # group bank and ledger rows according to periods and sum amounts
        bank_grouped = bank.groupby("period_id")["amount"].sum()
        ledger_grouped = ledger.groupby("period_id")["amount"].sum()

        matches = []
        unmatched = []

        all_periods = set(bank_grouped.index).union(set(ledger_grouped.index))

        for pid in all_periods:

            period_info = periods_df[periods_df["period_id"] == pid].iloc[0]

            bank_total = bank_grouped.get(pid, 0)
            ledger_total = ledger_grouped.get(pid, 0)

            bank_rows = bank[bank["period_id"] == pid].index.tolist()
            ledger_rows = ledger[ledger["period_id"] == pid].index.tolist()

            record = {
                "period_id": pid,
                "period_start": period_info["start"],
                "period_end": period_info["end"],
                "bank_total": bank_total,
                "ledger_total": ledger_total,
                "difference": bank_total - ledger_total,
                "bank_rows": bank_rows,
                "ledger_rows": ledger_rows
            }

            if bank_total == ledger_total:
                # print(f"Period {pid} MATCHED: {bank_total} = {ledger_total}")
                matches.append(record)
            else:
                unmatched.append(record)
        return {
            "matches": matches,
            "unmatched": unmatched,
            "periods": periods_df
            }
    elif grouping == "Monthly":
        # -----------------------------------
        # CREATE MONTH COLUMN
        # -----------------------------------

        bank["month"] = bank["date"].dt.to_period("M")
        ledger["month"] = ledger["date"].dt.to_period("M")

        # -----------------------------------
        # GROUP BOTH SIDES
        # -----------------------------------

        bank_grouped = bank.groupby("month")["amount"].sum()
        ledger_grouped = ledger.groupby("month")["amount"].sum()

        # -----------------------------------
        # GET ALL MONTHS
        # -----------------------------------

        all_months = set(bank_grouped.index).union(set(ledger_grouped.index))

        matches = []
        unmatched = []

        # -----------------------------------
        # COMPARE TOTALS
        # -----------------------------------

        for m in all_months:

            bank_total = bank_grouped[m] if m in bank_grouped.index else 0
            ledger_total = ledger_grouped[m] if m in ledger_grouped.index else 0

            bank_rows = bank[bank["month"] == m].index.tolist()
            ledger_rows = ledger[ledger["month"] == m].index.tolist()

            record = {
                "month": str(m),
                "bank_total": bank_total,
                "ledger_total": ledger_total,
                "difference": bank_total - ledger_total,
                "bank_rows": bank_rows,
                "ledger_rows": ledger_rows
            }

            if abs(bank_total - ledger_total) < 1:
                matches.append(record)
            else:
                unmatched.append(record)

        return {
            "matches": matches,
            "unmatched": unmatched
        }

    

def reconcile_msbl_charges(bank_charges, ledger_charges, pd, date_tolerance=2):

    bank = bank_charges.copy()
    ledger = ledger_charges.copy()

    matches = []
    used_bank_rows = set()

    unmatched_ledger = []
    unmatched_bank = []

    for ledger_idx, ledger_row in ledger.iterrows():

        ledger_amount = ledger_row["amount"]
        ledger_date = ledger_row["date"]

        candidate_rows = bank[
            (bank["date"] >= ledger_date - pd.Timedelta(days=date_tolerance)) &
            (bank["date"] <= ledger_date + pd.Timedelta(days=date_tolerance))
        ]

        best_match = None
        best_rows = None

        for i in range(len(candidate_rows)):

            for j in range(i+1, len(candidate_rows)):

                r1 = candidate_rows.iloc[i]
                r2 = candidate_rows.iloc[j]

                if r1.name in used_bank_rows or r2.name in used_bank_rows:
                    continue

                total = r1["amount"] + r2["amount"]

                if abs(total - ledger_amount) < 1:

                    best_match = total
                    best_rows = [r1.name, r2.name]
                    break

            if best_match:
                break

        if best_match:

            matches.append({
                "status": "MATCHED",
                "ledger_index": ledger_idx,
                "bank_rows": best_rows,
                "ledger_amount": ledger_amount,
                "bank_total": best_match
            })

            used_bank_rows.update(best_rows)

        else:

            unmatched_ledger.append(ledger_idx)

    for idx in bank.index:

        if idx not in used_bank_rows:
            unmatched_bank.append(idx)

    return {
        "matches": matches,
        "unmatched_bank": unmatched_bank,
        "unmatched_ledger": unmatched_ledger,
        "total_matches": len(matches),
        "total_unmatched_bank": len(unmatched_bank),
        "total_unmatched_ledger": len(unmatched_ledger)
    }