import streamlit as st
import pandas as pd
from normalization.column_mapper import map_columns
from normalization.cleaner import clean_dataframe

from ingestion.file_reader import read_file
from matching.engine import run_matching
from utils.amount_selector import build_amount_config
from utils.name_selector import name_selector
from utils.charges import is_charge
from utils.charge_recon import reconcile_mwml_charges
from utils.charge_recon import reconcile_msbl_charges


st.title("Reconciliation System")

bank = st.file_uploader("Upload Bank Statement", type=["csv","xlsx","pdf", "xls"])
ledger = st.file_uploader("Upload Ledger File", type=["csv","xlsx","pdf", "xls"])

if bank and ledger:

    # reading files
    bank_raw = read_file(bank)
    ledger_raw = read_file(ledger)

    # mapping columns
    bank_map = map_columns(bank_raw)
    ledger_map = map_columns(ledger_raw)

    # displaying mapping
    st.write("Detected Bank Columns:", bank_map)
    st.write("Detected Ledger Columns:", ledger_map)

    # selecting module (group)
    group = st.selectbox(
        "Select Group",
        ["None", "MSBL", "MWML", "Trustees", "Family Office", "Finance", "Capital", "MRPSL"]
    )

    # selecting name/text columns for matching
    bank_text_column = name_selector("Bank Statement", bank_map, st)
    ledger_text_column = name_selector("Ledger File", ledger_map, st)

    # clean and build amount columns based on config
    bank_config = build_amount_config("Bank Statement", bank_map, st)
    ledger_config = build_amount_config("Ledger File", ledger_map, st)

    # select charge config based on group
    if group == "MWML":
        charge_grouping = st.selectbox(
            "Please select the bank charge aggregation period for the Ledger",
            ["Weekly", "Monthly"]
        )


    run = st.button("Run Reconciliation")
    if run:
        # clean files and convert to dataframes
        bank_df = clean_dataframe(bank_raw, bank_map, bank.name, bank_config)
        ledger_df = clean_dataframe(ledger_raw, ledger_map, ledger.name, ledger_config)

        # display cleaned data
        st.subheader("Bank Data")
        st.dataframe(bank_df)

        st.subheader("Ledger Data")
        st.dataframe(ledger_df)

        # compute transaction matching results
        results = run_matching(
            bank_df,
            ledger_df,
            group=group,
            bank_text_column=bank_text_column,
            ledger_text_column=ledger_text_column,
            date_tolerance=2,
        )

        # display results
        
        # Charges 
        # st.metric("Charge Matches", charge_results["total_matches"])
        # st.metric("Unmatched Bank Charges", charge_results["total_unmatched_bank"])
        # st.metric("Unmatched Ledger Charges", charge_results["total_unmatched_ledger"])

        # Transactions
        st.subheader("Matched Transactions")
        st.write("Total Transaction Matches Found:", len(results["matches"]))

        # ===== SHOW MATCHED ROWS =====

        if results["matches"]:

            matched_display = []

            for m in results["matches"]:
                row = {
                    "Status": m["status"],
                    "Ledger Name": m["ledger_row"][ledger_text_column],
                    "Bank Name": m["bank_row"][bank_text_column],
                    "Ledger Row No.": m["ledger_index"],
                    "Bank Row No.": m["bank_index"],
                    "Ledger Amount": m["ledger_row"]["amount"],
                    "Bank Amount": m["bank_row"]["amount"],
                    "Ledger Date": m["ledger_row"]["date"].date(),
                    "Bank Date": m["bank_row"]["date"],
                    "Name Similarity": str(int(m["name_similarity"])) + "%"
                }
                matched_display.append(row)

            st.dataframe(matched_display)


        # ===== SHOW UNMATCHED =====

        st.subheader("Unmatched Bank Transactions")
        st.write(f"Total Potential Mis-matches Found: {len(results["unmatched_df1"])}")
        st.dataframe(results["unmatched_df1"])

        st.subheader("Unmatched Ledger Transactions")
        st.write(f"Total Potential Mis-matches Found: {len(results["unmatched_df2"])}")
        st.dataframe(results["unmatched_df2"])

        # separate charges and transactions
        bank_charges = results["unmatched_df1"][results["unmatched_df1"]["description"].apply(is_charge)]
        unmatched_bank_transactions = results["unmatched_df1"][~results["unmatched_df1"]["description"].apply(is_charge)]
        st.subheader("Bank Charges")
        st.dataframe(bank_charges)

        ledger_charges = results["unmatched_df2"][results["unmatched_df2"]["description"].apply(is_charge)]
        unmatched_ledger_transactions = results["unmatched_df2"][~results["unmatched_df2"]["description"].apply(is_charge)]
        st.subheader("Ledger Charges")
        st.dataframe(ledger_charges)

        # compute charge matching results
        if group == "MWML":
            charge_results = reconcile_mwml_charges(
                bank_charges,
                ledger_charges,
                grouping=charge_grouping,
            )
        elif group == "MSBL":

            charge_results = reconcile_msbl_charges(
                bank_charges,
                ledger_charges,
                pd,
                date_tolerance=2
            )


        st.subheader("Matched Charge Periods")
        st.write("Total Charge Matches Found:", len(charge_results["matches"]))
        if charge_results["matches"]:
            matched_charge_display = []
            if charge_grouping == "Weekly":
                for m in charge_results["matches"]:

                    matched_charge_display.append({
                        "Period": f"{m["period_start"].date()} - {m["period_end"].date()}",
                        "Ledger Total": m["ledger_total"],
                        "Bank Total": m["bank_total"],
                        "Difference": m["difference"],
                        "Bank Rows": m["bank_rows"],
                        "Ledger Rows": m["ledger_rows"]
                    })
            elif charge_grouping == "Monthly":
                for m in charge_results["matches"]:

                    matched_charge_display.append({
                        "Period": m["month"],
                        "Ledger Total": m["ledger_total"],
                        "Bank Total": m["bank_total"],
                        "Difference": m["difference"],
                        "Bank Rows": m["bank_rows"],
                        "Ledger Rows": m["ledger_rows"]
                    })

            st.dataframe(matched_charge_display)


        st.subheader("Unmatched Charge Periods")
        st.write("Total Charge Mis-Matches Found:", len(charge_results["unmatched"]))
        if charge_results["unmatched"]:

            unmatched_charge_display = []
            if charge_grouping == "Weekly":

                for u in charge_results["unmatched"]:
                    unmatched_charge_display.append({
                        "Period": f"{u["period_start"].date()} - {u["period_end"].date()}",
                        "Ledger Total": u["ledger_total"],
                        "Bank Total": u["bank_total"],
                        "Difference": u["difference"],
                        "Bank Rows": u["bank_rows"],
                        "Ledger Rows": u["ledger_rows"]
                    })
            elif charge_grouping == "Monthly":

                for u in charge_results["unmatched"]:
                    unmatched_charge_display.append({
                        "Period": u["month"],
                        "Ledger Total": u["ledger_total"],
                        "Bank Total": u["bank_total"],
                        "Difference": u["difference"],
                        "Bank Rows": u["bank_rows"],
                        "Ledger Rows": u["ledger_rows"]
                    })

            st.dataframe(unmatched_charge_display)
        

        
        # st.subheader("Detected Charge Periods")

        # periods_df = charge_results["periods"].copy()
        # periods_df["Period"] = periods_df.apply(
        #     lambda x: f"{x['start'].date()} → {x['end'].date()}",
        #     axis=1
        # )

        # st.dataframe(periods_df[["period_id", "Period"]])

        st.header("Remaining Unmatched Transactions")

        st.subheader("Unmatched Bank Transactions")
        st.write("Total Remaining Bank Mis-Matches Found:", len(unmatched_bank_transactions))
        st.dataframe(unmatched_bank_transactions)

        st.subheader("Unmatched Ledger Transactions")
        st.write("Total Remaining Bank Mis-Matches Found:", len(unmatched_ledger_transactions))
        st.dataframe(unmatched_ledger_transactions)


