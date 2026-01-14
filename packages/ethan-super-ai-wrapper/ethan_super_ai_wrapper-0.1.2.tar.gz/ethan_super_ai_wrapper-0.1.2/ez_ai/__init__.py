# file: ez_ai/__init__.py
import requests
import os

class _AIHandler:
    def __init__(self):
        self._openai_key = os.getenv("OPENAI_API_KEY")
        self._anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self._hf_key = os.getenv("HUGGINGFACE_API_KEY")
        self._model = None
        self._active_provider = None

    @property
    def openai_key(self): return self._openai_key
    @openai_key.setter
    def openai_key(self, key):
        self._openai_key = key
        self._set_provider("openai")

    @property
    def anthropic_key(self): return self._anthropic_key
    @anthropic_key.setter
    def anthropic_key(self, key):
        self._anthropic_key = key
        self._set_provider("anthropic")

    @property
    def hf_key(self): return self._hf_key
    @hf_key.setter
    def hf_key(self, key):
        self._hf_key = key
        self._set_provider("huggingface")

    @property
    def model(self): return self._model
    @model.setter
    def model(self, model_name):
        self._model = model_name
        if "gpt" in model_name or "dall" in model_name: self._active_provider = "openai"
        elif "claude" in model_name: self._active_provider = "anthropic"
        else: self._active_provider = "huggingface"

    def _set_provider(self, provider):
        self._active_provider = provider
        if provider == "openai": self._model = "gpt-4o"
        elif provider == "anthropic": self._model = "claude-3-5-sonnet-20240620"
        elif provider == "huggingface": self._model = "meta-llama/Meta-Llama-3-8B-Instruct"

    def _get_headers(self):
        if self._active_provider == "openai":
            return {"Authorization": f"Bearer {self._openai_key}", "Content-Type": "application/json"}
        elif self._active_provider == "anthropic":
            return {"x-api-key": self._anthropic_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        elif self._active_provider == "huggingface":
            return {"Authorization": f"Bearer {self._hf_key}"}

    def ask(self, prompt):
        try:
            if not self._active_provider: return "Error: Please set an API key first (e.g., ai.openai_key = '...')"
            
            if self._active_provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                payload = {"model": self._model, "messages": [{"role": "user", "content": prompt}]}
                res = requests.post(url, headers=self._get_headers(), json=payload).json()
                return res['choices'][0]['message']['content']

            elif self._active_provider == "anthropic":
                url = "https://api.anthropic.com/v1/messages"
                payload = {"model": self._model, "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}
                res = requests.post(url, headers=self._get_headers(), json=payload).json()
                return res['content'][0]['text']

            elif self._active_provider == "huggingface":
                url = f"https://router.huggingface.co/models/{self._model}"
                res = requests.post(url, headers=self._get_headers(), json={"inputs": prompt}).json()
                if isinstance(res, list) and 'generated_text' in res[0]: return res[0]['generated_text']
                return str(res)
        except Exception as e: return f"Error: {e}"

# Expose the object so users can import it
ai = _AIHandler()