def build_amount_config(file_label, mapping, st):

    options = []
    config = {
        "mode": None,
        "debit_col": None,
        "credit_col": None,
        "amount_col": None
    }

    # Detect available columns
    if "amount" in mapping:
        options.append("Use Amount Column")
        config["amount_col"] = mapping["amount"]

    if "debit" in mapping:
        options.append("Use Debit Only")
        config["debit_col"] = mapping["debit"]

    if "credit" in mapping:
        options.append("Use Credit Only")
        config["credit_col"] = mapping["credit"]

    if "debit" in mapping and "credit" in mapping:
        options.append("Combine Debit + Credit")

    # If only ONE option → auto select
    if len(options) == 1:
        selected = options[0]
    else:
        selected = st.selectbox(
            f"Select Amount Mode for {file_label}",
            options,
            key=file_label
        )

    # Translate selection into config
    if selected == "Use Amount Column":
        config["mode"] = "amount"

    elif selected == "Use Debit Only":
        config["mode"] = "debit"

    elif selected == "Use Credit Only":
        config["mode"] = "credit"

    elif selected == "Combine Debit + Credit":
        config["mode"] = "combine"

    return config