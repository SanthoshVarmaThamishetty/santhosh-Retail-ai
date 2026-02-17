import requests
import os

API_KEY = os.getenv("OPENROUTER_API_KEY")

def call_llm(prompt):

    if not API_KEY:
        return "LLM Error: API key not set"

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Retail AI Assistant"
    }

    payload = {
        "model": "openai/gpt-oss-120b:free",
        "messages": [
            {
                "role": "system",
                "content": """
You are a professional retail assistant.

Rules:
- Do NOT use markdown tables.
- Use short sections with emojis.
- Use bullet points.
- Keep answers concise.
- Always list products as bullets.
- Avoid long paragraphs.
- Be friendly but professional.
"""

            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

        print("LLM STATUS:", response.status_code)
        print("LLM RAW RESPONSE:", response.text)

        data = response.json()

        # Same structure as OpenAI SDK
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"LLM Exception: {str(e)}"
