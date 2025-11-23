"""
DCF (Discounted Cash Flow) Analysis Tool
Performs comprehensive DCF valuation analysis for companies using FMP API data
"""
from typing import Dict, Any, Optional, List
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
import requests


FMP_APP_ID = 'fmp_financial_api'


def make_fmp_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to FMP API"""
    try:
        conn = connections.api_key_auth(FMP_APP_ID)
        base_url = conn.url
        api_key = conn.api_key
        base_url = base_url.rstrip('/')

        url = f"{base_url}/{endpoint}"
        params["apikey"] = api_key

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def calculate_wacc(
    symbol: str,
    risk_free_rate: Optional[float] = None,
    equity_risk_premium: Optional[float] = 5.5
) -> Dict[str, Any]:
    """Calculate Weighted Average Cost of Capital (WACC) for a company.

    Args:
        symbol (str): Stock ticker symbol (e.g., "AAPL", "MSFT")
        risk_free_rate (Optional[float]): Risk-free rate (e.g., 4.5%). If None, uses 10-year Treasury
        equity_risk_premium (Optional[float]): Market risk premium (default 5.5%)

    Returns:
        dict: WACC calculation with components (cost of equity, cost of debt, WACC %)
    """
    # Get key metrics for beta
    metrics_result = make_fmp_request("key-metrics", {"symbol": symbol, "limit": 1})
    if not metrics_result["success"]:
        return {"error": f"Failed to get metrics: {metrics_result['error']}"}

    # Get balance sheet for debt and equity values
    balance_result = make_fmp_request("balance-sheet-statement", {"symbol": symbol, "limit": 1})
    if not balance_result["success"]:
        return {"error": f"Failed to get balance sheet: {balance_result['error']}"}

    # Get income statement for tax rate
    income_result = make_fmp_request("income-statement", {"symbol": symbol, "limit": 1})
    if not income_result["success"]:
        return {"error": f"Failed to get income statement: {income_result['error']}"}

    metrics = metrics_result["data"][0] if metrics_result["data"] else {}
    balance = balance_result["data"][0] if balance_result["data"] else {}
    income = income_result["data"][0] if income_result["data"] else {}

    # Extract values
    beta = metrics.get("beta", 1.0)

    # Use risk-free rate from input or default
    if risk_free_rate is None:
        risk_free_rate = 4.5  # Default 10-year Treasury rate

    # Calculate cost of equity using CAPM: Rf + Beta * (Rm - Rf)
    cost_of_equity = risk_free_rate + (beta * equity_risk_premium)

    # Get debt and equity values
    total_debt = balance.get("totalDebt", 0)
    market_cap = metrics.get("marketCap", 0)

    # Calculate tax rate
    income_before_tax = income.get("incomeBeforeTax", 1)
    income_tax = income.get("incomeTaxExpense", 0)
    tax_rate = (income_tax / income_before_tax * 100) if income_before_tax != 0 else 21.0

    # Get cost of debt (interest expense / total debt)
    interest_expense = income.get("interestExpense", 0)
    cost_of_debt_pre_tax = (abs(interest_expense) / total_debt * 100) if total_debt > 0 else 5.0
    cost_of_debt_after_tax = cost_of_debt_pre_tax * (1 - tax_rate / 100)

    # Calculate weights
    total_value = market_cap + total_debt
    weight_equity = market_cap / total_value if total_value > 0 else 1.0
    weight_debt = total_debt / total_value if total_value > 0 else 0.0

    # Calculate WACC
    wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt_after_tax)

    return {
        "symbol": symbol,
        "wacc_percent": round(wacc, 2),
        "components": {
            "cost_of_equity_percent": round(cost_of_equity, 2),
            "cost_of_debt_after_tax_percent": round(cost_of_debt_after_tax, 2),
            "weight_equity": round(weight_equity, 4),
            "weight_debt": round(weight_debt, 4),
            "beta": round(beta, 2),
            "risk_free_rate_percent": round(risk_free_rate, 2),
            "equity_risk_premium_percent": round(equity_risk_premium, 2),
            "tax_rate_percent": round(tax_rate, 2)
        },
        "capital_structure": {
            "market_cap": market_cap,
            "total_debt": total_debt,
            "total_value": total_value
        }
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def perform_dcf_analysis(
    symbol: str,
    projection_years: int = 5,
    fcf_growth_rate: Optional[float] = None,
    terminal_growth_rate: float = 2.5,
    discount_rate: Optional[float] = None,
    margin_of_safety: float = 20.0
) -> Dict[str, Any]:
    """Perform comprehensive DCF (Discounted Cash Flow) valuation analysis.

    Args:
        symbol (str): Stock ticker symbol (e.g., "AAPL", "MSFT", "TSLA")
        projection_years (int): Number of years to project (default 5, max 10)
        fcf_growth_rate (Optional[float]): Annual FCF growth rate %. If None, calculates from history
        terminal_growth_rate (float): Perpetual growth rate after projection period (default 2.5%)
        discount_rate (Optional[float]): WACC/discount rate %. If None, calculates automatically
        margin_of_safety (float): Desired safety margin % (default 20%)

    Returns:
        dict: Complete DCF analysis with intrinsic value, current price, and recommendation
    """
    # Validate inputs
    projection_years = min(max(1, projection_years), 10)
    terminal_growth_rate = min(max(0, terminal_growth_rate), 5)
    margin_of_safety = min(max(0, margin_of_safety), 50)

    # 1. Get historical cash flow data
    cf_result = make_fmp_request("cash-flow-statement", {"symbol": symbol, "limit": 5})
    if not cf_result["success"]:
        return {"error": f"Failed to get cash flows: {cf_result['error']}"}

    cash_flows = cf_result["data"]
    if not cash_flows or len(cash_flows) < 2:
        return {"error": "Insufficient historical cash flow data"}

    # 2. Get balance sheet for debt and cash
    balance_result = make_fmp_request("balance-sheet-statement", {"symbol": symbol, "limit": 1})
    if not balance_result["success"]:
        return {"error": f"Failed to get balance sheet: {balance_result['error']}"}

    balance = balance_result["data"][0] if balance_result["data"] else {}

    # 3. Get key metrics for shares and current price
    metrics_result = make_fmp_request("key-metrics", {"symbol": symbol, "limit": 1})
    if not metrics_result["success"]:
        return {"error": f"Failed to get metrics: {metrics_result['error']}"}

    metrics = metrics_result["data"][0] if metrics_result["data"] else {}

    # Extract latest FCF
    latest_fcf = cash_flows[0].get("freeCashFlow", 0)

    # Calculate historical FCF growth rate if not provided
    if fcf_growth_rate is None:
        historical_fcfs = [cf.get("freeCashFlow", 0) for cf in cash_flows[::-1]]
        if len(historical_fcfs) >= 2 and historical_fcfs[0] > 0:
            years = len(historical_fcfs) - 1
            cagr = (pow(historical_fcfs[-1] / historical_fcfs[0], 1/years) - 1) * 100
            fcf_growth_rate = min(max(cagr, -10), 30)  # Cap between -10% and 30%
        else:
            fcf_growth_rate = 5.0  # Default conservative growth

    # Calculate discount rate (WACC) if not provided
    if discount_rate is None:
        wacc_result = calculate_wacc(symbol)
        if "error" in wacc_result:
            discount_rate = 10.0  # Default fallback
        else:
            discount_rate = wacc_result["wacc_percent"]

    # 4. Project future free cash flows
    projected_fcfs = []
    current_fcf = latest_fcf

    for year in range(1, projection_years + 1):
        current_fcf = current_fcf * (1 + fcf_growth_rate / 100)
        projected_fcfs.append({
            "year": year,
            "fcf": current_fcf,
            "discount_factor": 1 / pow(1 + discount_rate / 100, year),
            "present_value": current_fcf / pow(1 + discount_rate / 100, year)
        })

    # 5. Calculate terminal value
    terminal_fcf = projected_fcfs[-1]["fcf"] * (1 + terminal_growth_rate / 100)
    terminal_value = terminal_fcf / ((discount_rate - terminal_growth_rate) / 100)
    terminal_pv = terminal_value / pow(1 + discount_rate / 100, projection_years)

    # 6. Calculate enterprise value
    pv_projected_fcfs = sum([fcf["present_value"] for fcf in projected_fcfs])
    enterprise_value = pv_projected_fcfs + terminal_pv

    # 7. Calculate equity value
    total_debt = balance.get("totalDebt", 0)
    cash_and_equivalents = balance.get("cashAndCashEquivalents", 0)
    equity_value = enterprise_value - total_debt + cash_and_equivalents

    # 8. Calculate intrinsic value per share
    shares_outstanding = balance.get("commonStock", 0)
    if shares_outstanding == 0:
        shares_outstanding = metrics.get("sharesOutstanding", 1)

    intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0

    # 9. Get current market price
    current_price = metrics.get("stockPrice", 0)

    # 10. Calculate margin of safety price
    target_price = intrinsic_value_per_share * (1 - margin_of_safety / 100)

    # 11. Generate recommendation
    if current_price == 0:
        recommendation = "Unable to compare - no market price available"
        upside_percent = 0
    else:
        upside_percent = ((intrinsic_value_per_share - current_price) / current_price) * 100

        if current_price <= target_price:
            recommendation = "STRONG BUY - Trading below margin of safety"
        elif current_price < intrinsic_value_per_share:
            recommendation = "BUY - Trading below intrinsic value"
        elif current_price < intrinsic_value_per_share * 1.1:
            recommendation = "HOLD - Fairly valued"
        else:
            recommendation = "OVERVALUED - Trading above intrinsic value"

    return {
        "symbol": symbol,
        "analysis_date": cash_flows[0].get("date", "N/A"),
        "valuation": {
            "intrinsic_value_per_share": round(intrinsic_value_per_share, 2),
            "current_market_price": round(current_price, 2),
            "target_price_with_mos": round(target_price, 2),
            "upside_potential_percent": round(upside_percent, 2)
        },
        "recommendation": recommendation,
        "assumptions": {
            "projection_years": projection_years,
            "fcf_growth_rate_percent": round(fcf_growth_rate, 2),
            "terminal_growth_rate_percent": round(terminal_growth_rate, 2),
            "discount_rate_wacc_percent": round(discount_rate, 2),
            "margin_of_safety_percent": round(margin_of_safety, 2)
        },
        "dcf_calculation": {
            "latest_fcf": latest_fcf,
            "pv_of_projected_fcfs": round(pv_projected_fcfs, 2),
            "terminal_value": round(terminal_value, 2),
            "pv_of_terminal_value": round(terminal_pv, 2),
            "enterprise_value": round(enterprise_value, 2),
            "total_debt": total_debt,
            "cash_and_equivalents": cash_and_equivalents,
            "equity_value": round(equity_value, 2),
            "shares_outstanding": shares_outstanding
        },
        "projected_cash_flows": [
            {
                "year": fcf["year"],
                "fcf": round(fcf["fcf"], 2),
                "present_value": round(fcf["present_value"], 2)
            }
            for fcf in projected_fcfs
        ]
    }


@tool(expected_credentials=[{"app_id": FMP_APP_ID, "type": ConnectionType.API_KEY_AUTH}])
def dcf_sensitivity_analysis(
    symbol: str,
    projection_years: int = 5,
    fcf_growth_rate: Optional[float] = None,
    terminal_growth_range: List[float] = [1.5, 2.0, 2.5, 3.0, 3.5],
    discount_rate_range: List[float] = [8.0, 9.0, 10.0, 11.0, 12.0]
) -> Dict[str, Any]:
    """Perform DCF sensitivity analysis with varying terminal growth and discount rates.

    Args:
        symbol (str): Stock ticker symbol
        projection_years (int): Number of years to project (default 5)
        fcf_growth_rate (Optional[float]): Annual FCF growth rate %. If None, calculates from history
        terminal_growth_range (List[float]): Range of terminal growth rates to test
        discount_rate_range (List[float]): Range of discount rates (WACC) to test

    Returns:
        dict: Sensitivity matrix showing intrinsic values for different assumptions
    """
    results_matrix = []

    for discount_rate in discount_rate_range:
        row = {"discount_rate_percent": discount_rate, "values": []}

        for terminal_growth in terminal_growth_range:
            dcf_result = perform_dcf_analysis(
                symbol=symbol,
                projection_years=projection_years,
                fcf_growth_rate=fcf_growth_rate,
                terminal_growth_rate=terminal_growth,
                discount_rate=discount_rate
            )

            if "error" in dcf_result:
                row["values"].append({"terminal_growth_percent": terminal_growth, "intrinsic_value": None})
            else:
                row["values"].append({
                    "terminal_growth_percent": terminal_growth,
                    "intrinsic_value": dcf_result["valuation"]["intrinsic_value_per_share"]
                })

        results_matrix.append(row)

    # Get base case (middle values)
    base_terminal = terminal_growth_range[len(terminal_growth_range) // 2]
    base_discount = discount_rate_range[len(discount_rate_range) // 2]

    base_case = perform_dcf_analysis(
        symbol=symbol,
        projection_years=projection_years,
        fcf_growth_rate=fcf_growth_rate,
        terminal_growth_rate=base_terminal,
        discount_rate=base_discount
    )

    return {
        "symbol": symbol,
        "sensitivity_matrix": results_matrix,
        "base_case": base_case,
        "ranges_tested": {
            "terminal_growth_range": terminal_growth_range,
            "discount_rate_range": discount_rate_range
        }
    }


if __name__ == "__main__":
    print("Testing DCF Analysis Tool...\n")

    # Test WACC calculation
    print("1. Calculate WACC for Apple (AAPL)")
    wacc_result = calculate_wacc("AAPL")
    if "error" in wacc_result:
        print(f"   Error: {wacc_result['error']}")
    else:
        print(f"   WACC: {wacc_result['wacc_percent']}%")
        print(f"   Cost of Equity: {wacc_result['components']['cost_of_equity_percent']}%")
        print(f"   Cost of Debt (after-tax): {wacc_result['components']['cost_of_debt_after_tax_percent']}%")

    print("\n2. Perform DCF Analysis for Apple (AAPL)")
    dcf_result = perform_dcf_analysis("AAPL", projection_years=5)
    if "error" in dcf_result:
        print(f"   Error: {dcf_result['error']}")
    else:
        print(f"   Intrinsic Value: ${dcf_result['valuation']['intrinsic_value_per_share']}")
        print(f"   Current Price: ${dcf_result['valuation']['current_market_price']}")
        print(f"   Recommendation: {dcf_result['recommendation']}")
        print(f"   Upside: {dcf_result['valuation']['upside_potential_percent']}%")
