import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")


def generate_response(prompt: str):
    try:
        response = model.generate_content(prompt)

        if not response.candidates:
            return "{}"

        text = response.candidates[0].content.parts[0].text

        return text

    except Exception as e:
        print("LLM Error:", e)
        return "{}"
