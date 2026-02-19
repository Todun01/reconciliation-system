import pandas as pd
from ingestion.pdf_parser import extract_pdf_tables
import streamlit as st

def read_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif file_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file, engine="openpyxl")


    elif file_name.endswith(".pdf"):
        df = extract_pdf_tables(uploaded_file)

    else:
        raise ValueError("Unsupported file format")

    return df