def aggregate_reconciliation(df1, df2):

    # Separate inflows and outflows
    df1_inflow = df1[df1["amount"] > 0]["amount"].sum()
    df1_outflow = df1[df1["amount"] < 0]["amount"].sum()

    df2_inflow = df2[df2["amount"] > 0]["amount"].sum()
    df2_outflow = df2[df2["amount"] < 0]["amount"].sum()

    return {
        "df1_inflow": df1_inflow,
        "df1_outflow": df1_outflow,
        "df2_inflow": df2_inflow,
        "df2_outflow": df2_outflow,
        "inflow_match": abs(df1_inflow - df2_inflow) < 1,
        "outflow_match": abs(df1_outflow - df2_outflow) < 1
    }