"""Offline stand-in for the google-genai client. FAKE: it returns canned text, so tests using it
prove the plumbing (prompts, grounding, disclaimer enforcement, error mapping), NOT what a real
Gemini model would say."""
import json
from types import SimpleNamespace

from palmreader.llm import SECTIONS


class FakeModels:
    def __init__(self, available=("gemini-3.6-flash",), chat_reply="Your heart line tradition says X.",
                 raises=None):
        self.available, self.chat_reply, self.raises = available, chat_reply, raises
        self.calls = []                      # (model, contents, config)

    def list(self):
        return [SimpleNamespace(name=f"models/{n}", supported_actions=["generateContent"]) for n in self.available]

    def generate_content(self, model, contents, config):
        self.calls.append((model, contents, config))
        if self.raises:
            raise self.raises
        if getattr(config, "response_mime_type", None) == "application/json":
            return SimpleNamespace(text=json.dumps({s: f"Canned text for {s}." for s in SECTIONS}))
        return SimpleNamespace(text=self.chat_reply)


class FakeClient:
    def __init__(self, **kw):
        self.models = FakeModels(**kw)


class ApiError(Exception):
    """Mimics google.genai.errors.APIError (has .code)."""
    def __init__(self, code, msg):
        super().__init__(f"{code} {msg}")
        self.code = code
