# Financial Analysis Agents - watsonx Orchestrate ADK

Two specialized agents for stock market analysis using the Financial Modeling Prep API and watsonx Orchestrate:
- **Stock Price Agent**: Real-time stock price quotes and search
- **Financial Analyst Agent**: Comprehensive annual report analysis with financial statements, ratios, and metrics

## Project Structure

```
adk-project/
├── agents/
│   ├── hello-world-agent.yaml
│   ├── stock-price-agent.yaml          # Stock price agent configuration
│   └── financial-analyst-agent.yaml    # Financial analyst agent configuration (NEW)
├── tools/
│   ├── stock_price_tool.py             # Stock price tool implementation
│   ├── financial_analysis_tool.py      # Financial analysis tool (NEW)
│   └── requirements.txt                # Python dependencies
├── .env                                 # Environment variables (your API key)
└── .env.template                        # Template for environment setup
```

## Setup Instructions

### 1. Install watsonx Orchestrate ADK

```bash
pip install ibm-watsonx-orchestrate-adk
```

### 2. Configure Environment Variables

The `.env` file is already configured with your FMP API key. If you need to change it:

```bash
# Edit .env file
WXO_SECURITY_SCHEMA_stock_tool=key_value_creds
WXO_CONNECTION_stock_tool_api_key=your_api_key_here
WXO_CONNECTION_stock_tool_base_url=https://financialmodelingprep.com/api/v3
```

### 3. Import the Tools

```bash
# Navigate to the project directory
cd /home/guthal/Finloggers/IBM-watsonx-Finloggers/adk-project

# Import the stock price tool
orchestrate tools import -k python -f tools/stock_price_tool.py -r tools/requirements.txt

# Import the financial analysis tool
orchestrate tools import -k python -f tools/financial_analysis_tool.py -r tools/requirements.txt
```

### 4. Import the Agents

```bash
# Import the stock price agent
orchestrate agents import -f agents/stock-price-agent.yaml

# Import the financial analyst agent
orchestrate agents import -f agents/financial-analyst-agent.yaml
```

### 5. Start the Orchestrate Server

```bash
# Start the server with the environment file
orchestrate server start --env-file .env
```

## Using the Agents

Once the server is running, you can interact with both agents through the watsonx Orchestrate interface.

### Stock Price Agent

**Example Queries:**
- "What's the current price of Apple stock?"
- "Get me the stock price for MSFT"
- "Search for Tesla stock"
- "Show me prices for AAPL, GOOGL, and MSFT"

**Available Tools:**
1. **get_stock_price(symbol)** - Fetch current price and details for a single stock
2. **get_multiple_stocks(symbols)** - Fetch prices for multiple stocks (comma-separated)
3. **search_stock(query)** - Search for stocks by company name

### Financial Analyst Agent (NEW)

**Example Queries:**
- "Analyze the annual report for Apple (AAPL)"
- "Give me a comprehensive financial analysis of Microsoft for the last 5 years"
- "What are Tesla's profitability trends?"
- "Analyze GOOGL's cash flow and capital allocation"
- "Compare Amazon's debt levels over the past 3 years"
- "Is Nvidia's revenue growth sustainable?"

**Available Tools from `financial_analysis_tool.py`:**
1. **get_company_profile(symbol)** - Company overview, sector, industry, market cap
2. **get_income_statement(symbol, period, limit)** - Revenue, expenses, profitability
3. **get_balance_sheet(symbol, period, limit)** - Assets, liabilities, equity, debt
4. **get_cash_flow_statement(symbol, period, limit)** - Operating, investing, financing cash flows
5. **get_financial_ratios(symbol, period, limit)** - Profitability, liquidity, leverage ratios
6. **get_key_metrics(symbol, period, limit)** - Valuation metrics, per-share data
7. **get_comprehensive_analysis(symbol, years)** - Complete financial analysis package

The Financial Analyst Agent provides detailed analysis including:
- Revenue and profitability trends
- Balance sheet health and debt analysis
- Cash flow generation and capital allocation
- Financial ratios and key metrics
- Strengths, risks, and investment perspective

## Environment Variable Configuration

This project uses watsonx Orchestrate's environment variable naming convention:

- `WXO_SECURITY_SCHEMA_stock_tool` - Defines the connection type (key_value_creds)
- `WXO_CONNECTION_stock_tool_api_key` - Your FMP API key
- `WXO_CONNECTION_stock_tool_base_url` - API base URL

The tool automatically reads these variables using the `get_connection_config()` function.

## Agent Configuration

The agent is configured with:

- **LLM**: `watsonx/meta-llama/llama-3-2-90b-vision-instruct`
- **Style**: `default` (streamlined, tool-centric mode)
- **Tools**: `stock_price_tool`

## Testing the Tools Directly

You can test the tools independently before importing them:

```bash
# Set environment variable
export WXO_CONNECTION_stock_tool_api_key=your_api_key_here

# Test the stock price tool
python tools/stock_price_tool.py

# Test the financial analysis tool
python tools/financial_analysis_tool.py
```

## Troubleshooting

### API Key Not Found
If you get an error about missing API key:
1. Check that `.env` file exists and contains the correct key
2. Ensure you started the server with `--env-file .env`
3. Verify the environment variable naming matches the pattern

### Tool Not Found
If the agent can't find the tool:
1. Make sure you imported the tool: `orchestrate tools import -k python -f tools/stock_price_tool.py`
2. Verify the tool name in the agent YAML matches the imported tool name

### Connection Issues
If API requests fail:
1. Check your internet connection
2. Verify the FMP API key is valid
3. Check the API base URL is correct

## Security Notes

- Never commit `.env` file to version control
- Use `.env.template` for sharing configuration structure
- Keep your API keys secure
- The `.gitignore` should include `.env`

## Next Steps

To extend this agent:

1. Add more financial data tools (company financials, historical data, etc.)
2. Implement caching for frequently requested stocks
3. Add error handling and retry logic
4. Create visualizations for stock data
5. Integrate with other watsonx services
