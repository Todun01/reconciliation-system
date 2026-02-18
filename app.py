import streamlit as st
from normalization.column_mapper import map_columns
from normalization.cleaner import clean_dataframe

from ingestion.file_reader import read_file
from matching.engine import run_matching


st.title("Reconciliation System")

file1 = st.file_uploader("Upload Bank Statement", type=["csv","xlsx","pdf"])
file2 = st.file_uploader("Upload Ledger File", type=["csv","xlsx","pdf"])

if file1 and file2:

    df1_raw = read_file(file1)
    df2_raw = read_file(file2)

    map1 = map_columns(df1_raw)
    map2 = map_columns(df2_raw)

    df1 = clean_dataframe(df1_raw, map1, file1.name)
    df2 = clean_dataframe(df2_raw, map2, file2.name)

    st.subheader("Normalized Bank Data")
    st.dataframe(df1.head())

    st.subheader("Normalized Ledger Data")
    st.dataframe(df2.head())

    results = run_matching(df1, df2)

    st.subheader("Match Summary")
    st.write("Total Matches Found:", len(results["matches"]))


    # ===== SHOW MATCHED ROWS =====

    if results["matches"]:
        st.subheader("Matched Transactions")

        matched_display = []

        for m in results["matches"]:
            row = {
                "Ledger Name": m["ledger_row"]["normalized_name"],
                "Bank Name": m["bank_row"]["normalized_name"],
                "Amount": m["ledger_row"]["amount"],
                "Ledger Date": m["ledger_row"]["date"].date(),
                "Bank Date": m["bank_row"]["date"].date(),
                "Name Similarity": m["name_similarity"]
            }
            matched_display.append(row)

        st.dataframe(matched_display)


    # ===== SHOW UNMATCHED =====

    st.subheader("Unmatched Bank Transactions")
    st.dataframe(results["unmatched_df1"])

    st.subheader("Unmatched Ledger Transactions")
    st.dataframe(results["unmatched_df2"])
