"""
Financial Analysis Tool - Comprehensive annual report analysis using FMP API
Fetches income statements, balance sheets, cash flow, ratios, and key metrics
Uses watsonx Orchestrate connection for secure credential management
"""
import os
import requests
from typing import Dict, Any, List
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials


# Connection app ID
FMP_APP_ID = 'fmp_financial_api'


def make_fmp_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to make FMP API requests using Watson Orchestrate connection.

    Args:
        endpoint: API endpoint (e.g., 'profile', 'income-statement')
        params: Query parameters (e.g., {'symbol': 'AAPL'})

    Returns:
        dict: API response data or error
    """
    conn = connections.api_key_auth(FMP_APP_ID)
    base_url = conn.url
    api_key = conn.api_key
    base_url = base_url.rstrip('/')

    try:
        url = f"{base_url}/{endpoint}"
        params["apikey"] = api_key

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not data:
            return {"success": False, "error": "No data returned from API"}

        return {"success": True, "data": data}

    except Exception as e:
        return {"success": False, "error": f"API request failed: {str(e)}"}


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def get_company_profile(symbol: str) -> Dict[str, Any]:
    """Get comprehensive company profile including basic information and current metrics.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        dict: Company profile including name, sector, industry, market cap, description, and key details
    """
    result = make_fmp_request("profile", {"symbol": symbol.upper()})

    if not result["success"]:
        result["symbol"] = symbol
        return result

    profile_data = result["data"][0] if isinstance(result["data"], list) else result["data"]

    return {
        "success": True,
        "symbol": profile_data.get("symbol"),
        "company_name": profile_data.get("companyName"),
        "price": profile_data.get("price"),
        "market_cap": profile_data.get("mktCap"),
        "sector": profile_data.get("sector"),
        "industry": profile_data.get("industry"),
        "website": profile_data.get("website"),
        "description": profile_data.get("description"),
        "ceo": profile_data.get("ceo"),
        "employees": profile_data.get("fullTimeEmployees"),
        "city": profile_data.get("city"),
        "state": profile_data.get("state"),
        "country": profile_data.get("country"),
        "exchange": profile_data.get("exchangeShortName"),
        "ipo_date": profile_data.get("ipoDate")
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def get_income_statement(symbol: str, period: str = "annual", limit: int = 100) -> Dict[str, Any]:
    """Get annual or quarterly income statements showing revenue, expenses, and profitability.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period (str): 'annual' or 'quarter' (default: 'annual')
        limit (int): Number of periods to retrieve (default: 5)

    Returns:
        dict: Income statement data including revenue, gross profit, operating income, net income, EPS
    """
    result = make_fmp_request(
        "income-statement",
        {"symbol": symbol.upper(), "period": period, "limit": limit}
        )

    if not result["success"]:
        result["symbol"] = symbol
        return result

    statements = []
    for stmt in result["data"]:
        statements.append({
            "date": stmt.get("date"),
            "fiscal_year": stmt.get("calendarYear"),
            "period": stmt.get("period"),
            "revenue": stmt.get("revenue"),
            "cost_of_revenue": stmt.get("costOfRevenue"),
            "gross_profit": stmt.get("grossProfit"),
            "gross_profit_ratio": stmt.get("grossProfitRatio"),
            "operating_expenses": stmt.get("operatingExpenses"),
            "operating_income": stmt.get("operatingIncome"),
            "operating_income_ratio": stmt.get("operatingIncomeRatio"),
            "net_income": stmt.get("netIncome"),
            "net_income_ratio": stmt.get("netIncomeRatio"),
            "eps": stmt.get("eps"),
            "eps_diluted": stmt.get("epsdiluted"),
            "ebitda": stmt.get("ebitda"),
            "ebitda_ratio": stmt.get("ebitdaratio")
        })

    return {
        "success": True,
        "symbol": symbol,
        "period": period,
        "count": len(statements),
        "statements": statements
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def get_balance_sheet(symbol: str, period: str = "annual", limit: int = 100) -> Dict[str, Any]:
    """Get balance sheet data showing assets, liabilities, and shareholder equity.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period (str): 'annual' or 'quarter' (default: 'annual')
        limit (int): Number of periods to retrieve (default: 5)

    Returns:
        dict: Balance sheet data including total assets, liabilities, equity, cash, debt
    """
    result = make_fmp_request(
        "balance-sheet-statement",
        {"symbol": symbol.upper(), "period": period, "limit": limit}
    )

    if not result["success"]:
        result["symbol"] = symbol
        return result

    statements = []
    for stmt in result["data"]:
        statements.append({
            "date": stmt.get("date"),
            "fiscal_year": stmt.get("calendarYear"),
            "period": stmt.get("period"),
            "cash_and_equivalents": stmt.get("cashAndCashEquivalents"),
            "short_term_investments": stmt.get("shortTermInvestments"),
            "total_current_assets": stmt.get("totalCurrentAssets"),
            "total_assets": stmt.get("totalAssets"),
            "total_current_liabilities": stmt.get("totalCurrentLiabilities"),
            "total_liabilities": stmt.get("totalLiabilities"),
            "short_term_debt": stmt.get("shortTermDebt"),
            "long_term_debt": stmt.get("longTermDebt"),
            "total_debt": stmt.get("totalDebt"),
            "total_stockholders_equity": stmt.get("totalStockholdersEquity"),
            "retained_earnings": stmt.get("retainedEarnings"),
            "total_equity": stmt.get("totalEquity")
        })

    return {
        "success": True,
        "symbol": symbol,
        "period": period,
        "count": len(statements),
        "statements": statements
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def get_cash_flow_statement(symbol: str, period: str = "annual", limit: int = 100) -> Dict[str, Any]:
    """Get cash flow statements showing operating, investing, and financing activities.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period (str): 'annual' or 'quarter' (default: 'annual')
        limit (int): Number of periods to retrieve (default: 5)

    Returns:
        dict: Cash flow data including operating cash flow, investing activities, financing activities, free cash flow
    """
    result = make_fmp_request(
        "cash-flow-statement",
        {"symbol": symbol.upper(), "period": period, "limit": limit}
    )

    if not result["success"]:
        result["symbol"] = symbol
        return result

    statements = []
    for stmt in result["data"]:
        statements.append({
            "date": stmt.get("date"),
            "fiscal_year": stmt.get("calendarYear"),
            "period": stmt.get("period"),
            "operating_cash_flow": stmt.get("operatingCashFlow"),
            "capital_expenditure": stmt.get("capitalExpenditure"),
            "free_cash_flow": stmt.get("freeCashFlow"),
            "investing_cash_flow": stmt.get("netCashUsedForInvestingActivites"),
            "financing_cash_flow": stmt.get("netCashUsedProvidedByFinancingActivities"),
            "net_change_in_cash": stmt.get("netChangeInCash"),
            "dividends_paid": stmt.get("dividendsPaid"),
            "stock_repurchased": stmt.get("commonStockRepurchased"),
            "debt_repayment": stmt.get("debtRepayment")
        })

    return {
        "success": True,
        "symbol": symbol,
        "period": period,
        "count": len(statements),
        "statements": statements
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def get_financial_ratios(symbol: str, period: str = "annual", limit: int = 100) -> Dict[str, Any]:
    """Get comprehensive financial ratios for profitability, liquidity, and efficiency analysis.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period (str): 'annual' or 'quarter' (default: 'annual')
        limit (int): Number of periods to retrieve (default: 100)

    Returns:
        dict: Financial ratios including ROE, ROA, current ratio, debt ratios, profit margins
    """
    result = make_fmp_request(
        "ratios",
        {"symbol": symbol.upper(), "period": period, "limit": limit}
    )

    if not result["success"]:
        result["symbol"] = symbol
        return result

    ratios = []
    for ratio in result["data"]:
        ratios.append({
            "date": ratio.get("date"),
            "fiscal_year": ratio.get("calendarYear"),
            "period": ratio.get("period"),
            # Profitability Ratios
            "gross_profit_margin": ratio.get("grossProfitMargin"),
            "operating_profit_margin": ratio.get("operatingProfitMargin"),
            "net_profit_margin": ratio.get("netProfitMargin"),
            "return_on_equity": ratio.get("returnOnEquity"),
            "return_on_assets": ratio.get("returnOnAssets"),
            # Liquidity Ratios
            "current_ratio": ratio.get("currentRatio"),
            "quick_ratio": ratio.get("quickRatio"),
            "cash_ratio": ratio.get("cashRatio"),
            # Leverage Ratios
            "debt_ratio": ratio.get("debtRatio"),
            "debt_equity_ratio": ratio.get("debtEquityRatio"),
            # Efficiency Ratios
            "asset_turnover": ratio.get("assetTurnover"),
            "inventory_turnover": ratio.get("inventoryTurnover"),
            # Valuation
            "price_earnings_ratio": ratio.get("priceEarningsRatio"),
            "price_to_book_ratio": ratio.get("priceToBookRatio")
        })

    return {
        "success": True,
        "symbol": symbol,
        "period": period,
        "count": len(ratios),
        "ratios": ratios
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def get_key_metrics(symbol: str, period: str = "annual", limit: int = 100) -> Dict[str, Any]:
    """Get key financial metrics and valuation indicators.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period (str): 'annual' or 'quarter' (default: 'annual')
        limit (int): Number of periods to retrieve (default: 5)

    Returns:
        dict: Key metrics including market cap, P/E ratio, revenue per share, book value, dividends
    """
    result = make_fmp_request(
        "key-metrics",
        {"symbol": symbol.upper(), "period": period, "limit": limit}
    )

    if not result["success"]:
        result["symbol"] = symbol
        return result

    metrics = []
    for metric in result["data"]:
        metrics.append({
            "date": metric.get("date"),
            "fiscal_year": metric.get("calendarYear"),
            "period": metric.get("period"),
            "market_cap": metric.get("marketCap"),
            "pe_ratio": metric.get("peRatio"),
            "price_to_sales_ratio": metric.get("priceToSalesRatio"),
            "price_to_book_ratio": metric.get("pbRatio"),
            "ev_to_sales": metric.get("enterpriseValueOverEBITDA"),
            "revenue_per_share": metric.get("revenuePerShare"),
            "net_income_per_share": metric.get("netIncomePerShare"),
            "book_value_per_share": metric.get("bookValuePerShare"),
            "operating_cash_flow_per_share": metric.get("operatingCashFlowPerShare"),
            "free_cash_flow_per_share": metric.get("freeCashFlowPerShare"),
            "dividend_yield": metric.get("dividendYield"),
            "payout_ratio": metric.get("payoutRatio")
        })

    return {
        "success": True,
        "symbol": symbol,
        "period": period,
        "count": len(metrics),
        "metrics": metrics
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def get_comprehensive_analysis(symbol: str, years: int = 3) -> Dict[str, Any]:
    """Get a comprehensive financial analysis package including all financial statements, ratios, and metrics.

    This is the primary tool for annual report analysis. It fetches:
    - Company profile and overview
    - Income statements (revenue, profitability)
    - Balance sheets (assets, liabilities, equity)
    - Cash flow statements (operating, investing, financing)
    - Financial ratios (profitability, liquidity, leverage)
    - Key metrics (valuation, per-share data)

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        years (int): Number of years of historical data to retrieve (default: 3, max: 10)

    Returns:
        dict: Comprehensive financial analysis with all statements, ratios, and metrics
    """
    symbol = symbol.upper()
    years = min(years, 10)  # Cap at 10 years

    # Make API requests directly instead of calling other tool functions
    profile_result = make_fmp_request("profile", {"symbol": symbol})
    income_result = make_fmp_request("income-statement", {"symbol": symbol, "period": "annual", "limit": years})
    balance_result = make_fmp_request("balance-sheet-statement", {"symbol": symbol, "period": "annual", "limit": years})
    cash_flow_result = make_fmp_request("cash-flow-statement", {"symbol": symbol, "period": "annual", "limit": years})
    ratios_result = make_fmp_request("ratios", {"symbol": symbol, "period": "annual", "limit": years})
    metrics_result = make_fmp_request("key-metrics", {"symbol": symbol, "period": "annual", "limit": years})

    # Check if any critical data failed
    failures = []
    if not profile_result.get("success"):
        failures.append(f"Profile: {profile_result.get('error')}")
    if not income_result.get("success"):
        failures.append(f"Income Statement: {income_result.get('error')}")
    if not balance_result.get("success"):
        failures.append(f"Balance Sheet: {balance_result.get('error')}")
    if not cash_flow_result.get("success"):
        failures.append(f"Cash Flow: {cash_flow_result.get('error')}")

    if failures:
        return {
            "success": False,
            "symbol": symbol,
            "error": "Failed to retrieve some financial data",
            "failures": failures
        }

    # Extract profile data
    profile_data = profile_result["data"][0] if isinstance(profile_result["data"], list) else profile_result["data"]

    # Process income statements
    income_statements = []
    for stmt in income_result.get("data", []):
        income_statements.append({
            "date": stmt.get("date"),
            "fiscal_year": stmt.get("calendarYear"),
            "revenue": stmt.get("revenue"),
            "gross_profit": stmt.get("grossProfit"),
            "operating_income": stmt.get("operatingIncome"),
            "net_income": stmt.get("netIncome"),
            "eps": stmt.get("eps")
        })

    # Process balance sheets
    balance_sheets = []
    for stmt in balance_result.get("data", []):
        balance_sheets.append({
            "date": stmt.get("date"),
            "fiscal_year": stmt.get("calendarYear"),
            "total_assets": stmt.get("totalAssets"),
            "total_liabilities": stmt.get("totalLiabilities"),
            "total_equity": stmt.get("totalEquity"),
            "total_debt": stmt.get("totalDebt")
        })

    # Process cash flows
    cash_flows = []
    for stmt in cash_flow_result.get("data", []):
        cash_flows.append({
            "date": stmt.get("date"),
            "fiscal_year": stmt.get("calendarYear"),
            "operating_cash_flow": stmt.get("operatingCashFlow"),
            "free_cash_flow": stmt.get("freeCashFlow")
        })

    return {
        "success": True,
        "symbol": symbol,
        "analysis_period_years": years,
        "company_profile": {
            "symbol": profile_data.get("symbol"),
            "company_name": profile_data.get("companyName"),
            "sector": profile_data.get("sector"),
            "industry": profile_data.get("industry"),
            "market_cap": profile_data.get("mktCap"),
            "price": profile_data.get("price")
        },
        "income_statements": income_statements,
        "balance_sheets": balance_sheets,
        "cash_flow_statements": cash_flows,
        "financial_ratios": ratios_result.get("data", []),
        "key_metrics": metrics_result.get("data", []),
        "summary": {
            "company_name": profile_data.get("companyName"),
            "sector": profile_data.get("sector"),
            "industry": profile_data.get("industry"),
            "current_price": profile_data.get("price"),
            "market_cap": profile_data.get("mktCap"),
            "years_analyzed": years,
            "latest_fiscal_year": income_statements[0].get("fiscal_year") if income_statements else None
        }
    }
