"""
Stock Price Tool - Fetches real-time stock prices from Financial Modeling Prep API
Uses watsonx Orchestrate connection environment variables for secure credential management
"""
import os
import requests
from typing import Dict, Any
from ibm_watsonx_orchestrate.agent_builder.tools import tool


def get_connection_config() -> Dict[str, str]:
    """
    Retrieve connection configuration from environment variables.
    Uses watsonx Orchestrate naming convention: WXO_CONNECTION_<app_id>_<field>
    """
    app_id = "stock_tool"

    config = {
        "api_key": os.getenv(f"WXO_CONNECTION_{app_id}_api_key"),
        "base_url": os.getenv(f"WXO_CONNECTION_{app_id}_base_url", "https://financialmodelingprep.com/api/v3")
    }

    # Fallback to direct environment variables if WXO_ prefixed ones not found
    if not config["api_key"]:
        config["api_key"] = os.getenv("FMP_API_KEY")

    return config


@tool()
def get_stock_price(symbol: str) -> Dict[str, Any]:
    """Fetch current stock price for a given symbol.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')

    Returns:
        dict: Dictionary containing stock price information including price, change, volume, and market data
    """
    config = get_connection_config()

    if not config["api_key"]:
        return {
            "success": False,
            "error": "API key not configured. Please set WXO_CONNECTION_stock_tool_api_key or FMP_API_KEY environment variable.",
            "symbol": symbol
        }

    try:
        url = f"{config['base_url']}/quote/{symbol.upper()}"
        params = {"apikey": config["api_key"]}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data or len(data) == 0:
            return {
                "success": False,
                "error": f"No data found for symbol: {symbol}",
                "symbol": symbol
            }

        stock_data = data[0]

        return {
            "success": True,
            "symbol": stock_data.get("symbol"),
            "name": stock_data.get("name"),
            "price": stock_data.get("price"),
            "change": stock_data.get("change"),
            "change_percent": stock_data.get("changesPercentage"),
            "day_low": stock_data.get("dayLow"),
            "day_high": stock_data.get("dayHigh"),
            "year_low": stock_data.get("yearLow"),
            "year_high": stock_data.get("yearHigh"),
            "market_cap": stock_data.get("marketCap"),
            "volume": stock_data.get("volume"),
            "avg_volume": stock_data.get("avgVolume"),
            "open": stock_data.get("open"),
            "previous_close": stock_data.get("previousClose"),
            "eps": stock_data.get("eps"),
            "pe": stock_data.get("pe"),
            "timestamp": stock_data.get("timestamp")
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. Please try again.",
            "symbol": symbol
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "symbol": symbol
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching stock data: {str(e)}",
            "symbol": symbol
        }


@tool()
def get_multiple_stocks(symbols: str) -> Dict[str, Any]:
    """Fetch stock prices for multiple symbols.

    Args:
        symbols (str): Comma-separated list of stock ticker symbols (e.g., 'AAPL,GOOGL,MSFT')

    Returns:
        dict: Dictionary containing data for all requested symbols
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    results = {}

    for symbol in symbol_list:
        if symbol:
            results[symbol] = get_stock_price(symbol)

    return {
        "success": True,
        "count": len(results),
        "stocks": results
    }


@tool()
def search_stock(query: str) -> Dict[str, Any]:
    """Search for stocks by company name or symbol.

    Args:
        query (str): Search query (company name or ticker symbol)

    Returns:
        dict: Dictionary containing search results with stock symbols and company information
    """
    config = get_connection_config()

    if not config["api_key"]:
        return {
            "success": False,
            "error": "API key not configured. Please set WXO_CONNECTION_stock_tool_api_key or FMP_API_KEY environment variable."
        }

    try:
        url = f"{config['base_url']}/search"
        params = {
            "query": query,
            "limit": 10,
            "apikey": config["api_key"]
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data:
            return {
                "success": False,
                "error": f"No results found for: {query}"
            }

        results = []
        for item in data:
            results.append({
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "currency": item.get("currency"),
                "stock_exchange": item.get("stockExchange"),
                "exchange_short": item.get("exchangeShortName")
            })

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Search failed: {str(e)}",
            "query": query
        }


if __name__ == "__main__":
    print("Testing stock price tool...")

    print("\n1. Getting Apple stock price:")
    result = get_stock_price("AAPL")
    print(result)

    print("\n2. Searching for 'Apple':")
    search_result = search_stock("Apple")
    print(search_result)

    print("\n3. Getting multiple stocks:")
    multi_result = get_multiple_stocks("AAPL,MSFT,GOOGL")
    print(multi_result)
