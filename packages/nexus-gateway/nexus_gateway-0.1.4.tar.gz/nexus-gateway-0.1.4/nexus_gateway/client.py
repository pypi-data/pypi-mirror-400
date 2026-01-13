import requests
import json

class NexusClient:
    def __init__(self, api_key: str, base_url: str = "https://nexusgateway.onrender.com/api"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def validate_key(self):
        """Checks if the key is valid by hitting a cheap endpoint."""
        # Simple check: Does it look like a key?
        if not self.api_key.startswith("nk-"):
            return False
        # Network check: Try to fetch stats (doesn't cost money)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            res = requests.get(f"{self.base_url}/stats", headers=headers)
            return res.status_code == 200
        except:
            return False

    def chat(self, message: str, model: str = "gpt-3.5-turbo", stream: bool = False):
        """
        Send a message. 
        If stream=True, returns a GENERATOR that yields text chunks.
        If stream=False, returns the full string.
        """
        endpoint = "/chat/stream" if stream else "/chat"
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {"message": message, "model": model}

        # Handle Streaming
        if stream:
            return self._handle_stream(url, payload, headers)
        
        # Handle Normal
        response = requests.post(url, json=payload, headers=headers)
        self._check_error(response)
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

    def _handle_stream(self, url, payload, headers):
        """Internal helper to read Server-Sent Events"""
        response = requests.post(url, json=payload, headers=headers, stream=True)
        self._check_error(response)

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    try:
                        json_str = line_str.replace("data: ", "")
                        if json_str.strip() == "[DONE]": break
                        
                        data = json.loads(json_str)
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            yield content
                    except:
                        pass

    def _check_error(self, response):
        if response.status_code == 401:
            raise Exception("Unauthorized: Invalid API Key")
        if response.status_code == 402:
            raise Exception("⛔ Quota Exceeded. Please upgrade at the Dashboard.")
        if response.status_code >= 400:
            raise Exception(f"API Error {response.status_code}: {response.text}")