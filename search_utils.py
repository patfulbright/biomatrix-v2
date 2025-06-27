from serpapi.google_search_results import GoogleSearch
import os

def search_web(query):
    params = {
        "q": query,
        "engine": "google",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    snippets = []

    for result in results.get("organic_results", [])[:3]:
        if "snippet" in result:
            snippets.append(result["snippet"])

    return " ".join(snippets)
