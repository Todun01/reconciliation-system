import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

def get_openai_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        load_dotenv()
        return os.getenv("OPENAI_API_KEY")
    
def extract_name(text):

    if not text or len(text) < 5:
        return ""

    # --------------------------
    # CLOUD MODE → OpenAI
    # --------------------------
    client = OpenAI(api_key=get_openai_key())

    prompt = f"""
        Extract ONLY the customer's full name from this bank transaction text.

        Rules:
        - Return ONLY the name
        - No explanations
        - No extra words

        Text:
        {text}
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # fast + cheap
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()

