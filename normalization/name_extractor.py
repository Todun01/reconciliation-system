import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import re 

def get_openai_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        load_dotenv()
        return os.getenv("OPENAI_API_KEY")
    
client = OpenAI(api_key=get_openai_key()) 
def extract_date_period(text):
    prompt = f"""
Extract the date from the following text.

Rules:
- Identify phrases like "FOR 6TH FEB 2026", "AS AT 13TH FEB 2026".
- Convert the extracted date into ISO format: YYYY-MM-DD.
- Ignore all other text.
- If no date is found, return null.

Text: "{text}"

Output:
"""

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=1
    )

    date = response.choices[0].message.content.strip()
    if date.lower() == "null":
        return None
    return date

def generate_regex_from_sample(sample_text):
    """
    Uses AI once to generate a regex pattern that extracts
    customer name from transaction description.
    Returns raw regex string.
    """

    prompt = f"""
You are a Python regex expert.

Given this transaction receipt description:



{sample_text}



Observe the text and accurately identify the customer name within the transaction receipt description.
Generate a Python regex pattern that accurately extracts ONLY the customer full name, and that would still extract if hyphenated. 

STRICT RULES:
- DO NOT include r''
- DO NOT include quotes
- DO NOT include backticks
- DO NOT include markdown
- Return ONLY the regex pattern string. 
- Must contain exactly one capturing group.
"""

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=1
    )

    pattern = response.choices[0].message.content.strip()

    return pattern

def validate_pattern(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False
    
def extract_name(text, pattern):
    match = re.search(pattern, str(text))
    if match:
        return match.group(1).strip()
    return ""

