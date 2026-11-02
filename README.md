# AI-Powered Palm Reading & Chatbot (NIBM KIC – Digital Image Processing, ICA 01)

A Streamlit app that takes a left and a right palm photo, validates them, runs them through an OpenCV
pipeline, marks the palm lines it can find *with confidence*, then asks Gemini (grounded in a small
palmistry knowledge base) for a structured reading. You can then chat about the reading.

> **Palmistry is a cultural / entertainment practice, not a scientifically validated method.** The
> reading must not be used for medical, financial, employment, relationship or other consequential
> decisions. The disclaimer is shown in the UI, appended to the report in code, and appended to every
> chatbot answer in code (it does not depend on the model remembering to write it).

## Setup (Windows; on macOS/Linux use `source .venv/bin/activate`)

### 1. Python Backend & Engine
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # then edit .env and paste your key; never commit .env

# Option A: Run FastAPI Core Backend (for React Frontend)
python server.py              # runs at http://127.0.0.1:8000

# Option B: Run Streamlit Application
streamlit run app.py          # opens http://localhost:8501
```

### 2. Modern React Frontend (Vite + TypeScript)
```powershell
cd frontend
npm install
npm run dev                   # opens http://127.0.0.1:5173
```
Tested with Python 3.13 and the exact versions pinned in `requirements.txt` (checked in a fresh venv). For the tests, report builder and UI test: `pip install -r requirements-dev.txt`.

### Environment variables
| Variable | Required | Meaning |
|---|---|---|
| `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) | for report + chat | Google AI Studio key: <https://aistudio.google.com/apikey>. Without it the image-processing tabs still work and the Reading tab shows a clear "no key" message. |
| `GEMINI_MODEL` | no | Force a specific model. **Leave unset (recommended)**: the app asks the API which models your key can use and picks the first of `gemini-3.6-flash`, `gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-2.5-flash`. |

`gemini-2.0-flash` (the original default) is **shut down**; Google's deprecations page lists
2026-06-01. Run `python tools/check_gemini.py` to see which models *your* key can use and to make a test call.

Errors shown to the user: missing key, rejected key (401/403), unknown/retired model (404), quota or rate
limit (429), network failure, and invalid JSON from the model — each with the fix.

## Using the app
1. Upload the left and right palm (JPG/JPEG/PNG). Each gets an instant quality verdict; fix problems by re-uploading in the same slot.
2. Click **Analyse palms**.
3. *Processing* tab: before → after panels for resize/grayscale, Gaussian blur, CLAHE (with histogram), segmentation, Sobel vs Canny, and thresholding + morphology.
4. *Detected features* tab: annotated palm. **Only confidently detected lines are drawn.** Uncertain and not-detected lines are listed in the legend and table, never drawn.
5. *Reading* tab → **Generate reading with Gemini** (needs the key). Download the report as Markdown.
6. *Chatbot* tab: ask follow-ups, e.g. "What differences are visible between my left and right palms?".

## Project structure
| File | Task | Role |
|---|---|---|
| `palmreader/segmentation.py` | 1, 2 | Adaptive hand segmentation: Lab distance-from-background (Otsu), Cr Otsu, Cr/Cb 2-means, fixed range; best candidate chosen by a "does it look like a hand" score; GrabCut fallback |
| `palmreader/validation.py` | 1 | Format/corruption check, EXIF rotation, resolution, hand-region blur (silhouette edge width), hand-region exposure/clipping, hand coverage, cut-off hand |
| `palmreader/preprocessing.py` | 2 | Resize+normalise, grayscale, Gaussian blur, CLAHE, segmentation overlay, black-hat, Sobel, Canny, global Otsu vs adaptive threshold, morphology; `COMPARISONS` defines the before/after panels |
| `palmreader/features.py` | 3 | Palm centre/orientation (distance transform + finger blobs), palm shape / hand type, skeleton-based heart/head/life/fate detection, confidence gates, annotation |
| `palmreader/knowledge_base.py` | 4 | Curated palmistry passages + TF-IDF retriever (RAG) |
| `palmreader/llm.py` | 4, 5 | Model resolution, error mapping, report generator, grounded multi-turn chatbot, enforced disclaimer |
| `palmreader/report.py` | 4 | Markdown rendering of the reading |
| `app.py` | 6 | Streamlit UI integrating everything (validation and analysis cached per file) |
| `tests/` | – | pytest suite on synthetic hands (no personal images, no network) |
| `tools/check_gemini.py` | – | Which Gemini model works with your key |
| `tools/run_photo_tests.py` | – | Runs the whole flow on your photos in `photos/` and saves evidence to `outputs/` |
| `tools/e2e_ui.py` | – | Drives the real UI in a browser (Playwright, synthetic images): uploads, validation, comparisons, annotation, no-key message, and — with a FAKE Gemini client — report + 4 chat turns |
| `tools/build_report_docx.py` | – | Builds the technical report `.docx` (uses `outputs/results.json` if present) |
| `docs/` | – | Screenshot checklist and viva cheat-sheet |

## LLM specialisation (documented approach)
- **Model/provider:** Google Gemini via the `google-genai` SDK (model auto-selected, see above).
- **Mechanism:** general-purpose LLM + RAG over a curated palmistry knowledge base (`knowledge_base.py`, 20 passages) + a strict system prompt. Passages for *detected or uncertain* lines, the hand type, and the general themes are injected; passages for lines that were not detected are not.
- **Input:** structured JSON from OpenCV (per-line status, confidence, curvature, prominence, start/end region; palm shape and hand type; notes). Pixel paths are stripped. **The model never sees the photos.**
- **Output:** a fixed JSON schema with 9 sections (palm characteristics, major lines, personality, career, finance, relationships, future narrative, left-vs-right, uncertainty); the disclaimer is added in code.
- **Safeguards:** system prompt forbids describing undetected features and requires Observed vs Traditional separation and hedged language; every line carries `detected | uncertain | not_detected`; the chatbot receives a deterministic `QUESTION_GROUNDING` note when the question names a line that is not detected on one or both hands; the disclaimer is appended in code.
- **Chatbot:** each turn gets the feature JSON, the report, the last 12 messages and passages retrieved for the question.

## Limitations (please read)
- **Real-photo performance is not established by this repository's tests.** The automated tests use synthetic hands. Thresholds (`EDGE_WIDTH_MAX`, `MIN_REL_DEPTH`, `MIN_CONTRAST`, `DETECT_T`, palm-shape ratios) are untuned on real photos until you run `tools/run_photo_tests.py` on your own; each result prints the measured values so you can adjust them.
- Line detection is classical computer vision with hand-written geometry rules, not a trained model. It works best on a flat, open, well-lit palm against a plain, contrasting background with the fingers spread. Cluttered or skin-coloured backgrounds fall back to GrabCut and may fail; the validator then rejects the photo rather than guessing.
- The confidence value is a heuristic score, not a probability. Fate lines are frequently reported `not_detected`, which is also common on real palms.
- Palm shape / hand type comes from silhouette ratios and is approximate; the thresholds are heuristics (justified in comments in `features.py`).
- Left/right labels come from the uploader slot; handedness is not verified.
- Chatbot grounding is enforced by prompts plus a deterministic note, not by a verifier; a model can still misbehave. The disclaimer, however, is appended in code.

## Testing
```powershell
python -m pytest            # whole suite (116 tests, ~1-2 min), warnings are treated as errors
python tools/e2e_ui.py      # browser test of the real UI with synthetic images (needs requirements-dev.txt)
python tools/run_photo_tests.py [--chat]   # your own photos (see photos/README.txt)
```
Covered: file/format validation, per-hand blur and exposure (including a white wall not triggering "overexposed"), adaptive segmentation across four skin tones, three backgrounds, rotated and mirrored hands, line detection and honest labelling (no lines on a crease-free palm, uncertain lines never drawn), palm-shape thresholds, retrieval, and the LLM layer with a **fake** client (prompts, grounding note, disclaimers, model choice, error messages). Tests with the fake client do not show what a real Gemini model would answer.

## Privacy
Images are held in memory only (never saved by the app). Only structured features and text, never the images, are sent to the Gemini API. The key is read from the environment/`.env`, never hard-coded; `.gitignore` excludes `.env`, `photos/` and `outputs/`.

## Acknowledgements and AI-assisted code
Third-party: OpenCV (opencv-python-headless), NumPy, scikit-image (skeletonize), Pillow, Streamlit, Google `google-genai` SDK and the Gemini API, pytest, python-docx (report builder). Palmistry passages in `knowledge_base.py` are paraphrased from widely repeated popular teaching, written for this project.
**Much of the code, tests, documentation and report template were drafted with AI assistance (Claude Code, Anthropic) and then run and checked by the author.** Declare this in your submission as section 10 of the brief requires.
