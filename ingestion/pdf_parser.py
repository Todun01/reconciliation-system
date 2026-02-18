import pdfplumber
import pandas as pd

def extract_pdf_tables(file):
    all_rows = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()

            if table:
                for row in table:
                    all_rows.append(row)

    df = pd.DataFrame(all_rows)

    return df