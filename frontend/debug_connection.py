"""
Debug script to test watsonx Orchestrate connection and find agents
"""
import os
from dotenv import load_dotenv
from orchestrate_client import WatsonxOrchestrateClient
import json

# Load environment variables
load_dotenv()

print("=" * 60)
print("watsonx Orchestrate Connection Debug Tool")
print("=" * 60)

# Get configuration
instance_url = os.getenv("ORCHESTRATE_INSTANCE_URL")
api_key = os.getenv("ORCHESTRATE_API_KEY")
agent_id = os.getenv("AGENT_ID", "Financial_Analyst_Agent")

print("\n1. Configuration Check:")
print(f"   Instance URL: {instance_url if instance_url else '❌ NOT SET'}")
print(f"   API Key: {'✅ Set (' + api_key[:10] + '...' + api_key[-5:] + ')' if api_key else '❌ NOT SET'}")
print(f"   Agent ID: {agent_id}")

if not instance_url:
    print("\n❌ ERROR: ORCHESTRATE_INSTANCE_URL is not set!")
    print("\nTo fix this:")
    print("1. Log in to IBM watsonx Orchestrate")
    print("2. Go to Profile → Settings → API Details")
    print("3. Copy the 'Service Instance URL'")
    print("4. Edit frontend/.env and add it to ORCHESTRATE_INSTANCE_URL")
    print("\nExample format:")
    print("ORCHESTRATE_INSTANCE_URL=https://api.eu-central-1.dl.watson-orchestrate.ibm.com/instances/12345678-1234-1234-1234-123456789abc")
    exit(1)

if not api_key:
    print("\n❌ ERROR: ORCHESTRATE_API_KEY is not set!")
    exit(1)

print("\n2. Testing IBM Cloud Authentication...")
try:
    client = WatsonxOrchestrateClient(instance_url, api_key)
    print("   ✅ Authentication client created")

    # Test token generation
    token = client.auth.get_access_token()
    print(f"   ✅ Access token obtained: {token[:20]}...")
except Exception as e:
    print(f"   ❌ Authentication failed: {str(e)}")
    exit(1)

print("\n3. Listing Available Agents...")
try:
    agents = client.list_agents()

    if not agents:
        print("   ⚠️  No agents found in your instance")
        print("\n   This could mean:")
        print("   - You haven't deployed any agents yet")
        print("   - The instance URL is incorrect")
        print("   - The API key doesn't have access to agents")
        print("\n   To deploy your agent:")
        print("   cd /home/guthal/Finloggers/IBM-watsonx-Finloggers/adk-project")
        print("   orchestrate agents import -f agents/financial-analyst-agent.yaml")
    else:
        print(f"   ✅ Found {len(agents)} agent(s):\n")
        for i, agent in enumerate(agents, 1):
            print(f"   Agent {i}:")
            print(f"      Name: {agent.get('name', 'N/A')}")
            print(f"      ID: {agent.get('id', 'N/A')}")
            print(f"      Kind: {agent.get('kind', 'N/A')}")
            if agent.get('description'):
                print(f"      Description: {agent['description'][:80]}...")
            print()

        # Save agent IDs to a file for reference
        with open("available_agents.json", "w") as f:
            json.dump(agents, f, indent=2)
        print("   💾 Agent details saved to 'available_agents.json'")

except Exception as e:
    print(f"   ❌ Failed to list agents: {str(e)}")
    exit(1)

print("\n4. Testing Connection to Specific Agent...")
print(f"   Trying to connect to: {agent_id}")
try:
    agent_info = client.get_agent_info(agent_id)

    if agent_info:
        print(f"   ✅ Successfully connected to agent!")
        print(f"      Name: {agent_info.get('name')}")
        print(f"      ID: {agent_info.get('id')}")
        print(f"      Status: Active")
    else:
        print(f"   ❌ Agent '{agent_id}' not found")
        print("\n   Available agent IDs:")
        for agent in agents:
            print(f"      - {agent.get('id')}")
        print("\n   Update your .env file with the correct AGENT_ID")
except Exception as e:
    print(f"   ❌ Error getting agent info: {str(e)}")

print("\n5. Testing Chat Functionality...")
if agent_info:
    try:
        print("   Sending test message: 'Hello, can you help me?'")
        response = client.invoke_agent(agent_id, "Hello, can you help me?")
        print(f"   ✅ Got response: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Chat test failed: {str(e)}")

print("\n" + "=" * 60)
print("Debug Complete!")
print("=" * 60)
