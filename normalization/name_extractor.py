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
Generate a Python regex pattern that accurately extracts ONLY the customer full name.

STRICT RULES:
- DO NOT include r''
- DO NOT include quotes
- DO NOT include backticks
- DO NOT include markdown
- Return ONLY the regex pattern string.
- Must contain exactly one capturing group.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
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

