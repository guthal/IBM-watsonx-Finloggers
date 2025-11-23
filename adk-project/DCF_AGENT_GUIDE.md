# DCF Analyst Agent - Complete Guide

## 📊 Overview

The **DCF Analyst Agent** is a specialized AI agent that performs comprehensive Discounted Cash Flow (DCF) valuation analysis to determine the intrinsic value of stocks.

### What is DCF Analysis?

DCF values a company by:
1. Projecting future free cash flows
2. Discounting them to present value using WACC
3. Adding terminal value for perpetual growth
4. Adjusting for debt and cash to get equity value
5. Dividing by shares outstanding for per-share value

## 🎯 What It Does

### Core Capabilities:

1. **WACC Calculation** - Computes weighted average cost of capital
2. **DCF Valuation** - Full intrinsic value analysis with buy/sell recommendation
3. **Sensitivity Analysis** - Tests multiple scenarios for range of values

### Example Use Cases:

- "What's Apple's intrinsic value?"
- "Is Tesla undervalued?"
- "Perform DCF analysis on Microsoft with 10-year projection"
- "Show me sensitivity analysis for NVIDIA"
- "What's Google's WACC?"

## 🛠️ Tools Created

### 1. `calculate_wacc`

**Purpose**: Calculate Weighted Average Cost of Capital

**Parameters**:
- `symbol` (required): Stock ticker (e.g., "AAPL")
- `risk_free_rate` (optional): Risk-free rate % (default: 4.5%)
- `equity_risk_premium` (optional): Market risk premium % (default: 5.5%)

**Returns**:
```json
{
  "symbol": "AAPL",
  "wacc_percent": 9.45,
  "components": {
    "cost_of_equity_percent": 10.2,
    "cost_of_debt_after_tax_percent": 3.5,
    "weight_equity": 0.85,
    "weight_debt": 0.15,
    "beta": 1.2,
    "tax_rate_percent": 21.0
  }
}
```

### 2. `perform_dcf_analysis`

**Purpose**: Complete DCF valuation analysis

**Parameters**:
- `symbol` (required): Stock ticker
- `projection_years` (default: 5): Number of years to project (1-10)
- `fcf_growth_rate` (optional): FCF growth % (auto-calculates from history if not provided)
- `terminal_growth_rate` (default: 2.5%): Perpetual growth rate (0-5%)
- `discount_rate` (optional): WACC % (auto-calculates if not provided)
- `margin_of_safety` (default: 20%): Safety margin % (0-50%)

**Returns**:
```json
{
  "symbol": "AAPL",
  "valuation": {
    "intrinsic_value_per_share": 185.50,
    "current_market_price": 175.00,
    "target_price_with_mos": 148.40,
    "upside_potential_percent": 6.0
  },
  "recommendation": "BUY - Trading below intrinsic value",
  "assumptions": {
    "projection_years": 5,
    "fcf_growth_rate_percent": 8.5,
    "terminal_growth_rate_percent": 2.5,
    "discount_rate_wacc_percent": 9.45,
    "margin_of_safety_percent": 20.0
  },
  "dcf_calculation": {
    "latest_fcf": 99000000000,
    "pv_of_projected_fcfs": 450000000000,
    "terminal_value": 2500000000000,
    "pv_of_terminal_value": 1600000000000,
    "enterprise_value": 2050000000000
  },
  "projected_cash_flows": [
    {"year": 1, "fcf": 107415000000, "present_value": 98150000000},
    {"year": 2, "fcf": 116544975000, "present_value": 97350000000}
  ]
}
```

### 3. `dcf_sensitivity_analysis`

**Purpose**: Test DCF under multiple scenarios

**Parameters**:
- `symbol` (required): Stock ticker
- `projection_years` (default: 5): Years to project
- `fcf_growth_rate` (optional): FCF growth %
- `terminal_growth_range` (default: [1.5, 2.0, 2.5, 3.0, 3.5]): Terminal growth rates to test
- `discount_rate_range` (default: [8.0, 9.0, 10.0, 11.0, 12.0]): Discount rates to test

**Returns**: Matrix showing intrinsic value for each combination of assumptions

## 📋 Parameter Guidelines

### Projection Years
- **Conservative**: 5 years
- **Standard**: 7-10 years
- **Aggressive**: 10 years

### FCF Growth Rate
- **Mature Companies**: 3-7%
- **Growth Companies**: 10-20%
- **High-Growth Tech**: 20-30%
- **Auto-calculate**: Leave blank to calculate from historical CAGR

### Terminal Growth Rate
- **Conservative**: 1-2% (below GDP)
- **Standard**: 2-3% (around GDP)
- **Aggressive**: 3-4%
- **Max**: 5% (unrealistic beyond this)

### Discount Rate (WACC)
- **Low Risk**: 6-8%
- **Average**: 8-10%
- **Tech/Growth**: 10-12%
- **High Risk**: 12-15%
- **Auto-calculate**: Leave blank to compute from company data

### Margin of Safety
- **Aggressive**: 10-15%
- **Standard**: 20-25%
- **Conservative**: 30-40%
- **Warren Buffett**: 40-50%

## 🚀 Deployment Instructions

### Step 1: Import DCF Tool

```bash
cd /home/guthal/Finloggers/IBM-watsonx-Finloggers/adk-project
orchestrate tools import -k python -f tools/dcf_analysis_tool.py -r tools/requirements.txt
```

### Step 2: Import DCF Agent

```bash
orchestrate agents import -f agents/dcf-analyst-agent.yaml
```

### Step 3: Re-import Financial Analyst Agent

```bash
orchestrate agents import -f agents/financial-analyst-agent.yaml
```

This updates the Financial Analyst Agent to collaborate with the DCF Agent.

## 🤝 Agent Collaboration

The DCF Agent works with:

### Financial Analyst Agent
- **When**: User needs both fundamental analysis + valuation
- **Example**: "Is Apple a good investment?" → Financial Analyst gets fundamentals + delegates DCF

### Math Agent
- **When**: Complex calculations or verification needed
- **Example**: Custom formulas or validation requests

## 💬 Example Interactions

### Example 1: Simple Valuation

**User**: "What's Tesla's intrinsic value?"

**DCF Agent**:
1. Calls `perform_dcf_analysis("TSLA")`
2. Presents formatted results:
   - Intrinsic Value: $XXX
   - Current Price: $XXX
   - Recommendation: BUY/HOLD/OVERVALUED
   - Upside: X%

### Example 2: Custom Parameters

**User**: "Run DCF on Microsoft with 10-year projection and 12% growth"

**DCF Agent**:
1. Calls `perform_dcf_analysis("MSFT", projection_years=10, fcf_growth_rate=12)`
2. Notes: "Using 12% FCF growth is aggressive - consider sensitivity analysis"
3. Shows results

### Example 3: Comprehensive Analysis

**User**: "Give me full DCF for Apple with scenarios"

**DCF Agent**:
1. Calls `perform_dcf_analysis("AAPL")` for base case
2. Calls `dcf_sensitivity_analysis("AAPL")` for scenarios
3. Shows: "Intrinsic value ranges from $XXX to $XXX depending on assumptions"

### Example 4: Via Financial Analyst

**User**: "Should I buy Apple?"

**Financial Analyst Agent**:
1. Gets comprehensive financial analysis
2. Searches for recent news
3. **Delegates to DCF_Analyst_Agent**: "Perform DCF analysis for Apple"
4. Combines all insights:
   - Fundamentals: Strong revenue growth...
   - News: Positive sentiment...
   - Valuation: Intrinsic value $XXX vs price $XXX
   - **Recommendation**: BUY (fundamentally sound + undervalued)

## 📊 Output Format

The DCF Agent provides structured, professional output:

```
# 📊 DCF Valuation: Apple Inc. (AAPL)

## 💰 Valuation Summary
- Intrinsic Value per Share: $185.50
- Current Market Price: $175.00
- Target Buy Price (w/ 20% MOS): $148.40
- Upside Potential: +6.0%

## ✅ Recommendation: BUY - Trading below intrinsic value

Based on discounted cash flow analysis, Apple appears undervalued by approximately 6% compared to its intrinsic value.

## 🔍 Assumptions Used
- Projection Period: 5 years
- FCF Growth Rate: 8.5% (based on 5-year historical CAGR)
- Terminal Growth Rate: 2.5%
- Discount Rate (WACC): 9.45%
- Margin of Safety: 20%

## 📈 DCF Calculation Breakdown

**Enterprise Value Components:**
- PV of Projected FCFs (Years 1-5): $450.0B
- PV of Terminal Value: $1,600.0B
- Total Enterprise Value: $2,050.0B

**Equity Value Adjustments:**
- Less: Total Debt: $110.0B
- Plus: Cash & Equivalents: $62.0B
- Equity Value: $2,002.0B

**Per Share Calculation:**
- Shares Outstanding: 15.55B
- Intrinsic Value per Share: $185.50

## 💭 Investment Insight

Apple's strong free cash flow generation and moderate growth trajectory support a higher valuation than the current market price. The 6% upside provides a reasonable margin for error. However, ensure this aligns with your investment time horizon and risk tolerance.

📌 Disclaimer: This DCF analysis is a model-based estimate. Conduct your own research before making investment decisions.
```

## ⚠️ Limitations & Warnings

### When DCF May Not Work:
1. **Negative/Inconsistent FCF**: Early-stage or unprofitable companies
2. **Financial Companies**: Use DDM or P/B instead
3. **Cyclical Industries**: FCF varies widely - use normalized averages
4. **Recent IPOs**: Insufficient historical data

### Red Flags the Agent Mentions:
- Recent negative FCF
- Very high debt levels
- Aggressive growth assumptions
- Limited historical data

## 🔧 Technical Details

### Files Created:

1. **`tools/dcf_analysis_tool.py`** (471 lines)
   - 3 tools: calculate_wacc, perform_dcf_analysis, dcf_sensitivity_analysis
   - Uses FMP API for financial data
   - Comprehensive error handling
   - Auto-calculation of missing parameters

2. **`agents/dcf-analyst-agent.yaml`** (305 lines)
   - Detailed instructions for DCF methodology
   - Parameter guidelines
   - Communication style
   - Collaboration with other agents

3. **`agents/financial-analyst-agent.yaml`** (updated)
   - Added DCF_Analyst_Agent to collaborators
   - Instructions on when to delegate valuation queries

### Dependencies:

All dependencies already in `tools/requirements.txt`:
- `requests>=2.31.0`
- `ibm-watsonx-orchestrate-adk`
- `duckduckgo-search>=4.0.0`

### API Integration:

Uses same FMP API connection as Financial Analyst Agent:
- Connection ID: `fmp_financial_api`
- Configured in `tools/fmp_connection.yaml`

## 📚 References

### DCF Methodology:
- Enterprise Value = PV(Projected FCFs) + PV(Terminal Value)
- Equity Value = Enterprise Value - Net Debt + Cash
- Intrinsic Value per Share = Equity Value / Shares Outstanding

### Formulas Used:

**WACC**:
```
WACC = (E/V × Re) + (D/V × Rd × (1-T))

Where:
E = Market value of equity
D = Market value of debt
V = E + D
Re = Cost of equity (from CAPM: Rf + β(Rm - Rf))
Rd = Cost of debt
T = Tax rate
```

**Terminal Value**:
```
TV = FCF(final year) × (1 + g) / (WACC - g)

Where:
g = Terminal growth rate
```

**Present Value**:
```
PV = FV / (1 + r)^n

Where:
r = Discount rate (WACC)
n = Number of years
```

## 🎓 Educational Value

The DCF Agent not only calculates but also:
- Explains concepts when asked
- Provides context for assumptions
- Warns about limitations
- Suggests appropriate parameter ranges
- Teaches users about valuation methodology

---

**Created by**: Finloggers Team
**Date**: 2025-11-22
**Version**: 1.0
**Purpose**: Comprehensive DCF valuation for IBM watsonx Orchestrate
