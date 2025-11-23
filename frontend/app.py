"""
Financial Analyst Agent - Streamlit Chat Interface
Cloud-deployed IBM watsonx Orchestrate Agent Integration
"""
import streamlit as st
import streamlit.components.v1 as components
import os
from datetime import datetime
from orchestrate_client import WatsonxOrchestrateClient
from typing import List, Dict


# Page configuration
st.set_page_config(
    page_title="Financial Analyst AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage[data-testid="user-message"] {
        background-color: #e3f2fd;
    }
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #f5f5f5;
    }
    .sidebar-info {
        padding: 1rem;
        background-color: #f0f7ff;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1976d2;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "client" not in st.session_state:
        st.session_state.client = None

    if "agent_id" not in st.session_state:
        st.session_state.agent_id = None

    if "agents_list" not in st.session_state:
        st.session_state.agents_list = []

    if "connected" not in st.session_state:
        st.session_state.connected = False


def load_config():
    """Load configuration from environment variables or .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    config = {
        "instance_url": os.getenv("ORCHESTRATE_INSTANCE_URL", ""),
        "api_key": os.getenv("ORCHESTRATE_API_KEY", ""),
        "agent_id": os.getenv("AGENT_ID", "Financial_Analyst_Agent")
    }
    return config


def sidebar_config():
    """Render sidebar configuration"""
    with st.sidebar:
        st.title("⚙️ Configuration")

        # Load config
        config = load_config()

        # Connection Status
        if st.session_state.connected:
            st.success("✅ Connected to Agent")
        else:
            st.warning("⚠️ Not Connected")

        st.divider()

        # API Configuration
        st.subheader("🔐 API Settings")

        with st.expander("Configure Connection", expanded=not st.session_state.connected):
            instance_url = st.text_input(
                "Orchestrate Instance URL",
                value=config["instance_url"],
                help="Your watsonx Orchestrate cloud instance URL",
                placeholder="https://api.<region>.dl.watson-orchestrate.ibm.com/instances/<id>"
            )

            api_key = st.text_input(
                "IBM Cloud API Key",
                value=config["api_key"],
                type="password",
                help="Your IBM Cloud API key for authentication"
            )

            # Auto-fetch agents button
            if st.button("🔍 Fetch Available Agents", use_container_width=True):
                if not instance_url or not api_key:
                    st.error("Please provide Instance URL and API Key first")
                else:
                    with st.spinner("Fetching agents from cloud..."):
                        try:
                            temp_client = WatsonxOrchestrateClient(instance_url, api_key)
                            agents = temp_client.list_agents()

                            if agents:
                                st.session_state.agents_list = agents
                                st.success(f"✅ Found {len(agents)} agent(s)!")
                            else:
                                st.warning("No agents found in this instance")
                        except Exception as e:
                            st.error(f"Failed to fetch agents: {str(e)}")

            # Agent selection dropdown or manual input
            if st.session_state.agents_list:
                st.markdown("**Select an Agent:**")
                agent_options = {
                    f"{agent.get('name', 'Unknown')} ({agent.get('id', 'N/A')})": agent.get('id')
                    for agent in st.session_state.agents_list
                }

                selected_agent_label = st.selectbox(
                    "Available Agents",
                    options=list(agent_options.keys()),
                    label_visibility="collapsed"
                )

                agent_id = agent_options[selected_agent_label]

                # Show agent details
                selected_agent = next((a for a in st.session_state.agents_list if a.get('id') == agent_id), None)
                if selected_agent and selected_agent.get('description'):
                    st.caption(f"📝 {selected_agent['description'][:100]}...")
            else:
                agent_id = st.text_input(
                    "Agent ID (Manual Entry)",
                    value=config["agent_id"],
                    help="The ID of your Financial Analyst Agent"
                )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔗 Connect", type="primary", use_container_width=True):
                    if not instance_url or not api_key:
                        st.error("Please provide Instance URL and API Key")
                    elif not agent_id:
                        st.error("Please provide Agent ID")
                    else:
                        with st.spinner("Connecting..."):
                            try:
                                client = WatsonxOrchestrateClient(instance_url, api_key)
                                # Test connection by getting agent info
                                agent_info = client.get_agent_info(agent_id)

                                if agent_info:
                                    st.session_state.client = client
                                    st.session_state.agent_id = agent_id
                                    st.session_state.connected = True
                                    st.success("✅ Connected!")
                                    st.rerun()
                                else:
                                    st.error("❌ Could not find agent. Check Agent ID.")
                            except Exception as e:
                                st.error(f"❌ Connection failed: {str(e)}")

            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.session_state.connected = False
                    st.session_state.client = None
                    st.rerun()

        # Agent Info
        if st.session_state.connected and st.session_state.client:
            st.divider()
            st.subheader("🤖 Agent Information")

            with st.spinner("Loading agent info..."):
                agent_info = st.session_state.client.get_agent_info(st.session_state.agent_id)

                if agent_info:
                    st.markdown(f"""
                    <div class="metric-card">
                        <strong>Name:</strong> {agent_info.get('name', 'Financial Analyst Agent')}<br>
                        <strong>ID:</strong> {st.session_state.agent_id}<br>
                        <strong>Status:</strong> Active
                    </div>
                    """, unsafe_allow_html=True)

                    if agent_info.get('description'):
                        st.info(agent_info['description'])

        # Chat Controls
        st.divider()
        st.subheader("💬 Chat Controls")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        # Example Queries
        st.divider()
        st.subheader("📝 Example Queries")

        examples = {
            "📈 Financial Analysis": [
                "Analyze Apple's (AAPL) annual report",
                "What are Tesla's profitability trends?",
                "Compare Microsoft's revenue growth over 3 years"
            ],
            "🔍 Web Search + Analysis": [
                "What's the latest news on Apple and their financials?",
                "Analyze Tesla Q4 performance and market sentiment",
                "Give me Microsoft's financial health with recent AI news"
            ],
            "🧮 Calculations": [
                "Calculate percentage change from $100M to $150M",
                "What's the average of revenue: 100, 120, 140, 160, 180?",
                "Calculate compound growth of $1000 at 7% for 5 years"
            ]
        }

        for category, queries in examples.items():
            with st.expander(category):
                for query in queries:
                    if st.button(query, key=query, use_container_width=True):
                        if st.session_state.connected:
                            st.session_state.user_input = query
                            st.rerun()
                        else:
                            st.warning("Please connect to the agent first")


def render_watson_orchestrate_chat():
    """Render Watson Orchestrate embedded chat widget"""
    watson_orchestrate_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background-color: #f5f5f5;
            }
            #root {
                width: 100%;
                height: 100%;
                min-height: 700px;
            }
            .debug-info {
                position: absolute;
                top: 10px;
                left: 10px;
                background: white;
                padding: 10px;
                border: 1px solid #ccc;
                font-family: monospace;
                font-size: 12px;
                z-index: 9999;
            }
        </style>
    </head>
    <body>
        <div class="debug-info" id="debug">Loading Watson Orchestrate...</div>
        <div id="root"></div>

        <script>
            const debug = document.getElementById('debug');

            try {
                debug.innerHTML = 'Step 1: Setting configuration...<br>';

                // Try without agentEnvironmentId to use live environment by default
                window.wxOConfiguration = {
                    orchestrationID: "097a2cc6c9244419ae143b766eb0f746_be51f0bb-5afa-4282-a25a-f053bd49296f",
                    hostURL: "https://eu-de.watson-orchestrate.cloud.ibm.com",
                    rootElementID: "root",
                    showLauncher: true,
                    crn: "crn:v1:bluemix:public:watsonx-orchestrate:eu-de:a/097a2cc6c9244419ae143b766eb0f746:be51f0bb-5afa-4282-a25a-f053bd49296f::",
                    deploymentPlatform: "ibmcloud",
                    chatOptions: {
                        agentId: "fc512c24-b39c-4d88-a9a3-5ab41b16c813"
                    }
                };

                debug.innerHTML += 'Step 2: Configuration set. Loading script...<br>';
                debug.innerHTML += 'Agent ID: fc512c24-b39c-4d88-a9a3-5ab41b16c813<br>';
                debug.innerHTML += 'Environment ID: f303c70c-4e0f-4561-b838-329b670f41ae<br>';

                const script = document.createElement('script');
                script.src = 'https://eu-de.watson-orchestrate.cloud.ibm.com/wxochat/wxoLoader.js?embed=true';

                script.onload = function() {
                    debug.innerHTML += 'Step 3: Script loaded successfully!<br>';
                    if (typeof wxoLoader !== 'undefined') {
                        debug.innerHTML += 'Step 4: wxoLoader found. Initializing...<br>';
                        try {
                            // Check console for errors
                            const originalError = console.error;
                            const errors = [];
                            console.error = function(...args) {
                                errors.push(args.join(' '));
                                originalError.apply(console, args);
                            };

                            const instance = wxoLoader.init();
                            debug.innerHTML += 'Step 5: Initialized!<br>';
                            debug.innerHTML += 'Instance type: ' + (typeof instance) + '<br>';
                            debug.innerHTML += 'Instance value: ' + instance + '<br>';

                            // Check for console errors
                            setTimeout(function() {
                                if (errors.length > 0) {
                                    debug.innerHTML += 'Console errors:<br>' + errors.join('<br>') + '<br>';
                                }

                                // Check DOM for any chat elements
                                const chatElements = document.querySelectorAll('[class*="chat"], [id*="chat"], [class*="watson"], [id*="watson"]');
                                debug.innerHTML += 'Found ' + chatElements.length + ' chat-related elements<br>';

                                if (instance && typeof instance.openWindow === 'function') {
                                    debug.innerHTML += 'Step 6: Opening chat window...<br>';
                                    instance.openWindow();
                                } else {
                                    debug.innerHTML += 'Step 6: Cannot open - instance methods not available<br>';
                                    if (instance) {
                                        debug.innerHTML += 'Available methods: ' + Object.keys(instance).join(', ') + '<br>';
                                    }
                                }
                            }, 2000);
                        } catch(e) {
                            debug.innerHTML += 'ERROR in init: ' + e.message + '<br>';
                            debug.innerHTML += 'Stack: ' + e.stack + '<br>';
                        }
                    } else {
                        debug.innerHTML += 'ERROR: wxoLoader not found!<br>';
                    }
                };

                script.onerror = function(e) {
                    debug.innerHTML += 'ERROR loading script: ' + e + '<br>';
                };

                document.head.appendChild(script);

            } catch(e) {
                debug.innerHTML += 'EXCEPTION: ' + e.message + '<br>';
            }
        </script>
    </body>
    </html>
    """

    components.html(watson_orchestrate_html, height=800, scrolling=False)


def display_welcome_message():
    """Display welcome message when not connected"""
    st.markdown("""
    # 📊 Financial Analyst AI Agent

    Welcome to the **Financial Analyst Agent** powered by IBM watsonx Orchestrate!

    ## 🎯 What Can I Do?

    ### Financial Analysis
    - 📈 Analyze annual reports and financial statements
    - 💰 Calculate financial ratios and key metrics
    - 📊 Track revenue, profitability, and cash flow trends
    - 🎯 Evaluate balance sheet health and debt levels

    ### Market Intelligence
    - 🔍 Search the web for recent company news
    - 📰 Find earnings reports and analyst opinions
    - 🌐 Discover industry trends and market sentiment
    - 📡 Get real-time information about stocks

    ### Mathematical Operations
    - 🧮 Perform financial calculations
    - 📐 Calculate percentage changes and growth rates
    - 📊 Compute averages and compound growth
    - ⚡ Validate complex financial ratios

    ---
    """)

    # Render Watson Orchestrate Chat Widget
    st.subheader("💬 Chat with Financial Analyst Agent")
    st.info("👇 Look for a **circular chat button** in the bottom-right corner of the frame below. Click it to start chatting!")
    render_watson_orchestrate_chat()


def main():
    """Main Streamlit application"""
    initialize_session_state()
    sidebar_config()

    # Check if connected
    if not st.session_state.connected:
        display_welcome_message()
        return

    # Main chat interface
    st.title("📊 Financial Analyst AI")
    st.caption(f"Connected to Agent: `{st.session_state.agent_id}`")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"_{message['timestamp']}_")

    # Check if there's a pre-filled input from example buttons
    if "user_input" in st.session_state:
        prompt = st.session_state.user_input
        del st.session_state.user_input
    else:
        # Chat input
        prompt = st.chat_input("Ask me anything about financial analysis...")

    if prompt:
        # Add user message to chat
        timestamp = datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"_{timestamp}_")

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing..."):
                # Convert messages to API format (without timestamps)
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ]

                response = st.session_state.client.invoke_agent(
                    st.session_state.agent_id,
                    prompt,
                    api_messages[:-1]  # Exclude the current user message
                )

            # Display response
            st.markdown(response)
            response_timestamp = datetime.now().strftime("%I:%M %p")
            st.caption(f"_{response_timestamp}_")

            # Add assistant message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": response_timestamp
            })


if __name__ == "__main__":
    main()
