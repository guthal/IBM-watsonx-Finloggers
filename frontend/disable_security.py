"""
Script to disable security for Watson Orchestrate Embedded Chat
This allows anonymous access for testing purposes
"""
import requests
import json

# Configuration
API_URL = "https://eu-de.watson-orchestrate.cloud.ibm.com"
INSTANCE_ID = "be51f0bb-5afa-4282-a25a-f053bd49296f"
API_KEY = "bREeTZO6SWjd2-0dRcxQiX7p7N4dZjipvvQ6Xvu1foPf"

# Endpoint
endpoint = f"{API_URL}/instances/{INSTANCE_ID}/v1/embed/secure/config"

# Payload to disable security
payload = {
    "public_key": "",
    "client_public_key": "",
    "is_security_enabled": False
}

# Headers for IBM Cloud authentication
headers = {
    "IAM-API_KEY": API_KEY,
    "Content-Type": "application/json"
}

print("Disabling security for Watson Orchestrate Embedded Chat...")
print(f"API URL: {API_URL}")
print(f"Instance ID: {INSTANCE_ID}")

try:
    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        print("\n✅ SUCCESS: Security has been disabled!")
        print("Your embedded chat now allows anonymous access.")
        print("\nRefresh your Streamlit app and the chat should now work.")
    else:
        print(f"\n❌ ERROR: Failed to disable security")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ EXCEPTION: {str(e)}")
    print("Please check your network connection and credentials.")
