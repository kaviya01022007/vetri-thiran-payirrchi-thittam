from typing import Optional
import json
import time
from google import genai
from google.genai import types
from config import get_settings

_client: Optional[genai.Client] = None

def get_client() -> genai.Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = genai.Client(api_key=settings["api_key"])
    return _client

def generate_text(prompt: str, *, temperature: float = 0.4, max_output_tokens: int = 1200) -> str:
    # NEW USERS KU ITHU THAAN WORK AAGUM - 3.8 is latest GA Sep 2 2026
    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
    ]
    last_error = None
    for model_name in models_to_try:
        try:
            print(f"Trying: {model_name}")
            response = get_client().models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_output_tokens),
            )
            text = (response.text or "").strip()
            if text:
                print(f"Success: {model_name}")
                return text
        except Exception as e:
            last_error = e
            print(f"{model_name} failed: {e}")
            time.sleep(1)
            continue

    raise last_error if last_error else RuntimeError("All models failed")

def generate_json(prompt: str, *, temperature: float = 0.4, max_output_tokens: int = 2000):
    models_to_try = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.5-flash"]
    last_error = None
    text = ""
    for model_name in models_to_try:
        try:
            print(f"Trying JSON: {model_name}")
            response = get_client().models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_output_tokens, response_mime_type="application/json"),
            )
            text = (response.text or "").strip()
            if text:
                break
        except Exception as e:
            last_error = e
            continue

    if not text and last_error:
        raise last_error

    try:
        return json.loads(text)
    except:
        s = text.find("{")
        e = text.rfind("}") + 1
        if s!= -1 and e!= 0:
            return json.loads(text[s:e])
        return json.loads(text)