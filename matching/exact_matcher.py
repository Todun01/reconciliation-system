import pandas as pd

def exact_match(df1, df2):
    matches = []

    df1 = df1.copy()
    df2 = df2.copy()

    df1["matched"] = False
    df2["matched"] = False

    for i, row1 in df1.iterrows():
        for j, row2 in df2.iterrows():

            if df2.loc[j, "matched"]:
                continue

            # Exact matching conditions
            if (
                row1["amount"] == row2["amount"]
                and row1["date"] == row2["date"]
            ):
                matches.append((i, j))

                df1.at[i, "matched"] = True
                df2.at[j, "matched"] = True
                break

    return matches, df1, df2