# Screenshot checklist (evidence for section 8 of the brief)

Take these yourself, from the running app, with **your own consented photos**. Do not edit or
mock up any screenshot. Blur faces/backgrounds if anything identifying is in the frame; the palms
themselves are the evidence. Save as the file name in the last column so the report builder and
your viva slides can find them (`docs/screenshots/` — this folder is not zipped by default; add the
PNGs to the report yourself).

Before you start: `streamlit run app.py`, browser at 100% zoom, window ~1400 px wide, key set in `.env`.
Run `python tools/run_photo_tests.py --chat` once first so you know what each pair will show.

| # | Screen to capture | What must be visible | Brief requirement | Save as |
|---|---|---|---|---|
| 1 | App on first load | Title, **entertainment disclaimer banner**, sidebar (key ✅, model name) | UI, disclaimer | `01_home.png` |
| 2 | **Pair 1 — both uploads** | Left and Right uploader previews with file names and the green "Image accepted" metrics line | Dual upload + previews | `02_pair1_uploads.png` |
| 3 | **Failure case** (pair "bad") | Red, actionable error(s) under the bad image (blurry / dark / cut-off) and the info line "Fix the problems above…" with *Analyse palms* greyed out | Validation, error case | `03_bad_image_error.png` |
| 4 | **Replacement** | After re-uploading a good image in the same slot: green accepted message | Re-upload | `04_reupload_ok.png` |
| 5 | Unsupported / corrupt file | Upload a `.gif` or a text file renamed `.jpg` → red "not supported" / "corrupted" message | Reject unsupported/corrupt | `05_unsupported_file.png` |
| 6 | **Processing tab, Left, pair 1 (a)** | "Resize + normalise → grayscale" and "Gaussian blur" before→after panels | Preprocessing | `06a_left_resize_blur.png` |
| 7 | Processing tab, Left, pair 1 (b) | **CLAHE** panel with before, after and the histogram | Contrast enhancement | `06b_left_clahe.png` |
| 8 | Processing tab, Left, pair 1 (c) | **Segmentation** overlay and **Sobel vs Canny** panels | Edge detection, segmentation | `06c_left_segmentation_edges.png` |
| 9 | Processing tab, Left, pair 1 (d) | **Thresholding + morphology**: black-hat, global Otsu, adaptive result | Thresholding, morphology | `06d_left_threshold.png` |
| 10 | Processing tab, Right, pair 1 | At least the CLAHE and thresholding panels for the right palm | Both palms processed | `07_right_processing.png` |
| 11 | "All pipeline stages" expander (open) | The full grid of stages | Transparency | `08_all_stages.png` |
| 12 | **Detected features tab, pair 1** | Annotated Left and Right palms, **legend in the corner**, status table | Annotated palm lines | `09_pair1_annotated.png` |
| 13 | Detected features tab, pair 2 | Same | ≥3 pairs | `10_pair2_annotated.png` |
| 14 | Detected features tab, pair 3 | Same | ≥3 pairs | `11_pair3_annotated.png` |
| 15 | A line that is **uncertain / not detected** | Legend showing "uncertain (not drawn)" or "not detected" and the matching table row, no line drawn for it | Uncertain/absent features marked | `12_uncertain_not_drawn.png` |
| 16 | **Reading tab (top)** | Palm characteristics, Major lines (Observed vs Traditional) | Report | `13_report_top.png` |
| 17 | Reading tab (middle) | Career, finance, relationships, future narrative | Report themes | `14_report_middle.png` |
| 18 | Reading tab (bottom) | **Left vs right comparison**, Uncertainty & limits, **disclaimer box**, Download button | Comparison, uncertainty, disclaimer | `15_report_bottom.png` |
| 19 | RAG expander (open) | "Knowledge passages retrieved for this reading" | LLM specialisation evidence | `16_rag_passages.png` |
| 20 | **Chatbot, turns 1-2** | "What does my heart line traditionally represent?" and "What differences are visible between my left and right palms?" with answers; **disclaimer under each answer** | Chatbot | `17_chat_1_2.png` |
| 21 | **Chatbot, not-detected line** | A question about a line your table shows as *not detected* (often the fate line) and the answer that says it was not detected and does not describe it | Grounding, no invented features | `18_chat_not_detected.png` |
| 22 | Chatbot, turns 3-4+ | Career question + one more follow-up (≥4 turns total in one thread) | Multi-turn | `19_chat_3_4.png` |
| 23 | Downloaded report | The `.md` file open in an editor, disclaimer at top and bottom | Report generation | `20_downloaded_report.png` |
| 24 | Terminal: install + start | `pip install -r requirements.txt` finishing in a fresh venv, then `streamlit run app.py` printing the URL with no errors | Reproducibility | `21_install_run.png` |
| 25 | Terminal: tests | `python -m pytest` final summary line (all passed, no warnings) | Testing | `22_pytest.png` |
| 26 | Terminal: Gemini check | `python tools/check_gemini.py` output showing which model your key uses | Model documentation | `23_check_gemini.png` |
| 27 | Terminal: photo run | `python tools/run_photo_tests.py --chat` summary for all pairs | Test findings | `24_photo_tests.png` |
| 28 | (Optional) Missing-key message | Rename `.env`, restart, click *Generate reading*: the red "No Gemini API key found…" message | Error handling | `25_missing_key.png` |

Tips
- Capture the Detected-features screenshots **after** you have looked at them: if a line is drawn in the wrong place, say so in the report. Honest findings score better than a perfect-looking table.
- Do not capture your `.env` file or the key. If you show a terminal, `check_gemini.py` never prints the key.
- Use the same pairs in screenshots 2, 6-12 and 16-22 so the story is continuous.
