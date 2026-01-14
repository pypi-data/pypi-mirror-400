import requests
import os
# We import the official tool safely
try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

class _AIHandler:
    def __init__(self):
        self._openai_key = os.getenv("OPENAI_API_KEY")
        self._anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self._hf_key = os.getenv("HUGGINGFACE_API_KEY")
        self._model = None
        self._active_provider = None
        
        # Memory & Persona
        self.history = [] 
        self.system_prompt = "You are a helpful assistant."

    # --- PROPERTIES ---
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
        if "gpt-3" in model_name or "gpt-4" in model_name or "dall" in model_name: 
            self._active_provider = "openai"
        elif "claude" in model_name: 
            self._active_provider = "anthropic"
        else: 
            self._active_provider = "huggingface"

    def _set_provider(self, provider):
        self._active_provider = provider
        if provider == "openai": self._model = "gpt-4o"
        elif provider == "anthropic": self._model = "claude-3-5-sonnet-20240620"
        elif provider == "huggingface": self._model = "mistralai/Mistral-7B-Instruct-v0.3"

    def _get_headers(self):
        # Only needed for OpenAI/Anthropic now
        if self._active_provider == "openai":
            return {"Authorization": f"Bearer {self._openai_key}", "Content-Type": "application/json"}
        elif self._active_provider == "anthropic":
            return {"x-api-key": self._anthropic_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}

    # --- PUBLIC FUNCTIONS ---

    def set_personality(self, text):
        self.system_prompt = text
        self.history = []

    def clear_memory(self):
        self.history = []

    def ask(self, prompt):
        try:
            if not self._active_provider: return "Error: Set an API key first."
            
            # --- OpenAI ---
            if self._active_provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                self.history.append({"role": "user", "content": prompt})
                messages = [{"role": "system", "content": self.system_prompt}] + self.history
                
                res = requests.post(url, headers=self._get_headers(), json={"model": self._model, "messages": messages}).json()
                answer = res['choices'][0]['message']['content']
                self.history.append({"role": "assistant", "content": answer})
                return answer

            # --- Anthropic ---
            elif self._active_provider == "anthropic":
                url = "https://api.anthropic.com/v1/messages"
                self.history.append({"role": "user", "content": prompt})
                
                payload = {
                    "model": self._model, "max_tokens": 1024, "system": self.system_prompt, "messages": self.history
                }
                res = requests.post(url, headers=self._get_headers(), json=payload).json()
                answer = res['content'][0]['text']
                self.history.append({"role": "assistant", "content": answer})
                return answer

            # --- HuggingFace (THE NEW PRO WAY) ---
            elif self._active_provider == "huggingface":
                if InferenceClient is None:
                    return "Error: Please run 'pip install huggingface_hub' to use Open Source models."
                
                # We use the official client. It handles URLs and Errors automatically.
                client = InferenceClient(token=self._hf_key)
                
                # Combine system prompt and user prompt
                full_prompt = f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:"
                
                try:
                    return client.text_generation(full_prompt, model=self._model, max_new_tokens=500)
                except Exception as hf_error:
                    return f"HuggingFace Error: {hf_error}"

        except Exception as e: return f"Critical Error: {e}"

    def generate_image(self, prompt):
        if self._openai_key:
            url = "https://api.openai.com/v1/images/generations"
            payload = {"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1024x1024"}
            headers = {"Authorization": f"Bearer {self._openai_key}", "Content-Type": "application/json"}
            res = requests.post(url, headers=headers, json=payload).json()
            try:
                return res['data'][0]['url']
            except:
                return f"Error generation image: {res}"
        else:
            return "Error: You need to set ai.openai_key to generate images."

ai = _AIHandler()