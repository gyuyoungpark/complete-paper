#!/usr/bin/env python3
"""List every caption in LaTeX sources with its word count and review flags.

Usage:
    python3 caption_check.py main.tex [supplement.tex ...]
    python3 caption_check.py main.tex --max-words 150

For each \\caption{...} it reports the number of words and flags:
  - words from the watch-list of parts/captions.md (trend, outcome,
    interpretation, evaluation), for a human or agent to review;
  - filler openers such as "This figure shows";
  - colour words not accompanied by a line style or marker word;
  - captions over --max-words.

The word list is a heuristic: "increases" in "as the field increases" may be a
plain description of a sweep. Review each flag; do not delete blindly.
Exit status is 1 if a caption exceeds --max-words, otherwise 0.
"""
import argparse
import re
import sys

WATCH = {
    "trend": ["increase", "increases", "increasing", "decrease", "decreases",
              "decreasing", "saturates", "saturate", "scales", "grows", "drops",
              "rises", "falls", "enhanced", "reduced", "suppressed"],
    "outcome": ["agrees", "agreement", "larger", "smaller", "higher", "lower",
                "better", "worse", "outperforms", "exceeds", "matches"],
    "interpretation": ["indicating", "indicates", "suggesting", "suggests",
                       "demonstrating", "demonstrates", "confirming", "confirms",
                       "implying", "implies", "reveals", "revealing", "because",
                       "due", "owing", "originates", "attributed"],
    "evaluation": ["clearly", "remarkably", "excellent", "good", "well",
                   "expected", "strikingly", "obviously", "significantly",
                   "dramatically", "nicely"],
}
OPENERS = [r"^this figure", r"^the figure", r"^figure shows", r"^plot of",
           r"^plots of", r"^graph of", r"^here we show"]
COLOURS = ["red", "blue", "green", "black", "orange", "purple", "yellow",
           "gray", "grey", "cyan", "magenta", "brown", "pink"]
STYLES = ["solid", "dashed", "dotted", "dash-dotted", "circles", "squares",
          "triangles", "diamonds", "crosses", "stars", "dots", "open",
          "filled", "thick", "thin", "hatched"]


def strip_comments(text):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.split("\n"))


def captions(text):
    """Yield (position, caption text) for each \\caption with balanced braces."""
    for m in re.finditer(r"\\caption\*?\s*(\[[^\]]*\])?\s*\{", text):
        i = m.end()
        depth = 1
        while i < len(text) and depth:
            c = text[i]
            if c == "\\":
                i += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        yield m.start(), text[m.end():i - 1]


def plain(tex):
    t = re.sub(r"\\label\s*\{[^}]*\}", " ", tex)
    t = re.sub(r"\$[^$]*\$", " X ", t)                      # inline math -> one token
    t = re.sub(r"\\(?:eq)?ref\s*\{[^}]*\}", " N ", t)
    t = re.sub(r"\\cite[a-z]*\s*\{[^}]*\}", " ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", " ", t)
    t = re.sub(r"[{}~]", " ", t)
    return " ".join(t.split())


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--max-words", type=int, default=None)
    args = ap.parse_args()
    over = False
    total = 0

    for f in args.files:
        text = strip_comments(open(f, encoding="utf-8", errors="replace").read())
        for pos, raw in captions(text):
            total += 1
            line = text.count("\n", 0, pos) + 1
            cap = plain(raw)
            words = cap.split()
            low = [re.sub(r"[^a-z\-]", "", w.lower()) for w in words]
            print(f"{f}:{line}  {len(words)} words  {' '.join(words[:8])} ...")
            for kind, vocab in WATCH.items():
                hits = sorted({w for w in low if w in vocab})
                if hits:
                    print(f"      - {kind}: {', '.join(hits)}")
            if any(re.search(p, cap.lower()) for p in OPENERS):
                print("      - filler opener")
            if any(w in COLOURS for w in low) and not any(w in STYLES for w in low):
                print("      - colour named without a line style or marker")
            if args.max_words is not None and len(words) > args.max_words:
                print(f"      - OVER {args.max_words} WORDS")
                over = True

    print(f"\ncaptions: {total}")
    sys.exit(1 if over else 0)


if __name__ == "__main__":
    main()
