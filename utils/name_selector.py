# def name_selector(map, st):
#     print("running name selector with map:", map)
#     text_options = []

#     if "name" in map:
#         text_options.append(("Name", map["name"]))

#     if "description" in map:
#         text_options.append(("Description", map["description"]))

#     if not text_options:
#         st.warning("No suitable text column found in document. Please ensure your file has a 'name' or 'description' column.")
#         return None
    
#     if len(text_options) > 1:
#         text_label = st.selectbox(
#             "Select Bank Text Column for Matching",
#             options=[opt[0] for opt in text_options],
#             key="text_select"
#         )

#         # Get actual column name
#         text_column = dict(text_options)[text_label]
#     else:
#         text_column = text_options[0][1]
        
#     return text_column

def name_selector(file_label, mapping, st):
    options = []

    # Detect available columns
    if "name" in mapping:
        options.append(("Use Name Column", "name"))

    if "description" in mapping:
        options.append(("Use Description Column", "description"))

    # If only ONE option → auto select
    if len(options) == 1:
        selected = options[0]
    else:
        selected = st.selectbox(
            f"Select Column to get customer name from {file_label}",
            options=[opt[0] for opt in options],
            key=file_label
        )

    return selected[1]
