import pandas as pd
from ingestion.pdf_parser import extract_pdf_tables

# def detect_header_row(df):
#     """
#     Detect the header row by looking for common transaction column keywords.
#     """

#     header_keywords = ["date", "description", "debit", "credit", "amount", "balance"]

#     for i in range(min(50, len(df))):  # check first 50 rows max
#         row = df.iloc[i].astype(str).str.lower()

#         matches = sum(
#             any(keyword in cell for keyword in header_keywords)
#             for cell in row
#         )

#         if matches >= 3:  # at least 2 expected header keywords
#             return i

#     return 0  # fallback

def detect_header_row(df):
    header_keywords = [
        "date", "description", "amount", "debit", "credit",
        "transaction", "details", "balance"
    ]

    for i in range(min(50, len(df))):
        row = df.iloc[i]

        # 🔑 CRITICAL FIX: force every cell to safe string
        row = row.fillna("").astype(str).str.lower()

        matches = 0
        for cell in row:
            for keyword in header_keywords:
                if keyword in cell:
                    matches += 1
                    break

        if matches >= 2:
            return i

    return 0
def read_csv_smart(file):

    # Load without assuming header
    df_raw = pd.read_csv(file, header=None, dtype=str)

    header_row = detect_header_row(df_raw)

    file.seek(0)
    # Reload with detected header
    df = pd.read_csv(file, header=header_row)
    df = df.dropna(how="all")
    return df

def read_excel_smart(file):

    df_raw = pd.read_excel(file, header=None, engine="openpyxl")

    
    header_row = detect_header_row(df_raw)

    file.seek(0)
    df = pd.read_excel(file, header=header_row)
    df = df.dropna(how="all")
    return df

def read_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = read_csv_smart(uploaded_file)

    elif file_name.endswith((".xlsx", ".xls")):
        df = read_excel_smart(uploaded_file)


    elif file_name.endswith(".pdf"):
        df = extract_pdf_tables(uploaded_file)

    else:
        raise ValueError("Unsupported file format")

    return df