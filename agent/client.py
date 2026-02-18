import os
from pathlib import Path


# Load .env into environment if present
def _load_dotenv_if_present(path: str = None):
    try:
        from dotenv import load_dotenv
        load_dotenv(path)
        return
    except Exception:
        pass

    # Fallback: simple .env parser
    env_path = Path(path) if path else Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k not in os.environ:
                os.environ[k] = v


_load_dotenv_if_present()


class _DummyCompletions:
    def create(self, model, messages):
        raise RuntimeError("No API client configured. Set GROQ_API_KEY or OPENAI_API_KEY in .env or environment, or modify agent/client.py to use another provider.")


class _Chat:
    def __init__(self, impl):
        self.completions = impl


class _Client:
    def __init__(self):
        # Prefer GROQ if present
        groq_key = os.environ.get("GROQ_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")

        if groq_key:
            # Configure Groq-backed completions
            try:
                import requests

                # Prefer using Groq SDK if installed, otherwise fall back to requests
                try:
                    import groq as groq_sdk
                except Exception:
                    groq_sdk = None

                class _GroqCompletions:
                    def __init__(self, api_key: str):
                        self.api_key = api_key
                        self.endpoint = os.environ.get("GROQ_API_URL", "https://api.groq.ai/v1/llm/chat/completions")
                        self._sdk = groq_sdk

                    def create(self, model, messages):
                        # If SDK is available, try to use it with a few common interfaces
                        if self._sdk is not None:
                            try:
                                # Try common constructor patterns
                                client = None
                                if hasattr(self._sdk, "Client"):
                                    try:
                                        client = self._sdk.Client(api_key=self.api_key)
                                    except Exception:
                                        try:
                                            client = self._sdk.Client(self.api_key)
                                        except Exception:
                                            client = None

                                if client is None and hasattr(self._sdk, "Client") is False:
                                    # Maybe SDK exposes top-level functions
                                    client = self._sdk

                                # Try common call paths
                                if hasattr(client, "chat") and hasattr(client.chat, "completions") and hasattr(client.chat.completions, "create"):
                                    return client.chat.completions.create(model=model, messages=messages)
                                if hasattr(client, "completions") and hasattr(client.completions, "create"):
                                    return client.completions.create(model=model, messages=messages)
                                if hasattr(client, "create"):
                                    return client.create(model=model, messages=messages)
                            except Exception:
                                # Fall through to HTTP fallback
                                pass

                        # Fallback: HTTP POST to Groq endpoint
                        headers = {
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        }
                        payload = {"model": model, "messages": messages}
                        resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
                        try:
                            resp.raise_for_status()
                        except Exception as e:
                            raise RuntimeError(f"Groq API request failed: {e} - {resp.text}")
                        # return parsed json-like object; SDKs may return different shapes
                        return resp.json()

                self.chat = _Chat(_GroqCompletions(groq_key))
            except Exception:
                # requests missing or other issue
                self.chat = _Chat(_DummyCompletions())

        elif openai_key:
            try:
                import openai
                openai.api_key = openai_key

                class _OpenAICompletions:
                    def create(self, model, messages):
                        return openai.ChatCompletion.create(model=model, messages=messages)

                self.chat = _Chat(_OpenAICompletions())
            except Exception:
                self.chat = _Chat(_DummyCompletions())

        else:
            self.chat = _Chat(_DummyCompletions())


# module-level client instance
client = _Client()


def get_client():
    """Return the initialized client instance."""
    return client
