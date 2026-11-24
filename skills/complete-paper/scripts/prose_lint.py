#!/usr/bin/env python3
"""Sentence-level lint for a manuscript, and a guard for edits.

Usage:
    python3 prose_lint.py main.tex [more.tex ...]          LaTeX source (\\input is followed)
    python3 prose_lint.py section.txt                      plain text or Markdown
    python3 prose_lint.py main.tex --only hype filler      some categories only
    python3 prose_lint.py main.tex --max-words 40 --show 12
    python3 prose_lint.py --compare before.tex after.tex   what an edit changed that it must not change

Lint. Prints the length of sentences and paragraphs per section, and lists by category:
  long        sentences over --max-words (default 40); the share over 30 words is reported
  stacked     two hedges in one clause ("may possibly", "could potentially suggest")
  hype        words of praise and promise ("novel", "unprecedented", "paves the way")
  inflated    vocabulary that became markedly more frequent in papers once language models were
              used for writing ("delve", "pivotal", "underscore", "showcase", "intricate")
  filler      openers and phrases that carry nothing ("it is worth noting that", "plays a crucial
              role", "has attracted considerable attention", "in order to")
  intensifier "very", "clearly", "highly", "significantly" where no test is meant
  tail        a clause hung on with a comma and an -ing word (", highlighting the ...")
  signpost    sentences about the text ("as mentioned above", "we now turn to")
  closer      a paragraph that ends by summing itself up ("Overall, ...", "Taken together, ...")
  vague       "studies have shown", "it has been reported" in a sentence without a citation
  hidden-verb "perform an analysis of" for "analyse"
  opener      sentences that begin "There is", "It is ... that", or "This" + verb; three sentences
              in a row that begin with "We"; a sentence that begins with a symbol or a numeral
  usage       errors common in writing by non-native speakers ("researches", "discuss about")
  form        contractions, a doubled word, mixed British and American spelling
  abbrev      an abbreviation defined twice, used before its definition, or defined and then used
              fewer than three times
A hit is a place to look at, not an error: the lists cannot tell "novel" in "a novel by" from
praise. Mathematics, citations and references are masked before the text is read.

Compare. Reports every number, citation key, reference label and formula that is in one file and
not in the other, and the change in the count of hedges. An edit for style must change none of
them. Exit status is 1 if any did.

Standard library only. Exit status of the lint is 0, or 1 with --strict when a warning is found.
"""
import argparse
import bisect
import os
import re
import statistics
import sys
from collections import Counter, OrderedDict, defaultdict

W = r"[A-Za-z][A-Za-z'\-]*"
HEDGE = r"may|might|could|possibly|perhaps|presumably|potentially|likely|apparently|appears?\s+to|seems?\s+to|suggests?|suggesting|tentatively"
LISTS = OrderedDict([
    ("hype", ("W", r"\b(novel(?!\s+by)|unprecedented|remarkabl[ey]|striking(?:ly)?|dramatic(?:ally)?|tremendous(?:ly)?|extraordinar(?:y|ily)|"
                   r"exceptional(?:ly)?|outstanding|excellent|superior|breakthrough|revolutionar\w+|game-chang\w+|groundbreaking|cutting-edge|"
                   r"state-of-the-art|for\s+the\s+first\s+time|pav(?:e|es|ed|ing)\s+the\s+way|open(?:s|ed|ing)?\s+(?:up\s+)?(?:a\s+)?new\s+"
                   r"(?:avenue|door|possibilit|route|path|opportunit|horizon)\w*|holds?\s+(?:great\s+)?promise|highly\s+promising)\b")),
    ("inflated", ("N", r"\b(delv(?:e|es|ed|ing)|intricate(?:ly)?|intricacies|pivotal|paramount|meticulous(?:ly)?|underscor(?:e|es|ed|ing)|"
                       r"showcas(?:e|es|ed|ing)|leverag(?:e|es|ed|ing)|harness(?:es|ed|ing)?|unveil(?:s|ed|ing)?|unravel(?:s|ed|ing)?|"
                       r"shed(?:s|ding)?\s+(?:new\s+)?light\s+on|tapestry|testament|multifaceted|nuanced|holistic(?:ally)?|seamless(?:ly)?|"
                       r"foster(?:s|ed|ing)?|bolster(?:s|ed|ing)?|garner(?:s|ed|ing)?|realm|landscape\s+of|invaluable|commendable|"
                       r"profound(?:ly)?|vibrant|comprehensive(?:ly)?|crucial(?:ly)?|noteworthy|encompass(?:es|ed|ing)?|elucidat(?:e|es|ed|ing))\b")),
    ("filler", ("N", r"\b(it\s+is\s+(?:worth\s+)?(?:noting|mentioning|pointing\s+out|emphasi[sz]ing)\s+that|it\s+(?:should|must)\s+be\s+(?:noted|mentioned|"
                     r"emphasi[sz]ed|pointed\s+out)\s+that|it\s+is\s+(?:important|interesting|worthwhile)\s+to\s+(?:note|mention|point\s+out)(?:\s+that)?|"
                     r"it\s+is\s+well[\s-]known\s+that|needless\s+to\s+say|as\s+a\s+matter\s+of\s+fact|in\s+order\s+to|due\s+to\s+the\s+fact\s+that|"
                     r"in\s+the\s+context\s+of|plays?\s+an?\s+(?:important|crucial|key|vital|pivotal|significant|essential|central)\s+role|"
                     r"a\s+(?:wide|broad|large)\s+(?:range|variety)\s+of|in\s+recent\s+years|(?:has|have)\s+(?:attracted|received|drawn|gained)\s+"
                     r"(?:considerable|great|much|significant|tremendous|extensive|increasing|growing|a\s+lot\s+of|enormous)\s+(?:attention|interest)|"
                     r"with\s+the\s+(?:rapid\s+)?development\s+of|last\s+but\s+not\s+least|it\s+goes\s+without\s+saying)\b")),
    ("intensifier", ("N", r"\b(very|extremely|highly|quite|really|clearly|obviously|evidently|significantly|substantially|strongly|greatly|"
                          r"considerably|drastically|essentially|basically|actually|indeed|in\s+fact|of\s+course|undoubtedly|certainly)\b")),
    ("tail", ("N", r",\s+(?:thus\s+|thereby\s+)?(highlighting|underscoring|emphasi[sz]ing|demonstrating|showcasing|illustrating|indicating|"
                   r"suggesting|revealing|reflecting|confirming|paving|offering|providing|enabling|ensuring|making\s+it|opening)\b")),
    ("signpost", ("N", r"\b(we\s+now\s+turn\s+to|let\s+us\s+(?:now\s+)?\w+|as\s+(?:mentioned|discussed|noted|stated|described|explained)\s+"
                       r"(?:above|earlier|before|previously|below)|in\s+what\s+follows|the\s+rest\s+of\s+(?:this|the)\s+(?:paper|article|letter)\s+is\s+"
                       r"organi[sz]ed|in\s+this\s+(?:section|subsection),?\s+we|it\s+can\s+be\s+seen\s+that|as\s+can\s+be\s+seen|as\s+we\s+will\s+see)\b")),
    ("hidden-verb", ("N", r"\b((?:perform|conduct|undertak|execut)\w*|carr(?:y|ies|ied|ying)\s+out|ma(?:ke|kes|de|king))\s+(?:an?\s+|the\s+)?(?:\w+\s+)?"
                          r"(measurement|analysis|investigation|comparison|calculation|examination|characteri[sz]ation|optimi[sz]ation|evaluation|"
                          r"estimation|observation)s?\s+(?:of|on|between)\b")),
    ("usage", ("W", r"\b(researches|informations|evidences|equipments|softwares|literatures|knowledges|can\s+be\s+able\s+to|discuss(?:es|ed)?\s+about|"
                    r"emphasi[sz]e[sd]?\s+on|compris(?:e|es|ed)\s+of|is\s+consisted\s+of|as\s+following|in\s+the\s+other\s+hand|more\s+and\s+more|"
                    r"nowadays|a\s+lot\s+of|and\s+so\s+on|the\s+both|different\s+with|same\s+with|superior\s+than|according\s+to\s+(?:Fig|Eq|Table)|"
                    r"composed\s+by|in\s+case\s+of|researches?\s+on\s+it)\b")),
])
STACKED = re.compile(rf"\b(?:{HEDGE})\b(?:\s+\w+){{0,4}}?\s+(?:{HEDGE})\b", re.I)
VAGUE = re.compile(r"\b((?:many|several|some|numerous|previous|recent|earlier|prior)\s+(?:studies|works|reports|researchers|authors|groups|papers)|"
                   r"studies\s+have\s+(?:shown|reported|demonstrated|suggested|found)|it\s+(?:has|was)\s+been\s+(?:shown|reported|demonstrated|suggested|"
                   r"found|proposed|argued)|it\s+is\s+(?:widely|generally|commonly)\s+(?:believed|accepted|known|assumed)|the\s+literature\s+"
                   r"(?:shows|suggests|reports))\b", re.I)
CLOSER = re.compile(r"^(?:overall|in\s+summary|in\s+conclusion|to\s+summari[sz]e|to\s+conclude|taken\s+together|collectively|all\s+in\s+all|in\s+short|"
                    r"altogether|in\s+essence)\b,?", re.I)
EXPLETIVE = re.compile(r"^(?:there\s+(?:is|are|was|were|exists?)\b|it\s+(?:is|was)\s+(?:\w+\s+){0,3}?that\b|this\s+(?:is|was|shows?|indicates?|suggests?|"
                       r"means?|implies|demonstrates?|leads?|results?|allows?|makes?|provides?|can|may|will)\b)", re.I)
CONTRACTION = re.compile(r"\b(?:don't|doesn't|didn't|can't|couldn't|won't|wouldn't|isn't|aren't|wasn't|weren't|it's|that's|there's|we've|we're|"
                         r"we'll|let's|haven't|hasn't|shouldn't)\b", re.I)
DOUBLED = re.compile(r"\b([A-Za-z]{2,})\s+\1\b", re.I)
SPELLING = [("colour", "color"), ("behaviour", "behavior"), ("centre", "center"), ("modelling", "modeling"), ("analyse", "analyze"),
            ("fibre", "fiber"), ("neighbour", "neighbor"), ("labelled", "labeled"), ("characterise", "characterize"),
            ("optimise", "optimize"), ("magnetisation", "magnetization"), ("polarisation", "polarization"), ("realise", "realize")]
ABBREV_DOT = re.compile(r"\b(Figs?|Eqs?|Secs?|Refs?|Tabs?|Suppl?|Nos?|vs|cf|ca|al|e\.g|i\.e|etc|approx|resp|Dr|Prof)\.")
ENV_DROP = ("equation", "align", "gather", "multline", "eqnarray", "flalign", "alignat", "tabular", "tabular\\*", "tabularx", "longtable",
            "thebibliography", "verbatim", "lstlisting", "minted", "tikzpicture", "displaymath", "math", "split")
SECTION_SKIP = re.compile(r"acknowledg|reference|author\s+contrib|data\s+availab|code\s+availab|competing|conflict|funding", re.I)


def read_tex(path, depth=0):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        sys.exit(f"prose_lint: cannot read {path}: {exc.strerror}")
    folder, out = os.path.dirname(os.path.abspath(path)), []
    for n, line in enumerate(raw.split("\n"), 1):
        if path.endswith((".tex", ".ltx")):
            line = re.sub(r"(?<!\\)%.*", "", line)
            m = re.search(r"\\(?:input|include|subfile)\s*\{([^}]+)\}", line)
            if m and depth < 5:
                hit = next((os.path.join(folder, c) for c in (m.group(1).strip(), m.group(1).strip() + ".tex")
                            if os.path.isfile(os.path.join(folder, c))), None)
                if hit:
                    out.extend(read_tex(hit, depth + 1))
                    continue
        out.append((os.path.basename(path), n, line))
    return out


def keep_lines(match, token=" "):
    """Replacement that keeps the line breaks of what it replaces, so that line numbers stay valid."""
    return token + "\n" * match.group(0).count("\n")


def detex(text):
    """LaTeX source as readable text: mathematics, citations and references masked; line breaks kept."""
    a = text.find("\\begin{document}")
    if a >= 0:
        text = "\n" * text[:a].count("\n") + text[a + len("\\begin{document}"):]
    text = re.sub(r"\\end\{document\}.*", "", text, flags=re.S)
    for env in ENV_DROP:
        text = re.sub(r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (env, env), lambda m: keep_lines(m, " MATH " if env not in
                      ("tabular", "tabular\\*", "tabularx", "longtable", "thebibliography", "verbatim", "lstlisting", "minted", "tikzpicture") else " "),
                      text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]", lambda m: keep_lines(m, " MATH "), text, flags=re.S)
    text = re.sub(r"(?<!\\)\$[^$]*\$", lambda m: keep_lines(m, "MATH"), text)
    text = re.sub(r"\\(?:cite|citep|citet|citealp|onlinecite|parencite|textcite|footcite|autocite|supercite)\w*\*?\s*(?:\[[^\]]*\]\s*)*\{[^{}]*\}", " CITE", text)
    text = re.sub(r"\(?\\(?:eqref|ref|cref|Cref|autoref|pageref)\*?\s*\{[^{}]*\}\)?", "REF", text)
    text = re.sub(r"\\(?:label|includegraphics|bibliography|bibliographystyle|vspace|hspace|input|include|externaldocument|pagestyle|"
                  r"setcounter|addtocounter|renewcommand|newcommand|usepackage)\*?\s*(?:\[[^\]]*\]\s*)*(?:\{[^{}]*\}\s*)+", " ", text)
    # Headings become marks that keep the line count, so that where() reports the right line after them.
    text = re.sub(r"\\(?:sub)*(?:section|paragraph)\*?\s*(?:\[[^\]]*\])?\s*\{([^{}]*)\}",
                  lambda m: f"@@HEAD {' '.join(m.group(1).split())}@@" + "\n" * m.group(0).count("\n"), text)
    text = re.sub(r"\\begin\{abstract\}", "@@HEAD Abstract@@", text)
    text = re.sub(r"\\end\{abstract\}", "@@HEAD (main text)@@", text)   # a letter without sections continues here
    text = re.sub(r"\\(?:begin|end)\{[^{}]*\}(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"\\(?:title|author|affiliation|address|email|date|thanks|maketitle|centering|noindent|item|caption)\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("---", " \u2014 ").replace("--", "\u2013").replace("~", " ").replace("\\%", "%").replace("\\&", "&")
    text = re.sub(r"\\(?:,|;|:|!| |quad|qquad)", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", "", text)
    text = re.sub(r"[{}]", "", text)
    return text.replace("``", "\"").replace("''", "\"")


def sentences(par):
    masked = ABBREV_DOT.sub(lambda m: m.group(0)[:-1] + "\x00", par)
    masked = re.sub(r"(?<=\d)\.(?=\d)", "\x00", masked)
    cuts = [m.end() for m in re.finditer(r"[.!?][)\]'\"]*(?=\s+[A-Z(\[\"])", masked)]
    out, start = [], 0
    for c in cuts + [len(par)]:
        if par[start:c].strip():
            out.append((start, c))
        start = c
    return out


def words(s):
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", s)


def lint(lines, is_tex, opts):
    raw = "\n".join(t for _, _, t in lines)
    if is_tex:
        text = detex(raw)
    else:                                                # plain text or Markdown: headings kept, code left out
        text = re.sub(r"```.*?```", lambda m: keep_lines(m), raw, flags=re.S)
        text = re.sub(r"`[^`\n]*`", "CODE", text)
        text = re.sub(r"^#+\s*(.+)$", r"@@HEAD \1@@", text, flags=re.M)
    offsets, pos = [], 0
    for t in text.split("\n"):
        offsets.append(pos)
        pos += len(t) + 1

    def where(p):
        k = min(max(bisect.bisect_right(offsets, p) - 1, 0), len(lines) - 1)
        return f"{lines[k][0]}:{lines[k][1]}"

    hits, stats, section = defaultdict(list), OrderedDict(), "(front)"
    skip = is_tex and "@@HEAD" in text                    # title block and affiliations come before the first heading
    all_sent, abbr_def, abbr_use = [], OrderedDict(), defaultdict(list)

    def blocks():
        """(offset, text) of each paragraph, with every heading mark as a block of its own."""
        for m in re.finditer(r"(?:[^\n]*\S[^\n]*\n?)+", text):
            par, p0, last = m.group(0), m.start(), 0
            for h in re.finditer(r"@@HEAD .*?@@", par, re.S):
                if par[last:h.start()].strip():
                    yield p0 + last, par[last:h.start()]
                yield p0 + h.start(), h.group(0)
                last = h.end()
            if par[last:].strip():
                yield p0 + last, par[last:]

    for p0, par in blocks():
        head = re.match(r"\s*@@HEAD (.*?)@@\s*$", par, re.S)
        if head:
            section = re.sub(r"\s+", " ", head.group(1)) or section
            skip = bool(SECTION_SKIP.search(section))
            continue
        par = re.sub(r"@@HEAD .*?@@", " ", par)
        if skip or len(words(par)) < 6:
            continue
        spans = sentences(par)
        st = stats.setdefault(section, {"sent": [], "pars": []})
        st["pars"].append(len(spans))
        run_we = 0
        for k, (s, e) in enumerate(spans):
            sent = re.sub(r"\s+", " ", par[s:e]).strip()
            n = len([w for w in words(sent) if w not in ("MATH", "CITE", "REF")])
            if n < 3:
                continue
            at = where(p0 + s + (len(par[s:e]) - len(par[s:e].lstrip())))
            st["sent"].append(n)
            all_sent.append(n)
            if n > opts.max_words:
                hits["long"].append((at, f"{n} words: {sent[:90]}..."))
            for name, (_, pattern) in LISTS.items():
                for h in re.finditer(pattern, sent, re.I):
                    hits[name].append((at, f"\"{h.group(0).strip(', ')}\" in: {sent[max(0, h.start() - 40):h.end() + 40].strip()}"))
            for h in STACKED.finditer(sent):
                hits["stacked"].append((at, f"\"{h.group(0)}\" in: {sent[max(0, h.start() - 30):h.end() + 30].strip()}"))
            v = VAGUE.search(sent)
            if v and "CITE" not in sent:
                hits["vague"].append((at, f"\"{v.group(0)}\" without a citation: {sent[:90]}"))
            if k == len(spans) - 1 and len(spans) >= 3 and CLOSER.match(sent) and not re.search(r"conclu|summary|discussion|abstract", section, re.I):
                hits["closer"].append((at, sent[:100]))
            x = EXPLETIVE.match(sent)
            if x:
                hits["opener"].append((at, f"begins \"{x.group(0)}\": {sent[:80]}"))
            if re.match(r"(?:MATH|\d)", sent):
                hits["opener"].append((at, f"begins with a symbol or a numeral: {sent[:60]}"))
            run_we = run_we + 1 if re.match(r"We\b", sent) else 0
            if run_we == 3:
                hits["opener"].append((at, "three sentences in a row begin with \"We\""))
            for h in CONTRACTION.finditer(sent):
                hits["form"].append((at, f"contraction \"{h.group(0)}\""))
            for h in DOUBLED.finditer(sent):
                if h.group(1).lower() not in ("that", "had", "is") and h.group(1) not in ("MATH", "CITE", "REF", "CODE"):
                    hits["form"].append((at, f"doubled word \"{h.group(0)}\""))
            for h in re.finditer(r"((?:[A-Za-z][A-Za-z\-]+\s+){1,6})\(([A-Z][A-Za-z]{1,6}s?)\)", sent):
                short = h.group(2).rstrip("s")
                initials = "".join(w[0] for w in re.split(r"[\s\-]+", h.group(1).strip()) if w).upper()
                if len(short) >= 2 and short.isupper() and short in initials + "".join(c for c in h.group(1) if c.isupper()):
                    abbr_def.setdefault(short, []).append((at, bool(re.match(r"abstract$", section, re.I))))
            for h in re.finditer(r"(?<![A-Za-z(])([A-Z]{2,6})s?(?![A-Za-z])", sent):
                if h.group(1) not in ("MATH", "CITE", "REF"):
                    abbr_use[h.group(1)].append(at)
    # ----- abbreviations
    # The abstract and the main text each define an abbreviation once (ground rule 5 of SKILL.md), so a definition
    # in the abstract does not count against the one in the text.
    for short, defs in abbr_def.items():
        places = [at for at, _ in defs]
        for scope in (True, False):
            mine = [at for at, in_abstract in defs if in_abstract == scope]
            if len(mine) > 1:
                where_ = "in the abstract" if scope else "in the text"
                hits["abbrev"].append((mine[1], f"{short} is defined {len(mine)} times {where_} ({', '.join(mine[:3])}): "
                                                f"define it once {where_}"))
        uses = abbr_use.get(short, [])
        if len(uses) < 3:
            hits["abbrev"].append((places[0], f"{short} is defined and then used {len(uses)} time(s): write it out"))
    # ----- spelling variety
    low = text.lower()
    british = [b for b, a in SPELLING if re.search(rf"\b{b}", low)]
    american = [a for b, a in SPELLING if re.search(rf"\b{a}", low)]
    if british and american:
        hits["form"].append(("text", f"British and American spelling are mixed: {', '.join(british[:4])} / {', '.join(american[:4])}"))
    dashes = text.count("\u2014")
    return hits, stats, all_sent, dashes


LEVEL = {"long": "W", "stacked": "W", "hype": "W", "usage": "W", "form": "W", "vague": "W", "abbrev": "N", "inflated": "N", "filler": "N",
         "intensifier": "N", "tail": "N", "signpost": "N", "closer": "N", "hidden-verb": "N", "opener": "N"}
ADVICE = {"long": "split it, or cut a clause", "stacked": "one hedge per inference", "hype": "state the number and let the reader judge",
          "inflated": "use the plain word, or cut the sentence if nothing is left", "filler": "delete the phrase; the sentence stands without it",
          "intensifier": "delete, or replace with the number", "tail": "make it a sentence of its own that says what follows, or cut it",
          "signpost": "say the thing itself", "closer": "end on the finding, not on a summary of the paragraph",
          "vague": "cite the work, or say who", "hidden-verb": "use the verb", "opener": "start with the subject that acts",
          "usage": "correct the usage", "form": "fix the form", "abbrev": "see the rule for abbreviations"}


def numbers_of(text):
    text = re.sub(r"\\(?:cite\w*|ref|eqref|cref|Cref|label|autoref|includegraphics)\*?\s*(?:\[[^\]]*\])*\{[^{}]*\}", " ", text)
    return Counter(re.findall(r"(?<![A-Za-z_\d.])\d+(?:\.\d+)?(?![\d]*[A-Za-z_])", text))


def compare(old, new):
    out = []
    strip = lambda t: re.sub(r"(?<!\\)%.*", "", t)
    old, new = strip(old), strip(new)

    def diff(name, a, b):
        gone, came = a - b, b - a
        if gone or came:
            out.append((name, sorted(gone.elements()), sorted(came.elements())))

    keys = lambda t: Counter(k.strip() for m in re.finditer(r"\\(?:cite|citep|citet|citealp|onlinecite|parencite|textcite)\w*\*?\s*(?:\[[^\]]*\]\s*)*\{([^{}]*)\}", t)
                             for k in m.group(1).split(","))
    refs = lambda t: Counter(k.strip() for m in re.finditer(r"\\(?:eqref|ref|cref|Cref|autoref)\*?\s*\{([^{}]*)\}", t) for k in m.group(1).split(","))
    math = lambda t: Counter(re.sub(r"\s+", "", m.group(0)) for m in re.finditer(
        r"(?<!\\)\$[^$]+\$|\\\[.*?\\\]|\\begin\{(equation|align|gather|multline|eqnarray)\*?\}.*?\\end\{\1\*?\}", t, re.S))
    diff("numbers", numbers_of(re.sub(r"(?<!\\)\$[^$]+\$", " ", old)), numbers_of(re.sub(r"(?<!\\)\$[^$]+\$", " ", new)))
    diff("citation keys", keys(old), keys(new))
    diff("reference labels", refs(old), refs(new))
    diff("formulas", math(old), math(new))
    hedge = lambda t: len(re.findall(rf"\b(?:{HEDGE})\b", t, re.I))
    return out, hedge(old), hedge(new)


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Sentence-level lint and edit guard.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    ap.add_argument("--only", nargs="+", metavar="CATEGORY", help="list only these categories")
    ap.add_argument("--max-words", type=int, default=40, dest="max_words", help="longest sentence allowed (default 40)")
    ap.add_argument("--show", type=int, default=6, help="hits listed per category (default 6; 0 lists all)")
    ap.add_argument("--strict", action="store_true", help="exit with status 1 when a warning is found")
    opts = ap.parse_args()
    if opts.compare:
        try:
            old, new = (open(p, encoding="utf-8", errors="replace").read() for p in opts.compare)
        except OSError as exc:
            sys.exit(f"prose_lint: cannot read {exc.filename}: {exc.strerror}")
        changes, h_old, h_new = compare(old, new)
        print(f"prose_lint --compare: {opts.compare[0]} -> {opts.compare[1]}")
        for name, gone, came in changes:
            print(f"\nCHANGED {name}")
            if gone:
                print("  only before: " + ", ".join(gone[:20]) + (" ..." if len(gone) > 20 else ""))
            if came:
                print("  only after:  " + ", ".join(came[:20]) + (" ..." if len(came) > 20 else ""))
        print(f"\nhedges: {h_old} before, {h_new} after" + (": fewer hedges; check that no claim became stronger" if h_new < h_old else ""))
        print("\n" + ("the edit changed protected content: restore it, or have the author confirm each change" if changes
                      else "numbers, citations, references and formulas are unchanged"))
        sys.exit(1 if changes else 0)
    if not opts.files:
        ap.error("give the files to read, or --compare BEFORE AFTER")
    lines = [line for p in opts.files for line in read_tex(p)]
    is_tex = any(p.endswith((".tex", ".ltx")) for p in opts.files)
    hits, stats, all_sent, dashes = lint(lines, is_tex, opts)
    total = sum(all_sent)
    print("prose_lint: " + ", ".join(opts.files))
    if not all_sent:
        print("\nno running text found")
        sys.exit(0)
    print(f"\nSENTENCES  {len(all_sent)} sentences, {total} words; mean {statistics.mean(all_sent):.1f}, median {statistics.median(all_sent):.0f}, "
          f"longest {max(all_sent)}; over 30 words: {100 * sum(1 for n in all_sent if n > 30) / len(all_sent):.0f}%; "
          f"spread (s.d./mean) {statistics.pstdev(all_sent) / statistics.mean(all_sent):.2f}")
    print("  section                          sentences   mean   longest   paragraphs   sentences per paragraph")
    for name, st in stats.items():
        if st["sent"]:
            print(f"  {name[:32]:<32} {len(st['sent']):>9}   {statistics.mean(st['sent']):>4.1f}   {max(st['sent']):>7}   {len(st['pars']):>10}   "
                  f"{statistics.mean(st['pars']):>4.1f}")
    if total and dashes * 1000 / total > 3:
        print(f"  em dashes: {dashes} ({dashes * 1000 / total:.1f} per 1000 words)")
    print("\nCATEGORY      HITS   PER 1000 WORDS")
    wanted = [c for c in LEVEL if (not opts.only or c in opts.only)]
    for c in wanted:
        if hits.get(c):
            print(f"  {c:<12} {len(hits[c]):>4}   {len(hits[c]) * 1000 / total:>6.1f}")
    warnings = 0
    for c in wanted:
        if not hits.get(c):
            continue
        warnings += len(hits[c]) if LEVEL[c] == "W" else 0
        print(f"\n{c.upper()} ({len(hits[c])}; {'warning' if LEVEL[c] == 'W' else 'note'}): {ADVICE[c]}")
        shown = hits[c] if opts.show == 0 else hits[c][:opts.show]
        for at, msg in shown:
            print(f"  {at}: {msg}")
        if len(shown) < len(hits[c]):
            print(f"  ... and {len(hits[c]) - len(shown)} more (--show 0 lists all)")
    print(f"\n{warnings} warning(s), {sum(len(v) for c, v in hits.items() if LEVEL[c] == 'N' and c in wanted)} note(s)")
    sys.exit(1 if (opts.strict and warnings) else 0)


if __name__ == "__main__":
    main()
