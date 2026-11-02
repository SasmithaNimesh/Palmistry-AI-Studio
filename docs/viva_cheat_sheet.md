# Viva cheat-sheet — AI Palm Reading & Chatbot

Say first, every time: **palmistry is entertainment, not science.** The marks reward the engineering,
not the predictions.

## 1. The pipeline in one breath
Upload → validate → resize/normalise → grayscale → Gaussian blur → CLAHE → segment the hand →
black-hat → Sobel + Canny → adaptive threshold + morphology → skeletonise → score creases as heart /
head / life / fate → draw only the confident ones → feed *structured facts* (never the photos) plus
retrieved palmistry passages to Gemini → report → chatbot that is handed the same facts.

## 2. Every technique, in plain English (and why)

| Technique | What it does | Why we used it | Parameters in our code |
|---|---|---|---|
| **Resize to 900 px wide + min-max normalise** | Makes every photo the same size and stretches its brightness to 0-255 | Thresholds and kernel sizes are in pixels, so size must be fixed; normalising reduces camera exposure differences | width 900, `cv2.normalize` |
| **RGB → grayscale** | One brightness channel | Creases are dark valleys in brightness; colour only adds noise for edge detection | `cv2.cvtColor` |
| **Gaussian blur** | Averages each pixel with neighbours (bell-shaped weights) | Skin texture and sensor noise create fake edges; blurring removes pixel-scale grain but keeps crease-scale structure | 5×5, σ = 1.2 |
| **CLAHE** | Histogram equalisation done per small tile, with a cap on contrast boost | Faint creases need more contrast. Plain equalisation over the whole image would blow out bright areas and amplify noise; the clip limit stops that | clip 3.0, 8×8 tiles |
| **Hand segmentation (adaptive)** | Separates hand from background | Later steps must look only at the palm. Fixed colour ranges failed on deep skin tones, so the image picks its own threshold: Otsu on distance-from-background colour (Lab), Otsu on the Cr channel, 2-means on Cr/Cb, plus the old fixed range. Each candidate is scored on "does it look like a hand" (size, solidity, border contact); the best wins; GrabCut is the fallback | `segmentation.py` |
| **Morphology (open/close/fill holes)** | Open removes specks, close fills pinholes | Clean masks; kept small so neighbouring fingers are not welded together | 5×5 ellipse |
| **Black-hat transform** | Closing minus image: highlights thin dark lines on a lighter surface | Exactly what a crease is | 21×21 ellipse |
| **Sobel** | Gradient (slope) magnitude | Shows edge strength everywhere (thick, soft) | 3×3 |
| **Canny** | Thin 1-px edges using two thresholds with hysteresis | Cleaner edge map; thresholds are set from the palm's median brightness so it adapts to exposure | 0.66× and 1.33× median |
| **Global Otsu threshold** | One automatic cut-off for the whole image | Shown deliberately for comparison: it breaks when the lighting is uneven | Otsu |
| **Adaptive threshold** | A separate cut-off per 31×31 neighbourhood | Robust to shading across the palm | Gaussian, block 31, C = -6 |
| **Close + open on the threshold map** | Joins small gaps, deletes specks | Gives continuous crease strokes | 5×5 close, 2×2 open |
| **Skeletonisation (Zhang-Suen, scikit-image)** | Thins each stroke to a 1-px centre line | Lets us measure length, curvature and position of a crease | `skeletonize` |
| **Junction splitting** | Cuts the skeleton where branches meet | Heart, head and life lines touch; each becomes its own candidate | 5×5 dilation around junctions |
| **Distance transform** | Distance of each hand pixel to the background | The biggest inscribed circle gives palm radius; opening with a disc of 0.6 r removes the fingers so we can measure them | `distanceTransform` |
| **Palm frame** | Centre, "fingers up" direction u, "thumb side" direction t | Makes line scoring independent of rotation and of left/right (mirroring): positions are measured in the hand's own axes | thumb = lowest finger blob; u re-estimated from the four fingers only |
| **Line scoring** | For each skeleton piece × each line type, a 0-1 score from length, orientation, and where it sits in the palm frame | Heart: horizontal, upper palm. Head: horizontal, middle. Life: vertical, thumb side. Fate: vertical, centre. Greedy matching: best score first, one crease per line | `DETECT_T 0.55`, `UNCERTAIN_T 0.30` |
| **Confidence gates** | A line is "detected" only if the geometry fits **and** the crease is at least 7% darker than the palm's mean brightness (absolute depth) **and** at least 2× the palm's own texture level | A well-placed but faint ridge is as likely to be skin texture; it is reported "uncertain" | `MIN_REL_DEPTH`, `MIN_CONTRAST` |
| **Honest drawing** | Only "detected" lines are drawn. Uncertain and absent lines appear in a legend and table | The brief says mark uncertain/absent features clearly and never invent them | legend panel on the image |

## 3. Design decisions, in plain English

- **Validation measures the hand, not the whole photo.** A plain white wall has almost no texture, so whole-image blur and brightness checks called a perfectly good photo "blurry" and "overexposed". Now we segment first and judge sharpness/exposure on the hand.
- **Blur = width of the hand's silhouette edge** (step height ÷ peak gradient), not Laplacian variance. The Laplacian scales with contrast, so pale skin on a white wall looked blurry even when sharp. Edge width is contrast-independent: a sharp edge is 2-3 px at 800 px wide, defocus makes it wider. Limit: 5 px.
- **Dark skin is not "too dark".** The darkness limit is on the *hand's* mean brightness (35) and is wide, because deep skin in good light legitimately measures 50-90.
- **LLM approach = general LLM + RAG + strict prompt.** The brief allows fine-tuning, a domain model, or RAG. RAG is transparent (you can show which passages were used), needs no training data, and keeps palmistry claims inside a curated, hedged knowledge base.
- **The LLM never sees the photos.** It gets the structured features (status, confidence, curvature, prominence, region, palm shape). So every statement is traceable to a measurement, and "observation vs interpretation" is separated by design.
- **Disclaimer enforced in code** (report field and every chat answer), not by trusting the model to write it.
- **Chat grounding:** if a question names a line that was not detected on one or both hands, we inject a note into the prompt saying so and forbidding a description. This is a prompt-level guard, not a verifier.
- **Model choice:** `gemini-2.0-flash` is shut down. The app asks the API which models the key can use and takes the first of a preference list; `GEMINI_MODEL` overrides.
- **Streamlit caching:** the script reruns on every chat message, so validation and analysis are cached per file contents (`st.cache_data`).
- **Privacy:** images are in memory only; only the structured features go to the API; `.env`, `photos/` and `outputs/` are git-ignored.

## 4. Ten likely examiner questions

**1. Why CLAHE and not ordinary histogram equalisation?**
Ordinary equalisation stretches the histogram of the whole image, so a few bright areas dominate and noise in flat regions is amplified. CLAHE equalises 8×8 tiles separately and clips the histogram (clip 3.0) so no tile gets an extreme boost. Creases are local, low-contrast features, so local equalisation is right. The app shows the before/after histogram.

**2. Why a Gaussian blur before edge detection, and why not a bigger one?**
Edge detectors react to any intensity jump, including skin grain. A 5×5, σ 1.2 Gaussian removes that grain. Bigger blurs would also wash out the thin creases we want. It is a trade-off, tuned on synthetic hands; real photos may need adjusting.

**3. What is the difference between Sobel and Canny, and which do you use?**
Sobel gives gradient magnitude (a soft, thick edge-strength map). Canny adds non-maximum suppression and hysteresis thresholds to produce thin, connected 1-px edges. We display both for comparison. The line finder itself relies on the black-hat map + adaptive threshold, because creases are thin dark lines rather than step edges.

**4. Why adaptive thresholding rather than one Otsu threshold?**
Lighting varies across a palm (shading, a brighter thumb pad). One global threshold either misses creases in dark areas or floods bright areas. The adaptive version decides per 31×31 neighbourhood. The UI shows the global Otsu result next to it.

**5. How does segmentation cope with different skin tones?**
It does not use fixed colour ranges. It compares each pixel with the background colour (taken from the photo's border), picks the cut-off with Otsu, and cross-checks with Cr-channel Otsu and 2-means on Cr/Cb. Each candidate is scored for hand-likeness; GrabCut is the fallback. Tests include light, medium, dark and deep tones, white/grey/cream backgrounds, rotation and mirroring; on a deep tone the old fixed range scored IoU 0.0 and the new method 0.995 (synthetic). On real photos with cluttered or skin-coloured backgrounds it can fail, and then the validator rejects the photo.

**5b. (follow-up) So does it work on real hands?**
Be honest: the automated tests are synthetic. Real-photo behaviour is shown by the pairs I ran with `tools/run_photo_tests.py` (see the findings table); thresholds were tuned only against what those runs showed.

**6. How do you detect the heart, head, life and fate lines?**
Skeletonise the crease map inside the palm, split at junctions, express each piece in the palm's own coordinate frame (fingers-up and thumb-side axes), and score it against simple templates per line (orientation, length, position). Best score first, one piece per line. A line is "detected" only if the score is ≥ 0.55 *and* the crease is deep enough and stands out from the palm's texture; "uncertain" otherwise; "not detected" if nothing scores ≥ 0.30.

**7. How do you avoid claiming features that are not there?**
Three layers: (a) status labels from the vision stage with confidence gates; (b) only "detected" lines are drawn, uncertain and absent ones are listed in a legend; (c) the LLM gets the statuses, is told never to describe unlisted features, and chat questions about undetected lines get an extra grounding note. A test checks that a palm with no creases gets zero detections and that uncertain lines are never drawn.

**8. Why RAG instead of fine-tuning?**
The brief allows either. There is no labelled palmistry dataset and no ground truth to tune towards; RAG gives traceable, editable knowledge, and I can display exactly which passages informed the answer. Retrieval is a small TF-IDF cosine retriever over 20 curated passages, chosen by detected lines/hand type plus general themes for the report, and by the question text for chat.

**9. What are the safeguards in the LLM stage?**
System prompt rules (only listed features, observed vs traditional, hedged language, no predictions or advice, knowledge-only claims); structured JSON output; the model never gets images; disclaimer appended in code to the report and every chat answer; friendly errors for missing key / bad model / quota. Limitation: a prompt cannot guarantee obedience; there is no automatic verifier of the model's claims.

**10. What are the limitations, and what would you do next?**
Rule-based line detection (not a learned model) tuned mostly on synthetic hands; confidence is a heuristic, not a probability; palm shape/hand type from silhouette ratios is approximate; skin-coloured or cluttered backgrounds break segmentation; left/right is trusted from the upload slot; the chat guard is prompt-level. Next: collect consented labelled photos, evaluate against human-marked lines, try a trained segmentation/line model (e.g. MediaPipe hand landmarks for the palm frame), and add a verifier that checks answers against the feature JSON.

**Bonus Q: What is the SQUARE/LONG threshold based on?**
Palm length ÷ width < 1.15 counts as "square" (tolerance for segmentation error at the wrist end and camera tilt); longest finger ÷ palm length > 0.8 counts as "long" (roughly the middle of typical adult proportions). They are heuristics, labelled approximate, not validated on a dataset.

**Bonus Q: Why does the validator reject some dark photos but not dark skin?**
It checks the hand's mean grey level against a wide range (35-230) plus the share of blown-out pixels, so a deep skin tone in good light passes while a genuinely underexposed photo fails.
