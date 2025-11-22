# Financial Analyst Agent - Setup & Usage Guide

## Overview

The Financial Analyst Agent is an expert AI agent that performs comprehensive annual report analysis using real financial data from the Financial Modeling Prep (FMP) API.

## What It Does

This agent analyzes companies by examining:
- **Income Statements**: Revenue, profitability, expense trends
- **Balance Sheets**: Assets, liabilities, debt levels, equity
- **Cash Flow Statements**: Operating cash flow, free cash flow, capital allocation
- **Financial Ratios**: Profitability, liquidity, leverage, efficiency metrics
- **Key Metrics**: Valuation multiples, per-share data, dividend information

## Quick Start

### Step 1: Import the Financial Analysis Tool

```bash
cd /home/guthal/Finloggers/IBM-watsonx-Finloggers/adk-project

orchestrate tools import -k python -f tools/financial_analysis_tool.py -r tools/requirements.txt
```

### Step 2: Import the Financial Analyst Agent

```bash
orchestrate agents import -f agents/financial-analyst-agent.yaml
```

### Step 3: Start the Server (if not already running)

```bash
orchestrate server start --env-file .env
```

Your `.env` file already contains the FMP API key configuration.

## Available Tools

### 1. get_comprehensive_analysis(symbol, years)
**Primary tool for annual report analysis**

Fetches all financial data in one call:
- Company profile and overview
- Income statements (annual)
- Balance sheets (annual)
- Cash flow statements (annual)
- Financial ratios
- Key metrics

**Example:**
```
"Analyze the annual report for Apple (AAPL) for the last 5 years"
```

### 2. get_company_profile(symbol)
Company overview and basic information.

### 3. get_income_statement(symbol, period, limit)
Revenue, expenses, and profitability data.
- `period`: "annual" or "quarter"
- `limit`: Number of periods (default: 5)

### 4. get_balance_sheet(symbol, period, limit)
Assets, liabilities, equity, and debt information.

### 5. get_cash_flow_statement(symbol, period, limit)
Operating, investing, and financing cash flows.

### 6. get_financial_ratios(symbol, period, limit)
Profitability, liquidity, and leverage ratios.

### 7. get_key_metrics(symbol, period, limit)
Valuation metrics and per-share data.

## Example Queries

### Comprehensive Analysis
```
"Analyze the annual report for Microsoft (MSFT)"
"Give me a complete financial analysis of Tesla for the last 3 years"
"Perform a comprehensive analysis of NVDA"
```

### Focused Analysis
```
"What are Apple's profitability trends over the last 5 years?"
"Analyze Amazon's cash flow and capital allocation"
"Show me Google's debt levels and how they've changed"
"Is Meta's revenue growth sustainable?"
"Compare Netflix's profit margins to historical averages"
```

### Specific Aspects
```
"What is Microsoft's return on equity trend?"
"Analyze Tesla's free cash flow generation"
"Show me Apple's balance sheet health"
"What are Amazon's key financial ratios?"
```

## What the Agent Provides

The Financial Analyst Agent structures its analysis as:

1. **Executive Summary** - Quick overview of financial health
2. **Business Overview** - Company profile and industry context
3. **Financial Performance** - Revenue and profitability trends
4. **Financial Position** - Balance sheet strength and leverage
5. **Cash Flow Analysis** - Cash generation and capital allocation
6. **Key Ratios & Metrics** - Comprehensive ratio analysis
7. **Strengths & Risks** - Key positives and concerns
8. **Conclusion** - Overall assessment and investment perspective

## API Endpoints Used

The tool connects to these FMP API endpoints:

- `/profile/{symbol}` - Company profile
- `/income-statement/{symbol}` - Income statements
- `/balance-sheet-statement/{symbol}` - Balance sheets
- `/cash-flow-statement/{symbol}` - Cash flow statements
- `/ratios/{symbol}` - Financial ratios
- `/key-metrics/{symbol}` - Key metrics

All endpoints use the same API key configured in your `.env` file.

## Data Availability

- **Historical Range**: Up to 10 years of annual data
- **Update Frequency**: Real-time updates when companies file new reports
- **Coverage**: All NYSE and NASDAQ listed companies
- **Data Quality**: Standardized and audited financial statements

## Testing the Tool

Before using with the agent, you can test the tool directly:

```bash
# Set the API key
export WXO_CONNECTION_stock_tool_api_key=your_api_key_here

# Run the test
python tools/financial_analysis_tool.py
```

This will fetch sample data for Apple (AAPL) and verify the connection works.

## Agent Behavior

The Financial Analyst Agent is configured to:
- Provide thorough, data-driven analysis
- Calculate growth rates and trends automatically
- Compare metrics across multiple years
- Highlight both strengths and risks objectively
- Format numbers clearly (e.g., "$125.4B", "32.5%")
- Cite specific fiscal years when referencing data
- Be balanced and analytical (not promotional)

## Integration with Stock Price Agent

You can use both agents together:
- **Stock Price Agent**: For real-time quotes and current prices
- **Financial Analyst Agent**: For deep financial analysis and annual reports

## Troubleshooting

### "API key not configured" Error
- Ensure `.env` file contains: `WXO_CONNECTION_stock_tool_api_key=your_key`
- Restart the orchestrate server with: `orchestrate server start --env-file .env`

### "No data returned" Error
- Verify the stock symbol is correct (e.g., "AAPL" not "Apple")
- Check that the company is publicly traded
- Some smaller companies may have limited financial data

### Tool Import Failed
```bash
# Verify the tool file exists
ls -la tools/financial_analysis_tool.py

# Re-import the tool
orchestrate tools import -k python -f tools/financial_analysis_tool.py -r tools/requirements.txt
```

### Agent Can't Find the Tool
- Ensure the tool was imported successfully
- Verify the agent YAML references `financial_analysis_tool` (singular)
- Re-import the agent: `orchestrate agents import -f agents/financial-analyst-agent.yaml`

## Advanced Usage

### Quarterly Analysis
Ask for quarterly data instead of annual:
```
"Show me Tesla's quarterly income statements for the last 8 quarters"
```

### Multi-Year Trends
Request longer historical periods:
```
"Analyze Apple's financial performance over the last 10 years"
```

### Comparative Analysis
Compare multiple metrics:
```
"Compare Microsoft's revenue growth, profit margins, and free cash flow over 5 years"
```

### Ratio Deep-Dive
Focus on specific ratio categories:
```
"Analyze Amazon's liquidity ratios and working capital trends"
"What are Google's profitability ratios and how have they changed?"
```

## Next Steps

Consider enhancing the analysis with:
1. Peer comparison (compare to competitors in same sector)
2. Industry benchmarking (compare ratios to industry averages)
3. Historical volatility analysis
4. Earnings quality scores
5. Financial health scoring system
6. Automated red flag detection
