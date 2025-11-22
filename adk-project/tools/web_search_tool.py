"""
Web Search Tool - DuckDuckGo-based web search for gathering market intelligence and news
Provides web search capabilities without requiring API keys
"""
from typing import Dict, List
from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool()
def web_search(query: str, max_results: int = 5) -> Dict:
    """Search the web using DuckDuckGo for recent news, market trends, and company information.

    Args:
        query (str): The search query (e.g., "Apple quarterly earnings 2024", "Tesla stock news")
        max_results (int): Maximum number of results to return (default 5, max 10)

    Returns:
        dict: Search results containing titles, snippets, and URLs
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return {
            "error": "duckduckgo-search library not installed. Please install it with: pip install duckduckgo-search",
            "query": query
        }

    # Limit max_results to reasonable range
    max_results = min(max(1, max_results), 10)

    try:
        ddgs = DDGS()
        results = []

        # Get search results - ddgs.text returns a generator
        search_results = list(ddgs.text(query, max_results=max_results))

        for idx, result in enumerate(search_results, 1):
            results.append({
                "position": idx,
                "title": result.get("title", "No title"),
                "snippet": result.get("body", "No description available"),
                "url": result.get("href", ""),
                "source": result.get("source", "Unknown")
            })

        return {
            "query": query,
            "num_results": len(results),
            "results": results,
            "success": True
        }
    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}",
            "query": query,
            "success": False,
            "num_results": 0,
            "results": []
        }


@tool()
def web_search_news(query: str, max_results: int = 5) -> Dict:
    """Search for recent news articles using DuckDuckGo News search.

    Args:
        query (str): The news search query (e.g., "Microsoft earnings", "tech sector trends")
        max_results (int): Maximum number of news articles to return (default 5, max 10)

    Returns:
        dict: News articles with titles, snippets, URLs, and publication dates
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return {
            "error": "duckduckgo-search library not installed. Please install it with: pip install duckduckgo-search",
            "query": query
        }

    # Limit max_results to reasonable range
    max_results = min(max(1, max_results), 10)

    try:
        ddgs = DDGS()
        results = []

        # Get news results - ddgs.news returns a generator
        news_results = list(ddgs.news(query, max_results=max_results))

        for idx, result in enumerate(news_results, 1):
            results.append({
                "position": idx,
                "title": result.get("title", "No title"),
                "snippet": result.get("body", "No description available"),
                "url": result.get("url", ""),
                "source": result.get("source", "Unknown"),
                "date": result.get("date", "Date not available")
            })

        return {
            "query": query,
            "num_results": len(results),
            "results": results,
            "success": True
        }
    except Exception as e:
        return {
            "error": f"News search failed: {str(e)}",
            "query": query,
            "success": False,
            "num_results": 0,
            "results": []
        }


if __name__ == "__main__":
    print("Testing Web Search Tool...\n")

    # Test general web search
    print("1. General Web Search: 'Apple stock performance 2024'")
    result1 = web_search("Apple stock performance 2024", max_results=3)
    print(f"Success: {result1.get('success')}")
    print(f"Query: {result1.get('query')}")
    print(f"Results found: {result1.get('num_results')}")

    if result1.get('error'):
        print(f"Error: {result1.get('error')}")
    elif result1.get('results'):
        for r in result1['results'][:2]:
            print(f"  - {r['title']}")
            print(f"    Snippet: {r['snippet'][:100]}...")
            print(f"    URL: {r['url']}")
    else:
        print("  No results returned")
    print()

    # Test news search
    print("2. News Search: 'Tesla quarterly earnings'")
    result2 = web_search_news("Tesla quarterly earnings", max_results=3)
    print(f"Success: {result2.get('success')}")
    print(f"Query: {result2.get('query')}")
    print(f"Results found: {result2.get('num_results')}")

    if result2.get('error'):
        print(f"Error: {result2.get('error')}")
    elif result2.get('results'):
        for r in result2['results'][:2]:
            print(f"  - {r['title']}")
            print(f"    Source: {r.get('source')}, Date: {r.get('date')}")
            print(f"    URL: {r['url']}")
    else:
        print("  No results returned")
