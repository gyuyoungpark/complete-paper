#!/usr/bin/env python3
"""Find sentences of one text that repeat sentences of others.

Usage:
    python3 overlap_check.py conclusion.txt abstract.txt [introduction.txt ...]
    python3 overlap_check.py conclusion.txt abstract.txt --run 6 --similar 0.6

The first file is the text under test (for example the conclusion). Each of
its sentences is compared with every sentence of the other files. A sentence
is flagged when it shares a run of at least --run identical consecutive words
with another sentence, or when the two sentences share at least --similar of
their content words (Jaccard index, common function words ignored).

Plain text in, one paragraph or many. Strip LaTeX first if the markup is heavy.
Exit status is 1 if any sentence is flagged, otherwise 0.
"""
import argparse
import re
import sys

ABBREV = ["e.g.", "i.e.", "et al.", "vs.", "cf.", "approx.", "Fig.", "Eq.", "Ref.", "Sec."]
STOP = set("""a an the of in on at to for from by with without and or but as is are was were be been
that this these those it its their we our have has had not no than then which who whose when where
while whereas if so such can may might will would should into over under between within both each
also only more most less very here there""".split())


def sentences(text):
    text = " ".join(text.split())
    for a in ABBREV:
        text = text.replace(a, a.replace(".", "\x00"))
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"(\[])', text)
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


def words(s):
    return re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", s.lower())


def longest_run(a, b):
    """Length and text of the longest run of consecutive words common to a and b."""
    best, end = 0, 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, end = cur[j], i
        prev = cur
    return best, " ".join(a[end - best:end])


def jaccard(a, b):
    sa = {w for w in a if w not in STOP}
    sb = {w for w in b if w not in STOP}
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target")
    ap.add_argument("others", nargs="+")
    ap.add_argument("--run", type=int, default=6,
                    help="flag a shared run of at least this many words")
    ap.add_argument("--similar", type=float, default=0.6,
                    help="flag a content-word Jaccard index at or above this")
    args = ap.parse_args()

    target = sentences(open(args.target, encoding="utf-8").read())
    pool = []
    for f in args.others:
        for s in sentences(open(f, encoding="utf-8").read()):
            pool.append((f, s, words(s)))

    flagged = 0
    for n, s in enumerate(target, 1):
        w = words(s)
        best_run, run_text, run_src = 0, "", ""
        best_sim, sim_src = 0.0, ""
        for f, other, ow in pool:
            r, txt = longest_run(w, ow)
            if r > best_run:
                best_run, run_text, run_src = r, txt, f
            j = jaccard(w, ow)
            if j > best_sim:
                best_sim, sim_src = j, f
        hit = best_run >= args.run or best_sim >= args.similar
        flagged += hit
        mark = "REPEATS" if hit else "ok     "
        print(f"{n:>2}. {mark} longest shared run {best_run} words; "
              f"content overlap {best_sim:.2f}   {' '.join(s.split()[:6])} ...")
        if best_run >= args.run:
            print(f'      - shared with {run_src}: "{run_text}"')
        if best_sim >= args.similar:
            print(f"      - most content words in common with a sentence of {sim_src}")

    print(f"\nsentences: {len(target)}   flagged: {flagged}")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
