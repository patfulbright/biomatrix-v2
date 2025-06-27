from serpapi import GoogleSearch
import os

def search_web(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    snippets = []

    for result in results.get("organic_results", [])[:3]:
        snippet = result.get("snippet", "")
        if snippet:
            snippets.append(snippet)

    return " ".join(snippets)
