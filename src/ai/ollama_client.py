import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def generate_response(self, model, prompt, images=None, stream=False):
        url = f"{self.base_url}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        if images:
            data["images"] = images # Base64 encoded images
        
        try:
            response = requests.post(url, json=data, stream=stream)
            if stream:
                return response
            else:
                return response.json().get("response", "")
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def list_models(self):
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url)
            return response.json().get("models", [])
        except:
            return []
