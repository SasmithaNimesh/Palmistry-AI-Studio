"""Create the submission zip and audit it.

    python tools/make_submission_zip.py [--out ../palm_reading_app_submission.zip]

Excluded on purpose: .env (secrets), photos/ (real palm photos; only photos/README.txt is kept),
outputs/ (derived from your photos), virtual envs, caches, other zips. The audit then lists every
image in the zip and scans every file for API-key patterns, and exits non-zero if it finds a
secret, an .env file, or a photo-like file outside docs/figures.
"""
import argparse
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".venv", "venv", "outputs", "__pycache__", ".pytest_cache", ".git"}
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff")
KEY_PATTERN = re.compile(rb"AIza[0-9A-Za-z_\-]{20,}|sk-[A-Za-z0-9]{20,}|AQ\.[A-Za-z0-9_\-]{30,}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT.parent / "palm_reading_app_submission.zip"))
    out = Path(ap.parse_args().out)
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                p = Path(dp) / f
                rel = p.relative_to(ROOT).as_posix()
                if f == ".env" or (f.startswith(".env.") and f != ".env.example") or f.endswith((".zip", ".pyc")):
                    continue
                if rel.startswith("photos/") and rel != "photos/README.txt":
                    continue
                z.write(p, f"palm_reading_app/{rel}")
                count += 1
    print(f"wrote {out} ({count} files, {out.stat().st_size // 1024} KB)")

    z = zipfile.ZipFile(out)
    names = z.namelist()
    images = [n for n in names if n.lower().endswith(IMAGE_EXT)]
    envs = [n for n in names if n.split("/")[-1].startswith(".env") and not n.endswith(".env.example")]
    leaks = [n for n in names if KEY_PATTERN.search(z.read(n))]
    stray = [n for n in images if "/docs/figures/" not in n]
    print("images in zip (should all be synthetic figures in docs/figures):")
    for n in images:
        print("  ", n)
    print("env files in zip:", envs or "none")
    print("API-key patterns found in:", leaks or "none")
    print("images outside docs/figures:", stray or "none")
    return 1 if (envs or leaks or stray) else 0


if __name__ == "__main__":
    sys.exit(main())
