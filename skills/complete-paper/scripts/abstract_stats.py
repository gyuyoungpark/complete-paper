#!/usr/bin/env python3
"""Count what parts/abstract.md asks to be counted, so nobody estimates by eye.

Usage:
    python3 abstract_stats.py abstract.txt
    python3 abstract_stats.py abstract.txt --max-sentence 30 --cap-words 250
    python3 abstract_stats.py abstract.txt --cap-chars 600
    cat abstract.txt | python3 abstract_stats.py -

Reports sentences, words, characters (with spaces), words per sentence, and
two things for a human or agent to review: link words that suggest more than
two clauses, and reference words that point outside their own sentence.
The clause and reference flags are heuristics; the counts are exact.
"such as" and a "These results" that opens the last sentence are not listed.
Exit status is 1 if a hard limit (--max-sentence, --cap-words, --cap-chars)
is exceeded, otherwise 0.
"""
import argparse
import re
import sys

ABBREV = ["e.g.", "i.e.", "et al.", "vs.", "cf.", "approx.", "Fig.", "Eq.", "Ref."]
LINKS = ["which", "whose", "whereas", "while", "although", "though", "because",
         "since", "so", "when", "where", "unless", "if", "but"]
REFS = ["this", "these", "those", "it", "its", "they", "their", "them",
        "then", "such", "former", "latter", "respectively"]


def split_sentences(text):
    text = " ".join(text.split())
    for a in ABBREV:
        text = text.replace(a, a.replace(".", "\x00"))
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"(\[])', text)
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


def found(words, sentence):
    low = re.findall(r"[A-Za-z]+", sentence.lower())
    return [w for w in low if w in words]


def reference_words(sentence, last):
    """Reference words, minus two uses parts/abstract.md allows: "such as"
    introducing examples, and "These results" opening the last sentence."""
    text = re.sub(r"\bsuch\s+as\b", " ", sentence, flags=re.I)
    if last:
        text = re.sub(r"^\W*These results\b", " ", text)
    return found(REFS, text)


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", help="text file with the abstract, or - for stdin")
    ap.add_argument("--max-sentence", type=int, default=30,
                    help="largest allowed number of words in one sentence")
    ap.add_argument("--cap-words", type=int, default=None)
    ap.add_argument("--cap-chars", type=int, default=None,
                    help="character cap, spaces included")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    text = " ".join(raw.split())
    sents = split_sentences(text)
    counts = [len(s.split()) for s in sents]
    total_words = sum(counts)
    fail = False

    print(f"sentences: {len(sents)}   words: {total_words}   "
          f"characters with spaces: {len(text)}   "
          f"mean words per sentence: {total_words / max(len(sents), 1):.1f}")
    print()
    for i, (s, n) in enumerate(zip(sents, counts), 1):
        links = found(LINKS, s)
        refs = reference_words(s, i == len(sents))
        notes = []
        if n > args.max_sentence:
            notes.append(f"OVER {args.max_sentence} WORDS")
            fail = True
        if len(links) >= 2:
            notes.append("check clauses: " + ", ".join(links))
        if refs:
            notes.append("check references: " + ", ".join(refs))
        head = " ".join(s.split()[:6])
        print(f"{i:>2}. {n:>3} words  {head} ...")
        for note in notes:
            print(f"      - {note}")

    if args.cap_words is not None and total_words > args.cap_words:
        print(f"\nOVER WORD CAP: {total_words} > {args.cap_words}")
        fail = True
    if args.cap_chars is not None and len(text) > args.cap_chars:
        print(f"\nOVER CHARACTER CAP: {len(text)} > {args.cap_chars}")
        fail = True
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
