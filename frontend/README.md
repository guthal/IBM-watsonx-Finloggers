# Financial Analyst Agent - Streamlit Interface

A conversational UI for the Financial Analyst Agent powered by IBM watsonx Orchestrate. This Streamlit application provides an intuitive chat interface to interact with your cloud-deployed AI agent for comprehensive financial analysis.

## 🎯 Features

- **💬 Chat Interface**: Natural conversation with the Financial Analyst Agent
- **📊 Financial Analysis**: Analyze annual reports, financial statements, and key metrics
- **🔍 Web Search Integration**: Get recent news and market sentiment
- **🧮 Mathematical Operations**: Perform financial calculations and validations
- **☁️ Cloud Integration**: Connects to IBM watsonx Orchestrate cloud-deployed agents
- **🔐 Secure Authentication**: Uses IBM Cloud IAM for secure API access

## 📋 Prerequisites

1. **IBM watsonx Orchestrate Account** with a deployed Financial Analyst Agent
2. **IBM Cloud API Key** with access to your watsonx Orchestrate instance
3. **Python 3.8+** installed on your system
4. **Internet Connection** for API access

## 🚀 Quick Start

### 1. Clone the Repository

```bash
cd /home/guthal/Finloggers/IBM-watsonx-Finloggers/frontend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:

```env
# Your watsonx Orchestrate instance URL
ORCHESTRATE_INSTANCE_URL=https://api.<region>.dl.watson-orchestrate.ibm.com/instances/<your-instance-id>

# Your IBM Cloud API Key (already filled in)
ORCHESTRATE_API_KEY=bREeTZO6SWjd2-0dRcxQiX7p7N4dZjipvvQ6Xvu1foPf

# Your Agent ID
AGENT_ID=Financial_Analyst_Agent
```

#### How to Find Your Instance URL:

1. Log in to [IBM watsonx Orchestrate](https://www.ibm.com/products/watsonx-orchestrate)
2. Go to **Profile → Settings → API Details**
3. Copy the **Service Instance URL**

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 🔧 Usage

### Connecting to the Agent

1. **Open the Sidebar** (click the `>` icon if collapsed)
2. **Configure Connection Settings**:
   - Instance URL (auto-loaded from .env)
   - API Key (auto-loaded from .env)
   - Agent ID (default: Financial_Analyst_Agent)
3. **Click "Connect"** button
4. Wait for the success message

### Asking Questions

Once connected, you can ask questions like:

**Financial Analysis:**
- "Analyze Apple's (AAPL) annual report"
- "What are Tesla's profitability trends?"
- "Compare Microsoft's revenue growth over 3 years"

**Web Search + Analysis:**
- "What's the latest news on Apple and their financials?"
- "Analyze Tesla Q4 performance and recent market sentiment"
- "Give me Google's financial health with recent AI announcements"

**Mathematical Operations:**
- "Calculate percentage change from $100M to $150M"
- "What's the average of revenue: 100, 120, 140, 160, 180?"
- "Calculate compound growth of $1000 at 7% for 5 years"

### Chat Controls

- **Clear Chat History**: Removes all messages and starts fresh
- **Example Queries**: Click any example in the sidebar to auto-fill
- **Refresh Connection**: Reconnect if the session expires

## 📁 Project Structure

```
frontend/
├── app.py                   # Main Streamlit application
├── orchestrate_client.py    # IBM watsonx Orchestrate API client
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your actual credentials (not tracked in git)
└── README.md               # This file
```

## 🔐 Security Notes

- **Never commit your `.env` file** to version control
- The API key in `.env.example` is your actual key - protect it
- IBM Cloud access tokens expire after 1 hour (automatically refreshed)
- All API communication uses HTTPS

## 🛠️ Troubleshooting

### "Connection failed" Error

**Possible causes:**
1. **Incorrect Instance URL**: Verify the URL format and instance ID
2. **Invalid API Key**: Check if the API key is correct and has proper permissions
3. **Agent Not Deployed**: Ensure your Financial Analyst Agent is deployed in watsonx Orchestrate
4. **Network Issues**: Check your internet connection

**Solution:**
```bash
# Test the client directly
python orchestrate_client.py
```

### "Could not find agent" Error

**Cause:** The Agent ID doesn't match any deployed agent

**Solution:**
1. Go to watsonx Orchestrate console
2. Navigate to **Agents** section
3. Find your Financial Analyst Agent
4. Copy the exact **Agent ID**
5. Update the `AGENT_ID` in `.env`

### Token Expiration

IBM Cloud tokens expire after 1 hour. The client automatically refreshes tokens, but if you see authentication errors:

1. Click **"Refresh"** in the sidebar
2. Click **"Connect"** again

### Rate Limiting

If you encounter rate limiting errors:
- Wait a few seconds between requests
- The agent performs complex operations that may take time
- Financial analysis with web search can take 30-60 seconds

## 🧪 Testing the Client

Test the API client independently:

```bash
cd frontend
python orchestrate_client.py
```

This will:
1. Load credentials from `.env`
2. Authenticate with IBM Cloud
3. List available agents
4. Test a simple chat interaction

## 📊 Advanced Features

### Custom Agent IDs

To use a different agent:

```python
# In .env file
AGENT_ID=Your_Custom_Agent_ID
```

### Conversation History

The app maintains conversation history automatically. The agent can:
- Reference previous questions
- Build context across multiple interactions
- Maintain analytical continuity

### Streaming Responses (Coming Soon)

Future versions will support streaming responses for real-time output.

## 🤝 Integration with Backend

This frontend connects to:
- **IBM watsonx Orchestrate Cloud** (agent hosting)
- **Financial Analysis Tool** (FMP API integration)
- **Math Agent** (calculation support)
- **Web Search Tool** (DuckDuckGo integration)

All tools are deployed in watsonx Orchestrate and accessed via the agent.

## 📚 Resources

- [IBM watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Agent Development Kit (ADK)](https://developer.watson-orchestrate.ibm.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [IBM Cloud API Authentication](https://cloud.ibm.com/docs/account?topic=account-iamtoken_from_apikey)

## 🐛 Known Issues

1. **First connection takes longer**: IBM Cloud token generation adds ~2-3 seconds
2. **Large responses may timeout**: Financial analysis can be comprehensive
3. **Web search results vary**: DuckDuckGo results depend on current availability

## 📝 Development

To modify the UI:

```bash
# Edit app.py for UI changes
# Edit orchestrate_client.py for API logic

# Restart Streamlit to see changes
streamlit run app.py
```

Streamlit auto-reloads when you save files!

## 📄 License

This project is part of the Finloggers IBM watsonx implementation.

---

**Built with ❤️ using IBM watsonx Orchestrate and Streamlit**
