import requests
import json

class NexusClient:
    def __init__(self, api_key: str, base_url: str = "https://nexusgateway.onrender.com/api"):
        """
        Initialize the Nexus Client.
        :param api_key: Your 'nk-...' key from the dashboard.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def chat(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Send a message to the AI.
        Automatically handles Caching and Routing.
        """
        url = f"{self.base_url}/chat"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "message": message,
            "model": model
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status() # Raise error if 402 (Payment) or 500
            
            data = response.json()
            # Extract just the text to make it easy for the user
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 402:
                raise Exception(" Quota Exceeded. Please upgrade at the Dashboard.")
            raise e