import requests
import os

SERP_API_KEY = os.getenv("SERP_API_KEY")

def web_search(query):

    if not SERP_API_KEY:
        return "No SERP API key configured."

    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "num": 5
    }

    r = requests.get(url, params=params, timeout=30)
    data = r.json()

    snippets = []

    for result in data.get("organic_results", []):
        snippets.append(result.get("snippet", ""))

    return "\n".join(snippets[:5])
