import requests
import os

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
        # FIX: Only switch to OpenAI if it is explicitly a GPT/DALL-E model
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
        elif provider == "huggingface": self._model = "HuggingFaceH4/zephyr-7b-beta"

    def _get_headers(self):
        if self._active_provider == "openai":
            return {"Authorization": f"Bearer {self._openai_key}", "Content-Type": "application/json"}
        elif self._active_provider == "anthropic":
            return {"x-api-key": self._anthropic_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        elif self._active_provider == "huggingface":
            return {"Authorization": f"Bearer {self._hf_key}"}

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
                
                payload = {"model": self._model, "messages": messages}
                res = requests.post(url, headers=self._get_headers(), json=payload).json()
                
                answer = res['choices'][0]['message']['content']
                self.history.append({"role": "assistant", "content": answer})
                return answer

            # --- Anthropic ---
            elif self._active_provider == "anthropic":
                url = "https://api.anthropic.com/v1/messages"
                self.history.append({"role": "user", "content": prompt})
                
                payload = {
                    "model": self._model, 
                    "max_tokens": 1024, 
                    "system": self.system_prompt,
                    "messages": self.history
                }
                res = requests.post(url, headers=self._get_headers(), json=payload).json()
                answer = res['content'][0]['text']
                self.history.append({"role": "assistant", "content": answer})
                return answer

            # --- HuggingFace (FIXED) ---
            elif self._active_provider == "huggingface":
                # Use the new Router URL
                url = f"https://router.huggingface.co/models/{self._model}"
                full_prompt = f"System: {self.system_prompt}\nUser: {prompt}"
                
                # Make the request
                response = requests.post(url, headers=self._get_headers(), json={"inputs": full_prompt})
                
                # SAFETY CHECK: If the API returns an error (404, 401, 500), return the text, don't crash.
                if response.status_code != 200:
                    return f"HuggingFace API Error ({response.status_code}): {response.text}"
                
                # Only try to read JSON if the status was 200 OK
                res = response.json()
                if isinstance(res, list) and 'generated_text' in res[0]: 
                    return res[0]['generated_text']
                return str(res)

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