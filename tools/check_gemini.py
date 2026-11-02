"""Check which Gemini model works with YOUR key.

    python tools/check_gemini.py

Prints the Gemini models your key can use for generateContent, which one the app will pick, and
makes one tiny test call. Never prints the key.
"""
import _env
_env.load_dotenv()

from palmreader import llm  # noqa: E402


def main() -> int:
    try:
        client = llm._client()
    except llm.LLMError as e:
        print("FAIL:", e)
        return 1
    try:
        names = sorted(m.name.split("/")[-1] for m in client.models.list()
                       if "generateContent" in (getattr(m, "supported_actions", None) or ["generateContent"]))
    except Exception as e:  # noqa: BLE001
        print("FAIL listing models:", llm.friendly_error(e))
        return 1
    print(f"{len(names)} models support generateContent for this key. Gemini ones:")
    for n in names:
        if n.startswith("gemini"):
            print("  ", n, "<- preferred" if n in llm.MODEL_PREFERENCE else "")
    try:
        model = llm.resolve_model(client)
    except llm.LLMError as e:
        print("FAIL:", e)
        return 1
    print("App will use:", model)
    try:
        r = client.models.generate_content(model=model, contents="Reply with the single word: ok")
        print("Test call OK ->", (r.text or "").strip()[:40])
    except Exception as e:  # noqa: BLE001
        print("FAIL test call:", llm.friendly_error(e, model))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
