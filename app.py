import streamlit as st
from normalization.column_mapper import map_columns
from normalization.cleaner import clean_dataframe

from ingestion.file_reader import read_file
from matching.engine import run_matching


st.title("Reconciliation System")

bank = st.file_uploader("Upload Bank Statement", type=["csv","xlsx","pdf"])
ledger = st.file_uploader("Upload Ledger File", type=["csv","xlsx","pdf"])

if bank and ledger:

    bank_raw = read_file(bank)
    ledger_raw = read_file(ledger)

    bank_map = map_columns(bank_raw)
    ledger_map = map_columns(ledger_raw)

    ledger_amount_column = None

    # Identify ledger amount options
    ledger_options = []

    if "debit" in ledger_map:
        ledger_options.append(ledger_map["debit"])

    if "credit" in ledger_map:
        ledger_options.append(ledger_map["credit"])

    # Show selector ONLY if multiple options exist
    if len(ledger_options) > 1:
        ledger_amount_column = st.selectbox(
            "Select Ledger Amount Column",
            ledger_options
        )
    elif len(ledger_options) == 1:
        ledger_amount_column = ledger_options[0]

    bank_df = clean_dataframe(bank_raw, bank_map, bank.name)
    ledger_df = clean_dataframe(ledger_raw, ledger_map, ledger.name, amount_column_override=ledger_amount_column)

    st.subheader("Bank Data")
    st.dataframe(bank_df)

    st.subheader("Ledger Data")
    st.dataframe(ledger_df)

    results = run_matching(bank_df, ledger_df)

    st.subheader("Match Summary")
    st.write("Total Potential Matches Found:", len(results["matches"]))


    # ===== SHOW MATCHED ROWS =====

    if results["matches"]:
        st.subheader("Matched Transactions")

        matched_display = []

        for m in results["matches"]:
            row = {
                "Status": m["status"],
                "Ledger Name": m["ledger_row"]["extracted_name"],
                "Bank Name": m["bank_row"]["name"],
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
