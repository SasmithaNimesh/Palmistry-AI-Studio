"""Drive the real Streamlit UI in a browser (Playwright + installed Edge/Chrome) with SYNTHETIC images.

    pip install playwright          (no browser download needed: uses your installed Edge/Chrome)
    python tools/e2e_ui.py [--shots DIR]

Scenario A  real app, no API key : uploads, validation, processing, annotation, "no key" message.
Scenario B  app with a FAKE Gemini client (tests/e2e_fake_app.py): report, 4 chat turns,
            disclaimer in UI / report / every answer, grounding note for a not-detected line.
Scenario C  bad image: blurry upload is rejected, Analyse disabled, replacement accepted; .gif rejected.

Scenario B proves the UI wiring only. It cannot show what real Gemini answers.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import cv2

import _env

sys.path.insert(0, str(_env.ROOT / "tests"))
from synthetic import synthetic_hand  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Server:
    def __init__(self, script: str, env_extra: dict, drop_key: bool):
        self.port = free_port()
        env = {k: v for k, v in os.environ.items() if not (drop_key and k in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_MODEL"))}
        env.update(env_extra)
        env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        self.log = tempfile.NamedTemporaryFile("w+", suffix=".log", delete=False)
        self.proc = subprocess.Popen(
            [os.environ.get("E2E_SERVER_PYTHON", sys.executable), "-m", "streamlit", "run", script, "--server.headless", "true", "--server.port", str(self.port),
             "--browser.gatherUsageStats", "false"],
            cwd=_env.ROOT, env=env, stdout=self.log, stderr=subprocess.STDOUT)
        self.url = f"http://localhost:{self.port}"
        for _ in range(60):
            try:
                if urllib.request.urlopen(f"{self.url}/_stcore/health", timeout=1).read() == b"ok":
                    return
            except Exception:  # noqa: BLE001
                time.sleep(1)
        raise RuntimeError("streamlit did not start")

    def stop(self) -> str:
        self.proc.terminate()
        try:
            self.proc.wait(10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.log.flush()
        return Path(self.log.name).read_text(errors="replace")


def make_images(d: Path) -> dict[str, Path]:
    files = {}
    for name, kw in {"pair1_left": dict(tone="light"), "pair1_right": dict(tone="light", mirror=True),
                     "pair2_left": dict(tone="deep", bg="grey"), "pair2_right": dict(tone="deep", bg="grey", mirror=True),
                     "blurry": dict(tone="medium", blur=5.0)}.items():
        img, _ = synthetic_hand(**kw)
        p = d / f"{name}.png"
        cv2.imwrite(str(p), img)
        files[name] = p
    (d / "notes.gif").write_bytes(b"GIF89a-not-a-palm")
    files["gif"] = d / "notes.gif"
    return files


def upload(page, idx: int, path: Path):
    page.locator('input[type="file"]').nth(idx).set_input_files(str(path))
    page.wait_for_timeout(2500)


def body(page) -> str:
    return page.locator("body").inner_text()


def tab(page, name: str):
    page.get_by_role("tab", name=name).click()
    page.wait_for_timeout(800)


def scenario_a(browser, files, shots: Path):
    srv = Server("app.py", {}, drop_key=True)
    try:
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.goto(srv.url)
        page.wait_for_selector("text=AI-Powered Palm Reading")
        t = body(page)
        check("A: disclaimer banner in UI", "entertainment" in t.lower())
        check("A: sidebar says key missing", "missing" in t.lower())
        page.screenshot(path=str(shots / "A1_home.png"))
        upload(page, 0, files["pair1_left"])
        upload(page, 1, files["pair1_right"])
        t = body(page)
        check("A: both palms accepted", t.count("Image accepted") == 2, f"{t.count('Image accepted')} accepted")
        page.screenshot(path=str(shots / "A2_uploads.png"))
        page.get_by_role("button", name="Analyse palms").click()
        page.wait_for_selector("text=original vs processed", timeout=90000)
        t = body(page)
        for title in ("Contrast enhancement (CLAHE)", "Edge detection (Sobel vs Canny)", "Thresholding + morphology", "Noise reduction (Gaussian blur)"):
            check(f"A: comparison panel '{title}'", title in t)
        check("A: before/after captions", "Before:" in t and "After:" in t)
        page.screenshot(path=str(shots / "A3_processing.png"), full_page=True)
        tab(page, "2 · Detected features")
        page.wait_for_selector("text=Right palm: annotated", timeout=30000)
        page.wait_for_timeout(1500)
        t = body(page)
        check("A: status table shows detected and not detected lines", "Fate Line" in t and "not detected" in t and "Heart Line" in t)
        check("A: annotated images for both palms", "Left palm: annotated" in t and "Right palm: annotated" in t)
        page.screenshot(path=str(shots / "A4_features.png"), full_page=True)
        tab(page, "3 · Reading")
        page.get_by_role("button", name="Generate reading with Gemini").click()
        page.wait_for_selector("text=No Gemini API key found", timeout=30000)
        check("A: missing-key message is clear", True)
        page.screenshot(path=str(shots / "A5_no_key.png"))
        page.close()
    finally:
        log = srv.stop()
    check("A: no Python traceback in server log", "Traceback" not in log, log[-400:])
    return log


def scenario_b(browser, files, shots: Path):
    fake_log = Path(tempfile.mkstemp(suffix=".jsonl")[1])
    fake_log.write_text("")
    srv = Server("tests/e2e_fake_app.py", {"FAKE_LLM_LOG": str(fake_log)}, drop_key=True)
    try:
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.goto(srv.url)
        page.wait_for_selector("text=AI-Powered Palm Reading")
        upload(page, 0, files["pair2_left"])
        upload(page, 1, files["pair2_right"])
        check("B: pair 2 (deep skin, grey bg) accepted", body(page).count("Image accepted") == 2)
        page.get_by_role("button", name="Analyse palms").click()
        page.wait_for_selector("text=original vs processed", timeout=90000)
        tab(page, "3 · Reading")
        page.get_by_role("button", name="Generate reading with Gemini").click()
        page.wait_for_selector("text=Left vs right comparison", timeout=60000)
        t = body(page)
        check("B: report sections rendered", all(s in t for s in ("Major lines", "Career themes", "Financial themes", "Uncertainty & limits")))
        check("B: disclaimer in report", t.lower().count("entertainment") >= 2)
        check("B: download button present", "Download report (Markdown)" in t)
        page.screenshot(path=str(shots / "B1_report.png"), full_page=True)
        tab(page, "4 · Chatbot")
        questions = ["What does my heart line traditionally represent?",
                     "What differences are visible between my left and right palms?",
                     "What does palmistry say about my career?",
                     "Tell me about my fate line."]
        box = page.get_by_test_id("stChatInputTextArea")
        for i, q in enumerate(questions, 1):
            box.fill(q)
            box.press("Enter")
            page.wait_for_selector("text=(fake model)", timeout=30000)
            page.wait_for_function(f"document.querySelectorAll('[data-testid=\"stChatMessage\"]').length >= {2 * i}", timeout=30000)
            page.wait_for_timeout(500)
        msgs = page.locator('[data-testid="stChatMessage"]').all_inner_texts()
        answers = msgs[1::2]
        check("B: 4 chat turns completed", len(answers) == 4, f"{len(answers)} answers")
        check("B: disclaimer appended to every chat answer", all("entertainment" in a.lower() for a in answers))
        page.screenshot(path=str(shots / "B2_chat.png"), full_page=True)
        calls = [json.loads(l) for l in fake_log.read_text().splitlines() if l.strip()]
        grounded = [c for c in calls if "QUESTION_GROUNDING: the user asks about the fate line" in c["system"]]
        check("B: fate-line question was sent with the grounding note", len(grounded) == 1, f"{len(grounded)} calls")
        check("B: model name was auto-resolved, not gemini-2.0-flash", all("2.0" not in c["model"] for c in calls), str({c['model'] for c in calls}))
        page.reload()
        page.wait_for_selector("text=AI-Powered Palm Reading")
        page.close()
    finally:
        log = srv.stop()
    check("B: no Python traceback in server log", "Traceback" not in log, log[-400:])
    return log


def scenario_c(browser, files, shots: Path):
    srv = Server("app.py", {}, drop_key=True)
    try:
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.goto(srv.url)
        page.wait_for_selector("text=AI-Powered Palm Reading")
        upload(page, 0, files["blurry"])
        upload(page, 1, files["pair1_right"])
        t = body(page)
        check("C: blurry hand rejected with actionable message", "looks blurry" in t and "Hold the phone steady" in t)
        check("C: Analyse button disabled", page.get_by_role("button", name="Analyse palms").is_disabled())
        page.screenshot(path=str(shots / "C1_blurry.png"))
        upload(page, 0, files["gif"])
        check("C: unsupported .gif rejected", "not supported" in body(page))
        upload(page, 0, files["pair1_left"])
        t = body(page)
        check("C: replacement accepted and Analyse enabled", t.count("Image accepted") == 2 and page.get_by_role("button", name="Analyse palms").is_enabled())
        page.screenshot(path=str(shots / "C2_replaced.png"))
        page.close()
    finally:
        log = srv.stop()
    check("C: no Python traceback in server log", "Traceback" not in log, log[-400:])
    return log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default=str(Path(tempfile.gettempdir()) / "palm_e2e_shots"))
    a = ap.parse_args()
    shots = Path(a.shots)
    shots.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="palm_e2e_imgs_"))
    files = make_images(work)
    logs = {}
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="msedge", headless=True)
        except Exception:  # noqa: BLE001
            browser = pw.chromium.launch(channel="chrome", headless=True)
        for name, fn in (("A", scenario_a), ("B", scenario_b), ("C", scenario_c)):
            try:
                logs[name] = fn(browser, files, shots)
            except Exception as e:  # noqa: BLE001
                check(f"{name}: scenario ran to the end", False, repr(e)[:300])
        browser.close()
    warn = [l for n, lg in logs.items() for l in (lg or "").splitlines() if "Warning" in l or "deprecat" in l.lower()]
    check("no Streamlit/Python warnings or deprecations in any server log", not warn, "; ".join(warn[:3]))
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed. Screenshots (of SYNTHETIC images) in {shots}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
