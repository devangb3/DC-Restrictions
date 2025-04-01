from google import genai
from google.genai import types
import pathlib
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def send_prompt(prompt):
    client = genai.Client(api_key = GEMINI_API_KEY)    
    
    check_path = pathlib.Path("./menu.csv")

    if not check_path.exists():
        raise FileNotFoundError(f"File not found: {check_path}")
    
    sample_file = client.files.upload(
        file=check_path,
    )
    print("My files:")
    for f in client.files.list():
        print("  ", f.name)
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[sample_file, prompt],
    )
    print(response.text)


send_prompt("Summarize this document")