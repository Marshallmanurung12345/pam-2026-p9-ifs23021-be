import requests

from app.config import Config


class LLMServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _extract_error_message(error_payload):
    if isinstance(error_payload, dict):
        error = error_payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            status = error.get("status")

            if status == "RESOURCE_EXHAUSTED" or "quota" in (message or "").lower():
                return "Kuota layanan AI sedang habis. Coba lagi beberapa saat lagi."

            if message:
                return message

    return "Layanan AI gagal memproses permintaan."


def generate_from_llm(prompt: str):
    if not Config.BASE_URL:
        raise LLMServiceError("GEMINI_BASE_URL belum diisi", 500)
    if not Config.LLM_TOKEN:
        raise LLMServiceError("GEMINI_API_KEY belum diisi", 500)

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
        try:
            error_payload = response.json()
        except Exception:
            error_payload = response.text
        message = _extract_error_message(error_payload)
        status_code = 429 if response.status_code == 429 else 502
        raise LLMServiceError(message, status_code)

    return response.json()
