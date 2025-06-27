import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_web(query):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "SerpAPI key not found."

    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google",
        "num": 3,
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        results = response.json()
        snippets = []

        for result in results.get("organic_results", []):
            if "snippet" in result:
                snippets.append(result["snippet"])

        return "\n\n".join(snippets[:3]) if snippets else "No relevant results found."

    except Exception as e:
        return f"Search error: {str(e)}"
