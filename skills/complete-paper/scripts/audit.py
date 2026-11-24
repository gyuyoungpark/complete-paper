#!/usr/bin/env python3
"""Run every check of the skill on a finished manuscript, add the cross-checks, and write one report.

Usage:
    python3 audit.py main.tex
    python3 audit.py main.tex --supp supplement.tex --bib refs.bib --brief brief.md --repro repro.md
    python3 audit.py main.tex --figures make_fig1.py make_fig2.py --style figstyle.md --width-mm 86 178
    python3 audit.py main.tex --require data competing contributions ai
    python3 audit.py main.tex --abstract-chars 600 --words 3750 --display-max 4 --refs-max 50 --title-chars 100
    python3 audit.py main.tex --report audit.md

Part checks (each is the script of one part, run on the final files):
  equations      eq_refs.py        unresolved references, duplicate labels, numbers typed by hand
  citations      cite_order.py     every figure, table and panel cited, and in order
  captions       caption_check.py  length and review flags of every caption
  tables         table_check.py    form of every table
  supplement     supp_check.py     callouts, reach, size, style (with --supp)
  references     ref_check.py      citations against the list (--online also checks the records)
  prose          prose_lint.py     profile of the text; its warnings are counted
  abstract       abstract_stats.py the venue's cap on the abstract (--abstract-words, --abstract-chars)
  duplication    overlap_check.py  conclusion against abstract and introduction (a finding to review, never a failure)
  figures        fig_lint.py       all figure scripts in one run (with --figures)
  brief          brief_check.py    the claim sheet, and its key numbers against the text (with --brief)
  methods        methods_check.py  the reproducibility checklist (with --repro)
  house rules    audit_tex.py      limitations outside the Results, voice, punctuation, gap, tone, roadmap, earlier work
                                   (ground rules 7 and 10 to 15 of SKILL.md; a finding to review, never a failure)

Cross-checks made here:
  placeholders   TODO, ??, [CITE], lorem ipsum, example images, coloured or struck-out text left in; a statement that
                 ends in an ellipsis ("publicly available via ..."); "Fig. X", "Supplementary Fig. X", "Table X"
  compile log    undefined references and citations, labels defined twice (reads main.log if present)
  numbers        a number in the abstract or the conclusion that the rest of the text does not contain
  sentences      sentences of more than 30 words in the abstract and the conclusion
  abbreviations  defined in the abstract and not again in the text
  statements     the statements named with --require; a data statement that offers data on request only
  initials       initials in the contribution statement that match no author, and authors without a role
  limits         abstract, running text, display items, references and title against the limits given

What no script can check is listed at the end of the report: the tests of the parts that need a reader.
Standard library only. Exit status is 1 if a part check fails or a cross-check reports an error.
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prose_lint  # noqa: E402  (same folder; supplies the reader and the de-TeX step)

PLACEHOLDER = [(r"\?\?", "\"??\" (an unresolved reference)"), (r"\b(?:TODO|TBD|FIXME|XXX)\b", "a to-do mark"),
               (r"\[(?:CITE|REF|CITATION|FIGURE)[^\]]*\]", "a placeholder in brackets"), (r"lorem\s+ipsum", "filler text"),
               (r"\\(?:todo|hl|sout|added|deleted|replaced)\s*[\[{]", "an editing command"), (r"\\textcolor\s*\{(?:red|blue|magenta)\}", "coloured text"),
               (r"example-image", "a placeholder image"), (r"\[?[Pp]laceholder\b", "the word \"placeholder\""),
               (r"citation\s+needed|\bto\s+be\s+(?:added|written)\s+(?:later|here|soon)|insert\s+\w+\s+here", "an unfinished passage")]
# read on the text with mathematics masked, so that "1, ..., N" in a formula is not taken for a gap
ELLIPSIS_MID = re.compile(r"(?:…|\.\.\.)\s*[.;]\s")                 # "available via .... The code"
ELLIPSIS_END = re.compile(r"(?:…|\.\.\.)[\s.;:)\]]*$")              # "publicly available via ..." at the end of a line
NUMBER_LEFT = re.compile(r"(?<![A-Za-z])(?P<item>(?:Supplementary|Extended\s+Data)\s+(?:Figs?\.?|Figures?|Tables?|Notes?)|Figs?\.?|Figures?|Tables?)"
                         r"\s*(?:S\s?)?(?P<n>XX?|x)(?![A-Za-z0-9])")                           # "Fig. X", "Supplementary Table X"
STATEMENTS = {
    "data": r"data\s+(?:and\s+(?:code|materials)\s+)?availability|availability\s+of\s+data|\bdata\b[^.]{0,120}?\b(?:are|is|will\s+be|have\s+been)\s+"
            r"(?:made\s+)?(?:openly\s+|publicly\s+|freely\s+)?(?:available|deposited)\b|no\s+data\s+were\s+(?:created|generated|analy[sz]ed)",
    "code": r"code\s+availability|\bcode\b[^.]{0,100}?\b(?:is|are|will\s+be)\s+(?:openly\s+|publicly\s+)?available|source\s+code",
    "competing": r"competing\s+interests?|conflicts?\s+of\s+interest",
    "contributions": r"author\s+contributions?|contributed\s+equally|(?:each|all)\s+authors?\s+(?:contributed|discussed|commented|reviewed|approved)|"
                     r"\b(?:[A-Z]\.[\s\-]?){2,4}(?:\s*(?:,|and)\s*(?:[A-Z]\.[\s\-]?){2,4})*\s*:?\s*[^.]{0,80}?(?:conceiv|design|perform|wrote|supervis|"
                     r"synthesi|fabricat|measur|analy[sz]|develop|carried|Conceptuali[sz]ation|Investigation|Methodology|Software|Writing)",
    "funding": r"\bfunding\b|supported\s+by|financial\s+support|grant\s+no",
    "ai": r"AI\s+use|use\s+of\s+AI|artificial\s+intelligence|language\s+model|generative\s+AI|AI[\s-]assisted|AI\s+tools?"
          r"|ChatGPT|GPT-?\d|\bClaude\b|\bCodex\b|Copilot|\bGemini\b|OpenAI|Anthropic|\bLLMs?\b",
    "acknowledgments": r"acknowledg",
    "ethics": r"ethic|informed\s+consent|institutional\s+review",
}
REPOSITORY = re.compile(r"zenodo|figshare|dryad|osf\.io|dataverse|materials\s?cloud|nomad|github|gitlab|doi\.org|10\.\d{4,9}/", re.I)
SOFT = {"duplication", "house rules"}
READER_TESTS = [
    "Claim: title, abstract, last paragraph of the introduction and conclusion state the same result, within NOT SHOWN of brief.md",
    "Trace: every claim of the abstract is established by a Results paragraph and a display item (reverse outline against outline.md)",
    "Verbs: no section uses a stronger verb for the result than the kind of evidence allows",
    "Hand-off: the takeaway of each figure is stated in the text where the figure is first cited",
    "Notation: every symbol defined at first use, one symbol per quantity, the same in text, figures, tables and supplement",
    "Supplement: the main text stands alone; each callout states its result and names a place",
    "Limits: every entry of NOT SHOWN is stated once, in the Results beside the evidence it bounds, and nowhere else as a limitation (ground rule 10)",
    "Flow: the first sentences that reverse_outline.py lists tell the argument, each following from the last (ground rule 15)",
    "Statements: every declaration is true today (identifiers resolve, interests confirmed by the authors)",
]


def run(name, script, args, cwd):
    cmd = [sys.executable, os.path.join(HERE, script)] + args
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd, timeout=1800)
        out, code = done.stdout + done.stderr, done.returncode
    except (OSError, subprocess.SubprocessError) as exc:
        out, code = f"could not run: {exc}", 2
    m = re.findall(r"(\d+)\s+error\(s\),\s+(\d+)\s+warning\(s\)(?:,\s+(\d+)\s+note\(s\))?", out)
    e, w, n = (int(m[-1][0]), int(m[-1][1]), int(m[-1][2] or 0)) if m else (None, None, None)
    if m is None or not m:
        only_w = re.findall(r"(\d+)\s+warning\(s\),\s+(\d+)\s+note\(s\)", out)
        if only_w:
            e, w, n = 0, int(only_w[-1][0]), int(only_w[-1][1])
    if not m:
        tex_rules = re.findall(r"(\d+)\s+critical,\s+(\d+)\s+should fix,\s+(\d+)\s+nice to have", out)   # audit_tex.py
        if tex_rules:
            e, w, n = (int(x) for x in tex_rules[-1])
    status = "FAIL" if code != 0 else ("REVIEW" if (w or 0) > 0 else "PASS")
    if name in SOFT and status == "FAIL":
        status = "REVIEW"                                # a finding to fix, not one that blocks submission
    return {"name": name, "script": script, "cmd": " ".join([script] + args), "code": code, "e": e, "w": w, "n": n, "out": out, "status": status}


def numbers(tex):
    """Numbers quoted in a piece of LaTeX, as strings; single digits, exponents and indices are left out."""
    t = re.sub(r"(?<!\\)%.*", "", tex)
    t = re.sub(r"\\(?:cite\w*|ref|eqref|cref|Cref|label|autoref|includegraphics|bibitem)\*?\s*(?:\[[^\]]*\])*\{[^{}]*\}", " ", t)
    t = re.sub(r"(\d+(?:\.\d+)?)\s*\\times\s*10\^\{?\s*(-?\d+)\s*\}?", r"\1e\2", t)
    t = re.sub(r"[_^]\{[^{}]*\}|[_^][A-Za-z0-9]", " ", t)
    found = re.findall(r"(?<![A-Za-z\d.])\d+(?:\.\d+)?(?:e-?\d+)?(?![\d]*[A-Za-z_])|(?<![A-Za-z\d.])\d+(?:\.\d+)?(?=\\(?:un|,|%|mathrm|text|;))", t)
    return {n for n in found if not re.fullmatch(r"\d", n)}


def sections(text):
    """{heading: text} of a de-TeXed manuscript, in order, with '(front)' for what precedes the first heading."""
    out, name = {}, "(front)"
    for piece in re.split(r"(@@HEAD .*?@@)", text, flags=re.S):
        m = re.match(r"@@HEAD (.*?)@@", piece, re.S)
        if m:
            name = re.sub(r"\s+", " ", m.group(1)).strip() or name
            out.setdefault(name, "")
        else:
            out[name] = out.get(name, "") + piece
    return out


def raw_section(raw, title):
    """The LaTeX source of the section with this title (or of the abstract)."""
    if title.lower() == "abstract":
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, re.S)
        return m.group(1) if m else ""
    m = re.search(r"\\(?:sub)*section\*?\s*(?:\[[^\]]*\])?\{\s*" + re.escape(title) + r"\s*\}", raw)
    if not m:
        return ""
    nxt = re.search(r"\\(?:sub)*section\*?\s*(?:\[[^\]]*\])?\{|\\paragraph\*?\s*\{|\\begin\{acknowledg|\\acknowledg|"
                    r"\\begin\{thebibliography\}|\\bibliography\{|\\end\{document\}", raw[m.end():])
    return raw[m.end():m.end() + nxt.start()] if nxt else raw[m.end():]


def masked_lines(raw):
    """The source with mathematics and the bibliography blanked, line for line; \\ldots written as an ellipsis."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    t = re.sub(r"\\begin\{(equation|align|gather|multline|eqnarray|displaymath|math|thebibliography)\*?\}.*?\\end\{\1\*?\}",
               blank, raw, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$[^$]*(?<!\\)\$", blank, t, flags=re.S)
    t = re.sub(r"\\(?:l|text)?dots\b(?:\{\})?|\\textellipsis\b(?:\{\})?", "\u2026", t)
    return t.replace("~", " ").split("\n")


def unfinished(plain, k):
    """Whether line k ends a statement with an ellipsis; a sentence that goes on in lower case on the next line
    ("Co, Fe, ..." / "and their alloys") is a list, not a gap."""
    if ELLIPSIS_MID.search(plain[k]):
        return True
    if not ELLIPSIS_END.search(plain[k]):
        return False
    following = next((x.strip() for x in plain[k + 1:] if x.strip()), "")
    return not re.match(r"[a-z(,]", following)


def cross_checks(lines, opts):
    found = []

    def add(level, where, msg):
        found.append((level, where, msg))

    raw = "\n".join(t for _, _, t in lines)
    body_start = raw.find("\\begin{document}")
    # ----- placeholders
    plain = masked_lines(raw)
    tables = len(re.findall(r"\\begin\{(?:table|sidewaystable)\*?\}", raw))
    for k, (name, n, line) in enumerate(lines):
        for pattern, what in PLACEHOLDER:
            if re.search(pattern, line, re.I if "lorem" in pattern or "laceholder" in pattern else 0):
                add("E", f"{name}:{n}", f"{what} is left in the text: \"{line.strip()[:70]}\"")
                break
        else:
            text = plain[k] if k < len(plain) else ""
            left = [m for m in NUMBER_LEFT.finditer(text)          # "Table X" is Table 10 where tables are numbered I, II, ...
                    if not (m.group("item").lower().startswith("tab") and len(m.group("n")) * 10 <= tables)]
            if left:
                add("E", f"{name}:{n}", f"a figure or table number left as a placeholder (\"{' '.join(left[0].group(0).split())}\"): "
                                        f"\"{line.strip()[:70]}\"")
            elif unfinished(plain, k):
                add("E", f"{name}:{n}", f"an unfinished statement, ending in an ellipsis, is left in the text: \"{line.strip()[:70]}\"")
    # ----- the compile log
    log = os.path.splitext(opts.main)[0] + ".log"
    if os.path.isfile(log):
        text = open(log, encoding="utf-8", errors="replace").read()
        for kind, pattern in (("reference", r"Reference `([^']+)' on page \d+ undefined"), ("citation", r"Citation `([^']+)' on page \d+ undefined"),
                              ("label defined twice", r"Label `([^']+)' multiply defined")):
            keys = sorted(set(re.findall(pattern, text)))
            if keys:
                add("E", os.path.basename(log), f"undefined {kind}: " + ", ".join(keys[:8]) if "twice" not in kind else f"{kind}: " + ", ".join(keys[:8]))
        over = len(re.findall(r"Overfull \\hbox", text))
        if over:
            add("N", os.path.basename(log), f"{over} overfull line(s): text runs into the margin")
    # ----- numbers of the abstract and the conclusion against the rest
    heads = [m.group(1) for m in re.finditer(r"\\(?:sub)*section\*?\s*(?:\[[^\]]*\])?\{([^{}]*)\}", raw)]
    closing = next((h for h in reversed(heads) if re.search(r"conclu|summary|outlook", h, re.I)), None)
    for title in ["Abstract"] + ([closing] if closing else []):
        part = raw_section(raw, title)
        if not part.strip():
            continue
        rest = raw[max(body_start, 0):].replace(part, " ")
        missing = sorted(numbers(part) - numbers(rest))
        if missing:
            add("W", title, f"quotes {', '.join(missing[:8])}, which the rest of the text does not contain: the {title.lower()} may give no number that the body lacks")
    # ----- sentence limits of the abstract and the conclusion (parts/abstract.md, parts/conclusion.md)
    plain_parts = sections(prose_lint.detex(raw))
    for title in ["Abstract"] + ([closing] if closing else []):
        body = re.sub(r"\s+", " ", plain_parts.get(title, ""))
        long = [len([w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", body[a:b]) if w not in ("MATH", "CITE", "REF")])
                for a, b in prose_lint.sentences(body)]
        long = [n for n in long if n > 30]
        if long:
            add("W", title, f"{len(long)} sentence(s) over 30 words (longest {max(long)}): the limit of this skill for the {title.lower()} is 30")
    # ----- abbreviations defined in the abstract only
    abstract = raw_section(raw, "Abstract")
    if abstract:
        after = raw[raw.find(abstract) + len(abstract):]
        for m in re.finditer(r"\(([A-Z]{2,6})s?\)", abstract):
            short = m.group(1)
            if re.search(rf"(?<![A-Za-z]){short}s?(?![A-Za-z])", after) and not re.search(rf"\({short}s?\)", after):
                add("N", "Abstract", f"{short} is defined in the abstract and used in the text without being defined there again")
    # ----- required statements
    low = raw[max(body_start, 0):]
    for name in opts.require or []:
        if not re.search(STATEMENTS[name], low, re.I):
            add("E", "statements", f"no statement on {name} was found, and the venue requires one")
    das = re.search(STATEMENTS["data"], low, re.I)
    if das:
        tail = low[das.start():das.start() + 900]
        if re.search(r"(?:up)?on\s+(?:reasonable\s+)?request", tail, re.I) and not REPOSITORY.search(tail):
            add("W", "statements", "the data are offered on request only: name a repository and an identifier where that is possible")
    # ----- initials
    authors = []
    for m in re.finditer(r"\\author\s*(?:\[[^\]]*\])?\s*\{", raw):
        inner = prose_lint_group(raw, m.end() - 1)
        for person in re.split(r"\\and\b|\\\\|,(?![^{]*\})", inner):
            person = re.sub(r"\\(?:thanks|footnote|email|orcid\w*|affiliation|inst)\s*\{[^{}]*\}|\$[^$]*\$|\\[A-Za-z]+|[{}~*\d]", " ", person)
            names = re.findall(r"[A-Z][A-Za-z\u00c0-\u024f'\-]*\.?", person)
            if len(names) >= 2:
                authors.append("".join(n[0] + "." for part in names for n in part.split("-") if n))
    stmt = re.search(r"(?:author\s+contributions?\b|contributions?\s*[:.]|authors?\s+contributed[^:.]{0,60}[:.])(.{0,900})", low, re.I | re.S)
    if stmt and authors:
        given = {m.group(0).replace("-", "") for m in re.finditer(r"(?<![A-Za-z.])(?:[A-Z]\.-?){2,4}(?![A-Za-z])", stmt.group(1).split("\n\n")[0])}
        if given:
            unknown = sorted(given - set(authors))
            absent = sorted(set(authors) - given)
            if unknown:
                add("W", "contributions", f"initials that match no author: {', '.join(unknown)} (authors: {', '.join(authors)})")
            if absent:
                add("W", "contributions", f"authors without a role in the contribution statement: {', '.join(absent)}")
    # ----- limits
    text = prose_lint.detex(raw)
    parts = sections(text)
    words = lambda t: len([w for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", t) if w not in ("MATH", "CITE", "REF")])
    abs_text = re.sub(r"\s+", " ", parts.get("Abstract", "")).strip()
    running = sum(words(t) for name, t in parts.items()
                  if name not in ("(front)", "Abstract") and not prose_lint.SECTION_SKIP.search(name))
    displays = len(re.findall(r"\\begin\{(?:figure|table|SCfigure|sidewaysfigure|sidewaystable)\*?\}", raw))
    cited = {k.strip() for m in re.finditer(r"\\(?:cite|citep|citet|citealp|onlinecite|parencite|textcite)\w*\*?\s*(?:\[[^\]]*\]\s*)*\{([^{}]*)\}", raw)
             for k in m.group(1).split(",") if k.strip()}
    refs = max(len(re.findall(r"\\bibitem", raw)), len(cited))
    tm = re.search(r"\\title\s*(?:\[[^\]]*\])?\s*\{", raw)
    title = re.sub(r"\s+", " ", re.sub(r"\\\\|\\[A-Za-z]+|[{}$]", " ", prose_lint_group(raw, tm.end() - 1))).strip() if tm else ""
    size = [("abstract, words", words(abs_text), opts.abstract_words), ("abstract, characters", len(abs_text), opts.abstract_chars),
            ("running text, words", running, opts.words), ("figures and tables", displays, opts.display_max),
            ("references", refs, opts.refs_max), ("title, characters", len(title), opts.title_chars)]
    for label, value, limit in size:
        if limit is not None and value > limit:
            add("E", "limits", f"{label}: {value}, over the limit of {limit}")
    return found, size


def prose_lint_group(text, i):
    """Content of the brace group that opens at text[i]."""
    depth, j = 0, i
    while j < len(text):
        if text[j] == "\\":
            j += 2
            continue
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j]
        j += 1
    return text[i + 1:]


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Run every check on a finished manuscript and write one report.")
    ap.add_argument("main", help="main source file")
    ap.add_argument("--supp", nargs="+", default=[], help="source file(s) of the supplement")
    ap.add_argument("--bib", nargs="+", default=[], help="bibliography file(s)")
    ap.add_argument("--brief", help="brief.md")
    ap.add_argument("--repro", help="repro.md")
    ap.add_argument("--figures", nargs="+", default=[], help="figure scripts, for fig_lint.py")
    ap.add_argument("--style", help="figstyle.md")
    ap.add_argument("--width-mm", nargs="+", dest="width_mm", default=[], help="column widths, for fig_lint.py")
    ap.add_argument("--online", action="store_true", help="let ref_check.py look up every record")
    ap.add_argument("--require", nargs="+", choices=sorted(STATEMENTS), help="statements the venue requires")
    ap.add_argument("--caption-below", action="store_true", dest="caption_below", help="the venue puts table captions below")
    ap.add_argument("--abstract-words", type=int, dest="abstract_words")
    ap.add_argument("--abstract-chars", type=int, dest="abstract_chars")
    ap.add_argument("--words", type=int, help="limit on the running text, as a plain word count")
    ap.add_argument("--display-max", type=int, dest="display_max")
    ap.add_argument("--refs-max", type=int, dest="refs_max")
    ap.add_argument("--title-chars", type=int, dest="title_chars")
    ap.add_argument("--skip", nargs="+", default=[], help="part checks to leave out, by name")
    ap.add_argument("--report", help="write the report to this file (audit.md)")
    opts = ap.parse_args()
    for p in [opts.main] + opts.supp + opts.bib + [x for x in (opts.brief, opts.repro, opts.style) if x] + opts.figures:
        if not os.path.isfile(p):
            sys.exit(f"audit: no such file: {p}")
    cwd = os.getcwd()
    tex = [opts.main] + opts.supp
    if not opts.bib:                                     # the files named in \bibliography{...}, when they lie beside the main file
        here = os.path.dirname(os.path.abspath(opts.main))
        named = re.findall(r"\\(?:bibliography|addbibresource)\s*\{([^}]+)\}", re.sub(r"(?<!\\)%.*", "", open(opts.main, encoding="utf-8", errors="replace").read()))
        for name in [n.strip() for group in named for n in group.split(",")]:
            path = next((os.path.join(here, c) for c in (name, name + ".bib") if os.path.isfile(os.path.join(here, c))), None)
            if path and path not in opts.bib:
                opts.bib.append(path)
    lines = prose_lint.read_tex(opts.main)
    raw = "\n".join(t for _, _, t in lines)
    parts = sections(prose_lint.detex(raw))
    plan = [("equations", "eq_refs.py", tex), ("citations", "cite_order.py", [opts.main]), ("captions", "caption_check.py", tex),
            ("tables", "table_check.py", tex + (["--caption", "below"] if opts.caption_below else []))]
    if opts.supp:
        plan.append(("supplement", "supp_check.py", [opts.main, "--supp"] + opts.supp))
    refargs = (["--bib"] + opts.bib if opts.bib else []) + (["--online"] if opts.online else [])
    own_lists = [p for p in tex if re.search(r"\\begin\{thebibliography\}", open(p, encoding="utf-8", errors="replace").read())]
    if opts.supp and len(own_lists) == len(tex):         # main text and supplement each carry their own list
        plan.append(("references", "ref_check.py", [opts.main] + refargs))
        plan.append(("references (supplement)", "ref_check.py", opts.supp + refargs))
    else:
        plan.append(("references", "ref_check.py", tex + refargs))
    plan.append(("prose", "prose_lint.py", [opts.main, "--show", "3"]))
    plan.append(("house rules", "audit_tex.py", [opts.main] + (["--supp", opts.supp[0]] if opts.supp else [])
                 + ["--checks", "limits,voice,punct,gap,tone,prior,questions,xrefs"]))
    tmp = tempfile.mkdtemp(prefix="audit_")
    clean = lambda t: re.sub(r"\s+", " ", t.replace("MATH", "X").replace("CITE", "").replace("REF", "N")).strip()
    names = {"abstract": "Abstract", "introduction": next((n for n in parts if re.search(r"introduction", n, re.I)), None),
             "conclusion": next((n for n in reversed(list(parts)) if re.search(r"conclu|summary|outlook", n, re.I)), None)}
    files = {}
    for key, name in names.items():
        if name and parts.get(name, "").strip():
            files[key] = os.path.join(tmp, key + ".txt")
            open(files[key], "w", encoding="utf-8").write(clean(parts[name]) + "\n")
    if "abstract" in files:
        caps = (["--cap-words", str(opts.abstract_words)] if opts.abstract_words else []) + (["--cap-chars", str(opts.abstract_chars)] if opts.abstract_chars else [])
        plan.append(("abstract", "abstract_stats.py", [files["abstract"], "--max-sentence", "1000"] + caps))   # sentence length: a warning below
    if "conclusion" in files and ("abstract" in files or "introduction" in files):
        plan.append(("duplication", "overlap_check.py", [files["conclusion"]] + [files[k] for k in ("abstract", "introduction") if k in files]))
    if opts.figures:
        plan.append(("figures", "fig_lint.py", opts.figures + (["--style", opts.style] if opts.style else []) + (["--width-mm"] + opts.width_mm if opts.width_mm else [])))
    if opts.brief:
        plan.append(("brief", "brief_check.py", [opts.brief, "--tex"] + tex))
    if opts.repro:
        plan.append(("methods", "methods_check.py", tex + ["--repro", opts.repro]))
    results = [run(name, script, args, cwd) for name, script, args in plan if name not in opts.skip]
    found, size = cross_checks(lines, opts)

    out = []
    out.append(f"# Audit of {os.path.basename(opts.main)}")
    out.append(f"\nRun on {datetime.date.today().isoformat()}. Files: {', '.join(tex + opts.bib)}.\n")
    out.append("## Part checks\n\n| Check | Script | Result | Errors | Warnings | Notes |\n|---|---|---|---|---|---|")
    show = lambda v: "-" if v is None else str(v)
    for r in results:
        out.append(f"| {r['name']} | {r['script']} | {r['status']} | {show(r['e'])} | {show(r['w'])} | {show(r['n'])} |")
    out.append("\n## Size\n\n| Quantity | Value | Limit |\n|---|---|---|")
    for label, value, limit in size:
        out.append(f"| {label} | {value} | {limit if limit is not None else 'not given'} |")
    out.append("\nThe running text is a plain word count of the sections between abstract and acknowledgments, captions included, "
               "equations and references excluded. The venue's own method decides.")
    out.append("\n## Cross-checks\n")
    if not found:
        out.append("Nothing found.")
    for level, title in (("E", "Errors"), ("W", "Warnings"), ("N", "Notes")):
        rows = [(w, m) for lv, w, m in found if lv == level]
        if rows:
            out.append(f"**{title}**\n")
            out.extend(f"- {w}: {m}" for w, m in rows)
            out.append("")
    failing = [r for r in results if r["status"] != "PASS"]
    if failing:
        out.append("## Output of the checks that did not pass\n")
        for r in failing:
            body = [line for line in r["out"].splitlines() if line.strip()]
            keep = [line for line in body if re.search(r"error|warning|Unresolved|Duplicate|typed by hand|\[E\]|\[W\]|FAIL|flagged|exceed|repro\.md:|shares|over the", line)]
            shown = keep if len(keep) > 3 else body[-25:]
            cmd = re.sub(r"\S*audit_\w+/", "", r["cmd"])
            out.append(f"### {r['name']} ({cmd})\n\n```\n" + "\n".join(shown[:25])[:3000] + "\n```\n")
    errors = sum(1 for lv, _, _ in found if lv == "E")
    fails = [r["name"] for r in results if r["status"] == "FAIL"]
    out.append("## Blocking\n")
    if errors or fails:
        if fails:
            out.append("- part checks that fail: " + ", ".join(fails))
        if errors:
            out.append(f"- {errors} error(s) in the cross-checks")
    else:
        out.append("Nothing blocks submission among the checks a script can make.")
    out.append("\n## Still to be read by a person or a fresh agent\n")
    out.extend(f"- [ ] {t}" for t in READER_TESTS)
    report = "\n".join(out) + "\n"
    print(report)
    if opts.report:
        with open(opts.report, "w", encoding="utf-8") as handle:
            handle.write(report)
        print(f"wrote {opts.report}")
    sys.exit(1 if (errors or fails) else 0)


if __name__ == "__main__":
    main()
