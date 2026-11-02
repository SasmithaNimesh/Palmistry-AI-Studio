"""Streamlit entry point for UI tests ONLY: runs the real app.py but swaps the Gemini client for a
FAKE one (canned replies). Proves the UI wiring, not what a real model would say.

    streamlit run tests/e2e_fake_app.py        (used by tools/e2e_ui.py)
"""
import json
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
os.environ["GEMINI_API_KEY"] = "fake-key-for-ui-test"
os.environ.pop("GEMINI_MODEL", None)

import palmreader.llm as llm  # noqa: E402
from fakes import FakeClient  # noqa: E402

if not getattr(llm, "_fake_installed", False):
    log = os.environ.get("FAKE_LLM_LOG")

    class LoggingClient(FakeClient):
        def __init__(self):
            super().__init__(chat_reply="(fake model) Tradition reads this feature in general terms only.")
            orig = self.models.generate_content

            def gen(model, contents, config):
                if log:
                    with open(log, "a", encoding="utf-8") as fh:
                        fh.write(json.dumps({"model": model, "system": str(config.system_instruction)[-1500:]}) + "\n")
                return orig(model=model, contents=contents, config=config)
            self.models.generate_content = gen

    llm._client = lambda: LoggingClient()
    llm._fake_installed = True

runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
