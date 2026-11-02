"""Task 04/05 plumbing with a FAKE client: prompts, grounding, disclaimers, model choice, errors."""
import json

import pytest

from fakes import ApiError, FakeClient
from palmreader import DISCLAIMER, llm
from palmreader.knowledge_base import Retriever
from palmreader.llm import LLMError, PalmChatbot, generate_report, strip_paths, with_disclaimer
from palmreader.report import report_to_markdown


def line(status, conf=0.0):
    return dict(status=status, confidence=conf, curvature=None, prominence=None, start_region=None,
                end_region=None, path=[[1, 2]], ridge_contrast=3.0)


FEATS = {side: {"side": side, "palm_detected": True, "notes": [],
                "palm": {"palm_shape": "square", "finger_length": "short", "palmistry_hand_type": "Earth",
                         "palm_length_to_width": 1.0, "finger_to_palm_length": 0.7, "note": "approximate"},
                "lines": {"heart_line": line("detected", .7), "head_line": line("detected", .66),
                          "life_line": line("uncertain", .4), "fate_line": line("not_detected")}}
         for side in ("Left", "Right")}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for k in ("GEMINI_MODEL", "GOOGLE_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    llm._resolved.clear()


def make_bot(**kw):
    client = FakeClient(**kw)
    report, _ = generate_report(FEATS, Retriever(), client=client)
    return PalmChatbot(FEATS, report, Retriever(), client=client), client, report


def test_default_model_is_not_the_retired_one():
    assert "2.0" not in llm.DEFAULT_MODEL
    assert all("gemini-2.0" not in m for m in llm.MODEL_PREFERENCE)


def test_model_resolution_prefers_first_available(monkeypatch):
    c = FakeClient(available=("gemini-2.5-flash", "gemini-3.8-flash"))
    assert llm.resolve_model(c) == "gemini-3.8-flash"
    monkeypatch.setenv("GEMINI_MODEL", "my-model")
    assert llm.resolve_model(c) == "my-model"


def test_no_supported_model_gives_clear_error():
    with pytest.raises(LLMError, match="GEMINI_MODEL"):
        llm.resolve_model(FakeClient(available=("gemini-2.0-flash",)))


def test_missing_key_message(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY")
    with pytest.raises(LLMError, match="GEMINI_API_KEY"):
        generate_report(FEATS, Retriever())


@pytest.mark.parametrize("code,needle", [(401, "rejected the API key"), (403, "rejected the API key"),
                                         (404, "not available"), (429, "quota")])
def test_http_errors_become_friendly_messages(code, needle):
    client = FakeClient(raises=ApiError(code, "boom"))
    with pytest.raises(LLMError, match=needle):
        generate_report(FEATS, Retriever(), client=client)


def test_bad_json_is_reported_not_crashed():
    client = FakeClient()
    client.models.generate_content = lambda **k: type("R", (), {"text": "not json"})()
    with pytest.raises(LLMError, match="valid JSON"):
        generate_report(FEATS, Retriever(), client=client)


def test_report_gets_all_sections_and_code_added_disclaimer():
    _, _, report = make_bot()
    assert all(k in report for k in llm.SECTIONS)
    assert report["disclaimer"] == DISCLAIMER
    md = report_to_markdown(report, FEATS)
    assert DISCLAIMER in md and md.rstrip().endswith("**")
    assert "Left palm" in md and "Right palm" in md


def test_llm_never_receives_pixel_paths_or_tuning_values():
    _, client, _ = make_bot()
    prompt = client.models.calls[0][1]
    assert '"path"' not in prompt and "ridge_contrast" not in prompt
    assert "not_detected" in prompt and "uncertain" in prompt          # statuses reach the model
    assert "path" not in json.dumps(strip_paths(FEATS))


def test_report_prompt_contains_only_retrieved_knowledge_for_observed_lines():
    _, client, _ = make_bot()
    prompt = client.models.calls[0][1]
    assert "[heart-1]" in prompt and "[safe-1]" in prompt


def test_every_chat_answer_carries_the_disclaimer_even_if_model_forgets():
    bot, _, _ = make_bot(chat_reply="Tradition reads a long line as openness.")
    for q in ["What does my heart line represent?",
              "What differences are visible between my left and right palms?",
              "What does palmistry say about my career?"]:
        a = bot.ask(q)
        assert "entertainment" in a.lower()
    assert len(bot.history) == 6


def test_disclaimer_not_duplicated():
    once = with_disclaimer("hello")
    assert with_disclaimer(once) == once


def test_question_about_undetected_line_is_grounded():
    bot, client, _ = make_bot()
    bot.ask("What does my fate line say about my career?")
    system = client.models.calls[-1][2].system_instruction
    assert "QUESTION_GROUNDING: the user asks" in system
    assert "Left: not detected" in system and "Right: not detected" in system
    assert "must NOT describe" in system


def test_question_about_detected_line_has_no_refusal_note():
    bot, client, _ = make_bot()
    bot.ask("Explain my heart line")
    assert "QUESTION_GROUNDING: the user asks" not in client.models.calls[-1][2].system_instruction


def test_uncertain_line_is_also_grounded():
    bot, client, _ = make_bot()
    bot.ask("Can you explain my life line in more detail?")
    system = client.models.calls[-1][2].system_instruction
    assert "life line" in system and "uncertain" in system


def test_chat_context_includes_observed_features_and_report():
    bot, client, _ = make_bot()
    bot.ask("Compare my left and right palms")
    system = client.models.calls[-1][2].system_instruction
    assert "OBSERVED_FEATURES" in system and "GENERATED_REPORT" in system and "Canned text" in system
