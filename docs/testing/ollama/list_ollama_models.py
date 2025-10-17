import requests
import json

# Ollama server URL
OLLAMA_URL = "http://192.168.1.98:11434/api/tags"

def list_models():
    try:
        response = requests.get(OLLAMA_URL)
        if response.status_code == 200:
            models_data = response.json()
            print("Available models:")
            for model in models_data.get('models', []):
                print(f"  - {model['name']}")
        else:
            print(f"Failed to fetch models. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching models: {e}")

if __name__ == "__main__":
    list_models()