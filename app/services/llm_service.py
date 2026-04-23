import requests

from app.config import Config


def generate_from_llm(prompt: str):
    if not Config.BASE_URL:
        raise Exception("GEMINI_BASE_URL belum diisi")
    if not Config.LLM_TOKEN:
        raise Exception("GEMINI_API_KEY belum diisi")

    response = requests.post(
        f"{Config.BASE_URL}/models/{Config.GEMINI_MODEL}:generateContent",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": Config.LLM_TOKEN,
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.8,
            },
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise Exception(f"LLM request failed: {response.status_code} {response.text}")

    return response.json()
