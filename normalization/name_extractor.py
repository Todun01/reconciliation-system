import os
import requests
from openai import OpenAI

OLLAMA_URL = "http://localhost:11434/api/generate"

def is_cloud():
    """Detect if running on hosted environment"""
    return os.getenv("OPENAI_API_KEY") is not None


def extract_name(text):

    if not text or len(text) < 5:
        return ""

    # --------------------------
    # CLOUD MODE → OpenAI
    # --------------------------
    if is_cloud():

        client = OpenAI()

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


    # --------------------------
    # LOCAL MODE → Ollama
    # --------------------------
    else:

        prompt = f"""
            Extract ONLY the customer's full name from this bank transaction text.

            Rules:
            - Return ONLY the name
            - No explanations
            - No extra words

            Text:
            {text}
            """

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"].strip()