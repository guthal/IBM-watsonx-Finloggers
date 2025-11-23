"""
IBM watsonx Orchestrate Cloud Client
Handles authentication and API communication with cloud-deployed agents
"""
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class IBMCloudAuth:
    """Handles IBM Cloud IAM authentication for watsonx Orchestrate"""

    IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self, api_key: str):
        """
        Initialize IBM Cloud authentication

        Args:
            api_key: IBM Cloud API key
        """
        self.api_key = api_key
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary

        Returns:
            Valid IBM Cloud access token
        """
        # Check if we have a valid token
        if self.access_token and self.token_expiry:
            if datetime.now() < self.token_expiry - timedelta(minutes=5):
                return self.access_token

        # Get new token
        self._refresh_token()
        return self.access_token

    def _refresh_token(self):
        """Refresh the IBM Cloud access token"""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }

        try:
            response = requests.post(
                self.IAM_TOKEN_URL,
                headers=headers,
                data=data,
                timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("access_token")

            # Token expires in 3600 seconds (1 hour)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

        except Exception as e:
            raise Exception(f"Failed to get IBM Cloud access token: {str(e)}")


class WatsonxOrchestrateClient:
    """Client for interacting with watsonx Orchestrate cloud agents"""

    def __init__(self, instance_url: str, api_key: str):
        """
        Initialize the watsonx Orchestrate client

        Args:
            instance_url: Your watsonx Orchestrate instance URL
            api_key: IBM Cloud API key
        """
        self.instance_url = instance_url.rstrip('/')
        self.auth = IBMCloudAuth(api_key)
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh authentication token"""
        access_token = self.auth.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def list_agents(self) -> List[Dict]:
        """
        List all available agents in the instance

        Returns:
            List of agent dictionaries
        """
        try:
            url = f"{self.instance_url}/v1/agents"
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return data.get("agents", [])
        except Exception as e:
            print(f"Error listing agents: {str(e)}")
            return []

    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """
        Get information about a specific agent

        Args:
            agent_id: The agent ID

        Returns:
            Agent information dictionary or None
        """
        try:
            url = f"{self.instance_url}/v1/agents/{agent_id}"
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting agent info: {str(e)}")
            return None

    def chat_completion(
        self,
        agent_id: str,
        messages: List[Dict],
        stream: bool = False
    ) -> Dict:
        """
        Send a chat completion request to the agent

        Args:
            agent_id: The agent ID to invoke
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response (not implemented yet)

        Returns:
            Response dictionary from the agent
        """
        try:
            url = f"{self.instance_url}/v1/agents/{agent_id}/chat/completions"

            payload = {
                "messages": messages,
                "stream": stream
            }

            response = self.session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=120  # Financial analysis can take time
            )
            response.raise_for_status()

            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {json.dumps(error_detail)}"
            except:
                error_msg += f" - {e.response.text}"
            return {"error": error_msg}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def invoke_agent(
        self,
        agent_id: str,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Invoke the agent with a user message

        Args:
            agent_id: The agent ID to invoke
            user_message: The user's input message
            conversation_history: Previous conversation messages

        Returns:
            Agent's response as string
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        response = self.chat_completion(agent_id, messages)

        if "error" in response:
            return f"❌ Error: {response['error']}"

        # Extract assistant message from response
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice:
                return choice["message"].get("content", "No response content")
            elif "text" in choice:
                return choice["text"]
        elif "response" in response:
            return response["response"]
        elif "content" in response:
            return response["content"]
        else:
            return f"⚠️ Unexpected response format: {json.dumps(response, indent=2)}"


if __name__ == "__main__":
    # Test the client
    import os
    from dotenv import load_dotenv

    load_dotenv()

    instance_url = os.getenv("ORCHESTRATE_INSTANCE_URL")
    api_key = os.getenv("ORCHESTRATE_API_KEY")

    if not instance_url or not api_key:
        print("Please set ORCHESTRATE_INSTANCE_URL and ORCHESTRATE_API_KEY in .env file")
        exit(1)

    print("Testing watsonx Orchestrate Cloud Client...")
    print(f"Instance URL: {instance_url}\n")

    client = WatsonxOrchestrateClient(instance_url, api_key)

    print("1. Listing agents...")
    agents = client.list_agents()
    print(f"Found {len(agents)} agent(s)")
    for agent in agents:
        print(f"  - {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'N/A')})")

    if agents:
        agent_id = agents[0].get('id')
        print(f"\n2. Getting info for agent: {agent_id}")
        info = client.get_agent_info(agent_id)
        if info:
            print(f"  Name: {info.get('name')}")
            print(f"  Description: {info.get('description')}")

        print(f"\n3. Testing chat with agent...")
        response = client.invoke_agent(agent_id, "Hello, can you help me?")
        print(f"Response: {response}")
