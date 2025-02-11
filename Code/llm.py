import os
import openai
from dotenv import load_dotenv
load_dotenv()  # Load API key from .env file

openai.api_key = os.getenv("AIPROXY_TOKEN")

def query_llm(prompt):
    """Queries GPT-4o-Mini to extract information."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]
