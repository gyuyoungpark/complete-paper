"""Build dist/complete-paper.skill, the archive that the Claude app takes as an uploaded skill.

The archive holds the folder skills/complete-paper/ as complete-paper/, without caches. Attach it to a GitHub
release; the README's install section points there.

Usage: python tools/build_skill.py
"""
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "complete-paper")
OUT = os.path.join(ROOT, "dist", "complete-paper.skill")
SKIP_DIRS = {"__pycache__", ".pytest_cache", "results"}
SKIP_FILES = (".pyc", ".DS_Store")


def main():
    if not os.path.isfile(os.path.join(SKILL, "SKILL.md")):
        sys.exit("build_skill: skills/complete-paper/SKILL.md not found")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(SKILL):
            dn[:] = sorted(d for d in dn if d not in SKIP_DIRS)
            for f in sorted(fn):
                if f.endswith(SKIP_FILES):
                    continue
                p = os.path.join(dp, f)
                arc = os.path.join("complete-paper", os.path.relpath(p, SKILL)).replace(os.sep, "/")
                z.write(p, arc)
                n += 1
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {n} files, {os.path.getsize(OUT) // 1024} KiB")


if __name__ == "__main__":
    main()
