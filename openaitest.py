import requests
from config import GOOGLE_API_KEY


def _friendly_gemini_error(error: Exception) -> str:
    err = str(error)
    if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
        return "Gemini quota exceeded. Please check Google billing or quota limits."
    if "API_KEY_INVALID" in err or "invalid" in err.lower() and "key" in err.lower():
        return "Gemini API key is invalid. Please update GOOGLE_API_KEY in config.py."
    return "Gemini request failed. Please try again later."


def gemini_test(prompt: str) -> str:
    params = {"key": GOOGLE_API_KEY}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 256},
    }
    models = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"]
    last_err = None

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        response = requests.post(url, params=params, json=body, timeout=20)
        if response.status_code == 404:
            last_err = f"Model not found: {model}"
            continue
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    raise RuntimeError(last_err or "Gemini request failed")


if __name__ == "__main__":
    try:
        print(gemini_test("Write an email to my boss for resignation?"))
    except Exception as e:
        print(_friendly_gemini_error(e))
