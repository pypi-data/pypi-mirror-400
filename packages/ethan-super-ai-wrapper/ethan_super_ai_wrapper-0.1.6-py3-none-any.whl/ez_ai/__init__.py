import requests
import os

class _AIHandler:
    def __init__(self):
        # Keys
        self._openai_key = os.getenv("OPENAI_API_KEY")
        self._anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self._hf_key = os.getenv("HUGGINGFACE_API_KEY")
        self._gemini_key = os.getenv("GEMINI_API_KEY") # <--- NEW
        
        # Internal state
        self._model = None
        self._active_provider = None
        self.system_prompt = "You are a helpful assistant."
        self.history = []

    # ==========================
    # 1. KEY PROPERTIES
    # ==========================
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

    # --- NEW GEMINI PROPERTY ---
    @property
    def gemini_key(self): return self._gemini_key
    @gemini_key.setter
    def gemini_key(self, key):
        self._gemini_key = key
        self._set_provider("gemini")

    # ==========================
    # 2. MODEL SWITCHING LOGIC
    # ==========================
    @property
    def model(self): return self._model
    @model.setter
    def model(self, model_name):
        self._model = model_name
        # Smart Auto-Detect
        if "gpt" in model_name or "dall" in model_name: 
            self._active_provider = "openai"
        elif "claude" in model_name: 
            self._active_provider = "anthropic"
        elif "gemini" in model_name:  # <--- NEW
            self._active_provider = "gemini"
        else: 
            self._active_provider = "huggingface"

    def _set_provider(self, provider):
        self._active_provider = provider
        if provider == "openai": self._model = "gpt-4o"
        elif provider == "anthropic": self._model = "claude-3-5-sonnet-20240620"
        elif provider == "huggingface": self._model = "mistralai/Mistral-7B-Instruct-v0.3"
        elif provider == "gemini": self._model = "gemini-1.5-flash" # <--- Default Gemini Model

    def _get_headers(self):
        if self._active_provider == "openai":
            return {"Authorization": f"Bearer {self._openai_key}", "Content-Type": "application/json"}
        elif self._active_provider == "anthropic":
            return {"x-api-key": self._anthropic_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        elif self._active_provider == "huggingface":
            return {"Authorization": f"Bearer {self._hf_key}"}
        elif self._active_provider == "gemini":
            return {"Content-Type": "application/json"} # Gemini key goes in URL, not header

    # ==========================
    # 3. CHAT LOGIC
    # ==========================
    def ask(self, prompt):
        try:
            if not self._active_provider: return "Error: Set an API key first."
            
            # --- OpenAI ---
            if self._active_provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                payload = {"model": self._model, "messages": [{"role": "user", "content": prompt}]}
                res = requests.post(url, headers=self._get_headers(), json=payload).json()
                return res['choices'][0]['message']['content']

            # --- Anthropic ---
            elif self._active_provider == "anthropic":
                url = "https://api.anthropic.com/v1/messages"
                payload = {"model": self._model, "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}
                res = requests.post(url, headers=self._get_headers(), json=payload).json()
                return res['content'][0]['text']

            # --- Gemini (NEW) ---
            elif self._active_provider == "gemini":
                # Google uses a different URL format
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._gemini_key}"
                
                # Google's JSON format is unique
                payload = {
                    "contents": [{
                        "parts": [{"text": f"{self.system_prompt}\n\nUser: {prompt}"}]
                    }]
                }
                
                response = requests.post(url, headers=self._get_headers(), json=payload)
                if response.status_code != 200:
                    return f"Gemini Error ({response.status_code}): {response.text}"
                
                return response.json()['candidates'][0]['content']['parts'][0]['text']

            # --- HuggingFace ---
            elif self._active_provider == "huggingface":
                payload = {"inputs": f"{self.system_prompt}\nUser: {prompt}"}
                url = f"https://api-inference.huggingface.co/models/{self._model}"
                response = requests.post(url, headers=self._get_headers(), json=payload)
                
                if response.status_code in [404, 410]:
                    url = f"https://router.huggingface.co/models/{self._model}"
                    response = requests.post(url, headers=self._get_headers(), json=payload)

                if response.status_code != 200: return f"Error ({response.status_code}): {response.text}"
                res = response.json()
                if isinstance(res, list) and 'generated_text' in res[0]: return res[0]['generated_text']
                return str(res)

        except Exception as e: return f"Critical Error: {e}"

    def set_personality(self, text):
        self.system_prompt = text

    def generate_image(self, prompt):
        return "Image Gen not loaded."

ai = _AIHandler()