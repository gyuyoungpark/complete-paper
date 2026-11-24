"""Tests for the skill's scripts.

Run from the repository root:
    python -m unittest discover -s tests -v

Network tests (Crossref and arXiv) run only when CP_NETWORK=1 is set.
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "complete-paper", "scripts")
FIX = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, SCRIPTS)

import verify_refs  # noqa: E402


def audit(*args):
    cmd = [sys.executable, os.path.join(SCRIPTS, "audit_tex.py"), *args, "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    data = json.loads(proc.stdout)
    findings = [f for d in data["documents"] for f in d["findings"]]
    return proc.returncode, findings


def has(findings, check, severity, *fragments):
    return any(f["check"] == check and f["severity"] == severity and all(x in f["message"] for x in fragments)
               for f in findings)


class AuditFlawed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.f = audit(os.path.join(FIX, "flawed", "main.tex"), "--code", os.path.join(FIX, "flawed"))

    def test_exit_code(self):
        self.assertEqual(self.code, 1)

    def test_refs(self):
        self.assertTrue(has(self.f, "refs", "CRITICAL", "'c'", "no entry"))
        self.assertTrue(has(self.f, "refs", "CRITICAL", "reference [1] should be 'b'"))
        self.assertTrue(has(self.f, "refs", "SHOULD", "'d' is never cited"))

    def test_xrefs(self):
        self.assertTrue(has(self.f, "xrefs", "CRITICAL", "undefined label 'fig:missing'"))
        self.assertTrue(has(self.f, "xrefs", "CRITICAL", "'fig:three'", "never cited"))
        self.assertTrue(has(self.f, "xrefs", "CRITICAL", "Fig. 2", "before Fig. 1"))
        self.assertTrue(has(self.f, "xrefs", "NICE", "'eq:energy'"))

    def test_abbrev(self):
        self.assertTrue(has(self.f, "abbrev", "SHOULD", "abstract", "'DMI'", "never defined"))
        self.assertTrue(has(self.f, "abbrev", "SHOULD", "body", "'LLG'", "never defined"))
        self.assertTrue(has(self.f, "abbrev", "SHOULD", "'YIG' in the title"))
        self.assertTrue(has(self.f, "abbrev", "NICE", "'SOT'", "used only 1"))
        self.assertFalse(any("XYZ" in f["message"] for f in self.f), "affiliations are not prose")

    def test_numbers(self):
        self.assertTrue(has(self.f, "numbers", "SHOULD", "'45'"))
        self.assertFalse(has(self.f, "numbers", "SHOULD", "'2.6'"))
        self.assertFalse(has(self.f, "numbers", "SHOULD", "'300'"))

    def test_questions(self):
        self.assertTrue(has(self.f, "questions", "CRITICAL", "title"))
        self.assertTrue(has(self.f, "questions", "CRITICAL", "caption"))
        self.assertTrue(has(self.f, "questions", "SHOULD", "body"))

    def test_todo(self):
        self.assertTrue(has(self.f, "todo", "CRITICAL", "red text"))
        self.assertTrue(has(self.f, "todo", "INFO", "1 TODO marker"))
        self.assertTrue(has(self.f, "todo", "NICE", "source comment"))

    def test_figcode(self):
        self.assertTrue(has(self.f, "figcode", "SHOULD", "figure title"))
        self.assertTrue(has(self.f, "figcode", "SHOULD", "annotation"))
        self.assertTrue(has(self.f, "figcode", "NICE", "panel letters"))


class AuditClean(unittest.TestCase):
    def test_no_findings(self):
        code, f = audit(os.path.join(FIX, "clean", "main.tex"))
        problems = [x for x in f if x["severity"] != "INFO"]
        self.assertEqual(problems, [])
        self.assertEqual(code, 0)


class VerifyRefsOffline(unittest.TestCase):
    def test_parse_bib(self):
        with open(os.path.join(FIX, "refs.bib"), encoding="utf-8") as fh:
            entries = verify_refs.parse_bib(fh.read())
        keys = [e["key"] for e in entries]
        self.assertEqual(keys, ["epr1935", "lecun2015", "vaswani2017", "lecun_wrong", "phantom_doi", "no_identifier"])
        self.assertEqual(verify_refs.find_ids(entries[0]), ("10.1103/PhysRev.47.777", None))
        self.assertEqual(verify_refs.find_ids(entries[2]), (None, "1706.03762"))
        self.assertEqual(verify_refs.find_ids(entries[5]), (None, None))

    def test_parse_bibitems(self):
        with open(os.path.join(FIX, "bibitems.tex"), encoding="utf-8") as fh:
            entries = verify_refs.parse_bibitems(fh.read())
        self.assertEqual([e["key"] for e in entries], ["epr", "epr_wrongvol", "attention"])
        self.assertEqual(verify_refs.find_ids(entries[2]), (None, "1706.03762"))

    def test_compare_bib_fields(self):
        rec = {"title": "Deep learning", "family": "lecun", "families": ["lecun", "bengio", "hinton"],
               "year": 2015, "volume": "521", "page": "436", "article_number": ""}
        good = {"raw": "", "fields": {"author": "LeCun, Yann and Bengio, Yoshua", "title": "Deep Learning",
                                      "year": "2015", "volume": "521", "pages": "436--444"}}
        bad = {"raw": "", "fields": {"author": "Hinton, G. and LeCun, Y.", "title": "Deep learning",
                                     "year": "2019", "volume": "521", "pages": "436"}}
        self.assertEqual(verify_refs.compare(good, rec)[0], [])
        problems = verify_refs.compare(bad, rec)[0]
        self.assertTrue(any("first author" in p for p in problems))
        self.assertTrue(any("year" in p for p in problems))

    def test_compare_bibitem_ignores_numbers_inside_doi(self):
        rec = {"family": "einstein", "families": ["einstein"], "year": 1935, "volume": "47",
               "page": "777", "article_number": ""}
        entry = {"fields": {}, "raw": "A. Einstein, Phys. Rev. \\textbf{48}, 777 (1935), doi:10.1103/PhysRev.47.777."}
        problems = verify_refs.compare(entry, rec)[0]
        self.assertTrue(any("volume 47" in p for p in problems))


def run_script(name, *args):
    cmd = [sys.executable, os.path.join(SCRIPTS, name), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout


class AbstractStats(unittest.TestCase):
    """Fixtures are the invented examples from parts/abstract.md."""

    def test_standard_example(self):
        code, out = run_script("abstract_stats.py", os.path.join(FIX, "abstract_standard.txt"), "--cap-words", "250")
        self.assertEqual(code, 0)
        self.assertIn("sentences: 6", out)
        self.assertNotIn("OVER", out)

    def test_short_example_fits_600_characters(self):
        code, out = run_script("abstract_stats.py", os.path.join(FIX, "abstract_short.txt"), "--cap-chars", "600")
        self.assertEqual(code, 0)
        self.assertIn("characters with spaces: 563", out)

    def test_character_cap_exceeded(self):
        code, out = run_script("abstract_stats.py", os.path.join(FIX, "abstract_standard.txt"), "--cap-chars", "600")
        self.assertEqual(code, 1)
        self.assertIn("OVER CHARACTER CAP", out)

    def test_sentence_limit(self):
        code, out = run_script("abstract_stats.py", os.path.join(FIX, "abstract_standard.txt"), "--max-sentence", "25")
        self.assertEqual(code, 1)
        self.assertIn("OVER 25 WORDS", out)

    def test_reference_words_listed(self):
        _, out = run_script("abstract_stats.py", os.path.join(FIX, "abstract_before.txt"))
        self.assertIn("check references: their", out)

    def test_allowed_uses_not_listed(self):
        _, out = run_script("abstract_stats.py", os.path.join(FIX, "abstract_standard.txt"))
        ref_lines = [l for l in out.splitlines() if "check references" in l]
        self.assertFalse(any("such" in l for l in ref_lines), "'such as' introduces examples")
        self.assertFalse(any("these" in l for l in ref_lines), "a closing 'These results' is allowed")
        _, before = run_script("abstract_stats.py", os.path.join(FIX, "abstract_before.txt"))
        self.assertFalse(any("such" in l for l in before.splitlines() if "check references" in l))


class EqRefs(unittest.TestCase):
    def test_planted_problems(self):
        code, out = run_script("eq_refs.py", os.path.join(FIX, "equations.tex"))
        self.assertEqual(code, 1)
        self.assertIn("Unresolved references: 1", out)
        self.assertIn("eq:missing", out)
        self.assertIn("Duplicate labels: 1", out)
        self.assertIn("Equation numbers typed by hand: 1", out)
        self.assertIn("Numbered displays without a label: 1", out)
        self.assertIn("eq:energy", out.split("never cited")[1])

    def test_clean_manuscript(self):
        code, out = run_script("eq_refs.py", os.path.join(FIX, "clean", "main.tex"))
        self.assertEqual(code, 0)
        self.assertIn("Unresolved references: 0", out)


class AuditCitePlaceholder(unittest.TestCase):
    def test_cite_placeholder_flagged(self):
        code, f = audit(os.path.join(FIX, "cite_placeholder.tex"), "--checks", "todo,abbrev")
        self.assertEqual(code, 1)
        self.assertTrue(has(f, "todo", "CRITICAL", "[CITE: ...]"))
        self.assertTrue(has(f, "todo", "INFO", "1 TODO marker"))
        self.assertFalse(any(x["check"] == "abbrev" and "CITE" in x["message"] for x in f),
                         "CITE is a marker, not an abbreviation")


class AuditFlow(unittest.TestCase):
    """Ground rules 10, 12 and 14: numbers in the order of the argument, plain punctuation, the gap as a need."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.f = audit(os.path.join(FIX, "flow.tex"), "--checks", "xrefs,punct,gap")

    def by(self, check, severity=None):
        return [x for x in self.f if x["check"] == check and (severity is None or x["severity"] == severity)]

    def test_equation_order(self):
        self.assertEqual(self.code, 1)
        self.assertTrue(has(self.f, "xrefs", "CRITICAL", "Eq. 2", "before labeled Eq. 1", "reorder the argument"))
        self.assertTrue(has(self.f, "xrefs", "SHOULD", "'eq:one'", "cited before it is displayed"))

    def test_punctuation(self):
        self.assertTrue(has(self.f, "punct", "SHOULD", "colon in the abstract"))
        self.assertTrue(has(self.f, "punct", "NICE", "semicolon in the body"))
        self.assertTrue(has(self.f, "punct", "NICE", "dash in the caption"))
        self.assertEqual(len(self.by("punct", "SHOULD")) + len(self.by("punct", "NICE")), 3,
                         "title colon, ratio, time, heading and TODO marker are not flagged")

    def test_gap_as_absence(self):
        self.assertTrue(has(self.f, "gap", "SHOULD", "'has not been' in the abstract"))
        self.assertTrue(has(self.f, "gap", "NICE", "'remains unknown' in the introduction"))
        self.assertEqual(len(self.by("gap")), 2, "the Results sentence is not part of the gap")


class AuditConclusionNumbers(unittest.TestCase):
    """Ground rule 16: a number in the conclusion must appear elsewhere in the paper."""

    def test_conclusion_number(self):
        code, f = audit(os.path.join(FIX, "numbers.tex"), "--checks", "numbers")
        found = [x for x in f if x["check"] == "numbers" and x["severity"] == "SHOULD"]
        self.assertEqual(len(found), 1, [x["message"] for x in found])
        self.assertIn("number '0.4' in the conclusion", found[0]["message"])

    def test_statement_after_conclusion_is_not_conclusion(self):
        """A data availability paragraph after the conclusion, with its run count and DOI, is not flagged."""
        main = os.path.join(ROOT, "skills", "complete-paper", "examples", "supplement", "main.tex")
        code, f = audit(main, "--checks", "numbers")
        self.assertEqual([x["message"] for x in f if x["check"] == "numbers" and x["severity"] == "SHOULD"], [])


class RefCheckOffline(unittest.TestCase):
    """scripts/ref_check.py without the network: keys, entries and placeholders."""

    def test_clean(self):
        code, out = run_script("ref_check.py", os.path.join(FIX, "clean", "main.tex"))
        self.assertEqual(code, 0, out)
        self.assertIn("0 error(s), 0 warning(s), 0 note(s)", out)

    def test_missing_and_uncited(self):
        code, out = run_script("ref_check.py", os.path.join(FIX, "flawed", "main.tex"))
        self.assertEqual(code, 1)
        self.assertIn("c: cited 1 time(s), but no such entry", out)
        self.assertIn("d: never cited", out)

    def test_placeholder(self):
        code, out = run_script("ref_check.py", os.path.join(FIX, "cite_placeholder.tex"))
        self.assertEqual(code, 1, out)


class AuditReadable(unittest.TestCase):
    """First principle and ground rules 10 and 15: machine tone, roadmap, earlier work as a fault, context."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.f = audit(os.path.join(FIX, "readable.tex"), "--checks", "tone,prior")

    def test_tone(self):
        self.assertEqual(self.code, 0, "tone and prior findings are never CRITICAL")
        self.assertTrue(has(self.f, "tone", "SHOULD", "abstract", "'crucial'"))
        self.assertTrue(has(self.f, "tone", "NICE", "'delve'"))
        self.assertTrue(has(self.f, "tone", "NICE", "'Furthermore'"))

    def test_roadmap_only_in_introduction(self):
        roadmap = [x for x in self.f if "roadmap" in x["message"]]
        self.assertEqual(len(roadmap), 1, [x["message"] for x in roadmap])
        self.assertIn("The rest of this paper", roadmap[0]["message"])

    def test_earlier_work(self):
        prior = [x for x in self.f if x["check"] == "prior"]
        self.assertEqual(len(prior), 1, [x["message"] for x in prior])
        self.assertIn("'fails to'", prior[0]["message"])

    def test_reverse_outline(self):
        code, out = run_script("reverse_outline.py", os.path.join(FIX, "readable.tex"))
        self.assertEqual(code, 0)
        self.assertIn("This tilt sets the threshold current.   <- POINTS BACK", out)
        self.assertIn("Furthermore, the threshold follows the analytical model.   <- ADDITIVE", out)
        self.assertIn("<- ONE SENTENCE", out)
        self.assertIn("paragraphs: 5   marked for review: 3", out)

    def test_reverse_outline_keeps_equations_in_paragraph(self):
        _, out = run_script("reverse_outline.py", os.path.join(FIX, "clean", "main.tex"))
        self.assertIn("paragraphs: 1", out)


class AuditLimits(unittest.TestCase):
    """Ground rule 10: each limitation is stated once, in the Results."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.f = audit(os.path.join(FIX, "limits.tex"), "--checks", "limits")
        cls.lim = [x for x in cls.f if x["check"] == "limits"]

    def test_outside_results_flagged(self):
        self.assertEqual(self.code, 0, "limits findings are never CRITICAL")
        self.assertTrue(has(self.f, "limits", "SHOULD", "'limited to'", "abstract"))
        self.assertTrue(has(self.f, "limits", "SHOULD", "'not considered'", "caption"))
        self.assertTrue(has(self.f, "limits", "SHOULD", "'limitation'", "'Conclusion'"))
        self.assertEqual(sum(x["severity"] == "SHOULD" for x in self.lim), 3)

    def test_earlier_work_not_flagged(self):
        self.assertFalse(any("Introduction" in x["message"] for x in self.lim))

    def test_results_counted_methods_low(self):
        self.assertTrue(has(self.f, "limits", "INFO", "1 sentence(s)", "in the Results"))
        self.assertTrue(has(self.f, "limits", "NICE", "'not included'", "'Methods'"))

    def test_no_headings(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "letter.tex")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("\\documentclass{article}\\begin{document}\n"
                         "Domain walls were not included in our model.\n\\end{document}\n")
            _, f = audit(p, "--checks", "limits")
        self.assertTrue(has(f, "limits", "NICE", "no section headings"))


class AuditVoice(unittest.TestCase):
    """Ground rule 11: what we did is written with "we" and an active verb."""

    @classmethod
    def setUpClass(cls):
        cls.code, cls.f = audit(os.path.join(FIX, "voice.tex"), "--checks", "voice")
        cls.v = [x for x in cls.f if x["check"] == "voice"]

    def test_abstract_flagged(self):
        self.assertEqual(self.code, 0, "voice findings are never CRITICAL")
        self.assertTrue(has(self.f, "voice", "SHOULD", "abstract", "'we investigate'"))
        self.assertTrue(has(self.f, "voice", "SHOULD", "abstract", "'were performed'"))

    def test_body_passive_low(self):
        self.assertTrue(has(self.f, "voice", "NICE", "body", "'were chosen'"))

    def test_not_flagged(self):
        self.assertEqual(len(self.v), 3, [x["message"] for x in self.v])
        self.assertFalse(any("was proposed" in x["message"] or "was obtained" in x["message"] for x in self.v),
                         "earlier work and captions keep their own voice")


def run_cases(test, relpath):
    """Run one of the skill's planted-fault case files on a copy of the skill; all cases must pass."""
    import re
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        skill = os.path.join(d, "complete-paper")
        shutil.copytree(os.path.join(ROOT, "skills", "complete-paper"), skill,
                        ignore=shutil.ignore_patterns("__pycache__"))
        proc = subprocess.run([sys.executable, os.path.join(skill, relpath)], capture_output=True, text=True,
                              encoding="utf-8")
    m = re.search(r"(\d+) of (\d+) cases pass", proc.stdout)
    test.assertTrue(m, proc.stdout[-2000:] + proc.stderr[-2000:])
    test.assertEqual(m.group(1), m.group(2), proc.stdout[-2000:])
    test.assertEqual(proc.returncode, 0)


class SupplementScripts(unittest.TestCase):
    EX = os.path.join(ROOT, "skills", "complete-paper", "examples", "supplement")

    def test_supp_cases(self):
        """The planted-fault cases in evals/supplement/supp_cases.py all pass."""
        run_cases(self, os.path.join("evals", "supplement", "supp_cases.py"))

    def test_example_is_clean(self):
        code, out = run_script("supp_check.py", os.path.join(self.EX, "main.tex"), "--supp",
                               os.path.join(self.EX, "supplement.tex"))
        self.assertEqual(code, 0, out)
        self.assertIn("0 error(s), 0 warning(s), 0 note(s)", out)

    def test_audit_follows_xr_prefixes(self):
        """References such as S-sec:robust resolve into the supplement; a section's opening paragraph
        may point ahead to the result it derives."""
        code, f = audit(os.path.join(self.EX, "main.tex"), "--supp", os.path.join(self.EX, "supplement.tex"),
                        "--checks", "xrefs")
        self.assertEqual(code, 0, [x["message"] for x in f if x["severity"] != "INFO"])
        self.assertFalse([x for x in f if x["severity"] != "INFO"])
        _, f = audit(os.path.join(self.EX, "main.tex"), "--checks", "xrefs")
        self.assertTrue(has(f, "xrefs", "INFO", "3 reference(s) into another document through xr"))

    def test_eq_refs_two_documents(self):
        code, out = run_script("eq_refs.py", os.path.join(self.EX, "main.tex"), os.path.join(self.EX, "supplement.tex"))
        self.assertIn("Unresolved references: 0", out)
        self.assertIn("linked by the prefixes", out)


try:
    import matplotlib  # noqa: F401
    import numpy  # noqa: F401
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False


@unittest.skipUnless(HAVE_MPL, "the figure scripts need matplotlib and numpy")
class FigureScripts(unittest.TestCase):
    FIGS = os.path.join(FIX, "figures")

    def lint(self, script, *args):
        cmd = [sys.executable, os.path.join(SCRIPTS, "fig_lint.py"), os.path.join(self.FIGS, script), *args]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        return proc.returncode, proc.stdout + proc.stderr

    def test_style_table(self):
        import fig_style
        enc = fig_style.load(os.path.join(self.FIGS, "figstyle.md"))
        self.assertEqual(enc["tilt 15 deg"], {"color": "#0072b2", "label": r"$15^\circ$", "linestyle": "-"})
        self.assertEqual(enc["simulation"]["linestyle"], "none")
        self.assertEqual(enc["simulation"]["marker"], "o")

    def test_clean_figure(self):
        code, out = self.lint("clean_fig.py", "--width-mm", "86", "178", "--min-height-mm", "2",
                              "--style", os.path.join(self.FIGS, "figstyle.md"))
        self.assertEqual(code, 0, out)
        self.assertIn("0 error(s) in 1 figure(s)", out)
        self.assertNotIn("WARNINGS", out)

    def test_faulty_figure(self):
        code, out = self.lint("faulty_fig.py", "--width-mm", "86", "178")
        self.assertEqual(code, 1)
        for planted in ("the figure is 304.8 mm wide", "figure title 'Field-free switching'",
                        "colour map 'jet'", "one colour, 2 meanings", "floating multiplier (1e11)",
                        "panel title 'Threshold current'"):
            self.assertIn(planted, out)

    def test_schematic(self):
        import matplotlib
        matplotlib.use("Agg")
        import fig_lint
        import fig_style as fs
        import schematic3d as s3
        self.assertEqual(len(s3.hall_bar(8, 1, arms=(2.5, 5.5))), 20)
        fs.use(base=8)
        fig, ax = fs.figure(86, 50)
        sc = s3.Scene()
        sc.box((0, 0, 0), (10, 6, 0.8), "#D9D9D9").box((1, 2, 0.8), (8, 2, 0.5), "#D55E00", label="film")
        sc.prism(s3.hall_bar(8, 1, arms=(2.5, 5.5), origin=(1, 2.5)), 1.3, 0.3, "#E69F00")
        sc.arrow((1.5, 3, 1.9), (8.5, 3, 1.9), label=r"$j$").triad((-1.0, -3.0, 0), 1.5).draw(ax)
        self.assertGreater(sum(1 for p in ax.patches if getattr(p, "base_colour", None)), 0)
        result = fig_lint.check(fig, widths_mm=[86, 178])
        self.assertEqual([f for f in result["findings"] if f[0] == "E"], [])
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_lint_cases(self):
        """The planted-fault cases in evals/figures/lint_cases.py all pass.

        They run the example scripts, which save their figures next to themselves, so the cases
        run on a copy of the skill and the example images in the repository stay as published."""
        run_cases(self, os.path.join("evals", "figures", "lint_cases.py"))

    def test_audit_skips_helpers(self):
        """audit_tex's figcode check ignores the copied helpers and schematic arrows."""
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for name in ("fig_style.py", "schematic3d.py", "fig_lint.py"):
                shutil.copy(os.path.join(SCRIPTS, name), d)
            with open(os.path.join(d, "fig1.py"), "w", encoding="utf-8") as fh:
                fh.write("import schematic3d as s3\nsc = s3.Scene()\nsc.arrow((0, 0, 0), (1, 0, 0), label='$j$')\n"
                         "fs.direct_label(ax, line, '$30^\\\\circ$')\n")
            _, f = audit(os.path.join(FIX, "clean", "main.tex"), "--checks", "figcode", "--code", d)
        self.assertFalse(any(x["check"] == "figcode" and x["severity"] != "INFO" for x in f),
                         [x["message"] for x in f])
        self.assertTrue(has(f, "figcode", "INFO", "1 plotting file(s) scanned"))


class CaptionCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.out = run_script("caption_check.py", os.path.join(FIX, "captions.tex"))
        cls.blocks = cls.out.split("captions.tex:")[1:]

    def test_counts_every_caption(self):
        self.assertEqual(self.code, 0)
        self.assertIn("captions: 3", self.out)
        self.assertEqual(len(self.blocks), 3)

    def test_commentary_flagged(self):
        before = self.blocks[0]
        for line in ("trend: decreases, increasing", "outcome: agrees", "interpretation: demonstrating",
                     "evaluation: clearly, well"):
            self.assertIn(line, before)

    def test_descriptive_caption_not_flagged(self):
        self.assertNotIn("      - ", self.blocks[1])

    def test_filler_and_colour(self):
        self.assertIn("filler opener", self.blocks[2])
        self.assertIn("colour named without a line style or marker", self.blocks[2])

    def test_word_cap(self):
        code, out = run_script("caption_check.py", os.path.join(FIX, "captions.tex"), "--max-words", "50")
        self.assertEqual(code, 1)
        self.assertIn("OVER 50 WORDS", out)


class OverlapCheck(unittest.TestCase):
    def test_part_example_shares_no_sentence(self):
        """The conclusion example in parts/conclusion.md shares no sentence with the abstract example."""
        code, out = run_script("overlap_check.py", os.path.join(FIX, "conclusion_after.txt"),
                               os.path.join(FIX, "abstract_standard.txt"))
        self.assertEqual(code, 0)
        self.assertIn("sentences: 4   flagged: 0", out)

    def test_copied_sentence_flagged(self):
        code, out = run_script("overlap_check.py", os.path.join(FIX, "conclusion_copied.txt"),
                               os.path.join(FIX, "abstract_standard.txt"))
        self.assertEqual(code, 1)
        self.assertIn("flagged: 1", out)
        self.assertIn('"these results identify crystal orientation', out)

    def test_abbreviations_do_not_split(self):
        import overlap_check
        self.assertEqual(len(overlap_check.sentences("See Fig. 2 and Eq. 3, e.g. here. Next one.")), 2)


class VersionTool(unittest.TestCase):
    """tools/version.py on a copy of the three files that carry the version."""

    def setUp(self):
        import shutil
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        for rel in (".claude-plugin/plugin.json", "skills/complete-paper/SKILL.md", "CHANGELOG.md"):
            os.makedirs(os.path.dirname(os.path.join(self.root, rel)) or self.root, exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, rel), os.path.join(self.root, rel))

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *args):
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "version.py"), "--root", self.root, *args],
                              capture_output=True, text=True, encoding="utf-8")
        return proc.returncode, proc.stdout + proc.stderr

    def test_repository_is_consistent(self):
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "version.py"), "check"],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def use_version(self, version, changelog):
        """Put the copied files at a known version with a changelog of the test's own, so that the test does not
        depend on whether the repository's current version is released yet."""
        import re
        for rel, pattern, repl in ((".claude-plugin/plugin.json", r'"version": "[^"]*"', f'"version": "{version}"'),
                                   ("skills/complete-paper/SKILL.md", r'(?m)^  version: "[^"]*"', f'  version: "{version}"')):
            p = os.path.join(self.root, rel)
            with open(p, encoding="utf-8") as f:
                text = f.read()
            with open(p, "w", encoding="utf-8") as f:
                f.write(re.sub(pattern, lambda m: repl, text, count=1))
        with open(os.path.join(self.root, "CHANGELOG.md"), "w", encoding="utf-8") as f:
            f.write(changelog)

    def test_release_cycle(self):
        self.use_version("1.2.3", "# Changelog\n\n## [Unreleased]\n\n### Added\n- A change.\n\n"
                                  "## [1.2.2] - 2026-01-01\n\n### Added\n- An earlier change.\n")
        current = self.run_tool("show")[1].strip()
        self.assertEqual(current, "1.2.3")
        major, minor, patch = (int(x) for x in current.split("."))
        self.assertEqual(self.run_tool("bump", f"{major}.{minor}.{patch - 1}")[0], 1)   # never downwards
        code, out = self.run_tool("bump", current, "--date", "2026-12-01")    # first release of the current version
        self.assertEqual(code, 0, out)
        self.assertEqual(self.run_tool("check", "v" + current)[0], 0)
        self.assertIn("### Added", self.run_tool("notes", current)[1])
        self.assertEqual(self.run_tool("bump", current)[0], 1)               # already released
        nxt = f"{major}.{minor + 1}.0"
        code, out = self.run_tool("bump", nxt)                               # [Unreleased] is now empty
        self.assertEqual(code, 1)
        self.assertIn("lists no change", out)
        self.assertEqual(self.run_tool("bump", nxt, "--allow-empty", "--date", "2026-12-05")[0], 0)
        self.assertEqual(self.run_tool("check", "v" + nxt)[0], 0)
        self.assertEqual(self.run_tool("check", "v" + current)[0], 1)         # the tag no longer matches the files
        log = open(os.path.join(self.root, "CHANGELOG.md"), encoding="utf-8").read()
        self.assertLess(log.index("## [Unreleased]"), log.index(f"## [{nxt}] - 2026-12-05"))
        self.assertLess(log.index(f"## [{nxt}]"), log.index(f"## [{current}] - 2026-12-01"))

    def test_files_that_disagree(self):
        p = os.path.join(self.root, ".claude-plugin", "plugin.json")
        text = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(text.replace('"version": "', '"version": "9', 1))
        code, out = self.run_tool("check")
        self.assertEqual(code, 1)
        self.assertIn("plugin.json says", out)


class RealRunFixes(unittest.TestCase):
    """Patterns the scripts got wrong on the first real manuscript (2026-11-24), in an invented fixture."""
    D = os.path.join(FIX, "realrun")

    def findings(self, *checks):
        code, f = audit(os.path.join(self.D, "main.tex"), "--checks", ",".join(checks))
        return f

    def test_equation_met_at_its_display(self):
        """Eq. (1) is displayed first and referenced by number only later: no order finding."""
        f = self.findings("xrefs")
        self.assertFalse([x for x in f if x["check"] == "xrefs" and x["severity"] == "CRITICAL"],
                         [x["message"] for x in f])

    def test_roadmap_with_references(self):
        """'Sections II-III give ..., and Sec. IV states ...' is a roadmap, although the refs are blanked."""
        self.assertTrue(has(self.findings("tone"), "tone", "SHOULD", "roadmap"))

    def test_gap_do_not_evaluate(self):
        self.assertTrue(has(self.findings("gap"), "gap", "NICE", "do not evaluate"))

    def test_limits_home_and_conclusion(self):
        """A limitation in a Results section with another name is at home; the same kind of sentence in the
        Conclusions is flagged."""
        f = [x for x in self.findings("limits") if x["severity"] == "SHOULD"]
        self.assertEqual(len(f), 1, [x["message"] for x in f])
        self.assertIn("Conclusions", f[0]["message"])

    def test_ruledtabular_draws_the_rules(self):
        code, out = run_script("table_check.py", os.path.join(self.D, "main.tex"))
        self.assertIn("0 error(s), 0 warning(s)", out)

    def test_audit_two_documents_and_ai_statement(self):
        """Main text and supplement with their own lists are checked apart; tool names count as an AI statement."""
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "audit.py"), "main.tex", "--supp", "supplement.tex",
                               "--require", "ai"], capture_output=True, text=True, encoding="utf-8", cwd=self.D)
        self.assertRegex(proc.stdout, r"\| references \| ref_check.py \| PASS")
        self.assertRegex(proc.stdout, r"\| references \(supplement\) \| ref_check.py \| PASS")
        self.assertNotIn("no statement on ai", proc.stdout)

    def test_brief_marker_not_counted(self):
        import tempfile
        text = open(os.path.join(ROOT, "skills", "complete-paper", "examples", "brief", "brief.md"), encoding="utf-8").read()
        line = [l for l in text.splitlines() if l.startswith("RESULT:")][0]
        words = len(line.split()) - 1
        padded = line + " word" * (30 - words) + " [unconfirmed]"           # exactly 30 words, plus the marker
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "brief.md")
            open(p, "w", encoding="utf-8").write(text.replace(line, padded))
            code, out = run_script("brief_check.py", p)
        self.assertNotIn("RESULT has 31 words", out)


class LetterLayout(unittest.TestCase):
    """A letter has no section headings, and headings must not shift the reported line numbers."""

    def test_prose_lint_lines_after_headings(self):
        import tempfile
        tex = ("\\documentclass{article}\n\\begin{document}\n\\title{T}\n\\begin{abstract}\n"
               "Short abstract sentence one about magnets and films here.\n\\end{abstract}\n\\maketitle\n"
               "\\section{Introduction}\nIt is worth noting that this sentence sits on line nine of the file.\n"
               "\\section{Results}\nIt is worth noting that this sentence sits on line eleven of the file.\n\\end{document}\n")
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "lines.tex")
            open(p, "w", encoding="utf-8").write(tex)
            code, out = run_script("prose_lint.py", p, "--show", "5")
        self.assertIn("lines.tex:9: begins \"It is worth noting that\"", out)
        self.assertIn("lines.tex:11: begins \"It is worth noting that\"", out)

    def test_audit_counts_a_letter(self):
        """Without \\section, the text after the abstract is running text, not abstract."""
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "audit.py"), os.path.join(FIX, "flawed", "main.tex")],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertIn("| abstract, words | 44 |", proc.stdout)
        self.assertRegex(proc.stdout, r"\| running text, words \| [1-9]\d* \|")


class TextScripts(unittest.TestCase):
    """brief_check, cite_order, table_check, methods_check and prose_lint."""

    def test_text_cases(self):
        """The planted-fault cases in evals/text/cases.py all pass."""
        run_cases(self, os.path.join("evals", "text", "cases.py"))


class FinishScripts(unittest.TestCase):
    """audit.py and submit_check.py."""
    EX = os.path.join(ROOT, "skills", "complete-paper", "examples")

    def test_finish_cases(self):
        """The planted-fault cases in evals/finish/cases.py all pass."""
        run_cases(self, os.path.join("evals", "finish", "cases.py"))

    def test_audit_runs_house_rules(self):
        """audit.py runs audit_tex.py as the house-rules check, and its findings never block."""
        supp = os.path.join(self.EX, "supplement")
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "audit.py"), "main.tex", "--supp", "supplement.tex"],
                              capture_output=True, text=True, encoding="utf-8", cwd=supp)
        row = [ln for ln in proc.stdout.splitlines() if ln.startswith("| house rules |")]
        self.assertEqual(len(row), 1, proc.stdout[-2000:])
        self.assertIn("audit_tex.py", row[0])
        self.assertNotIn("FAIL", row[0])
        self.assertNotIn("house rules", proc.stdout.split("## Blocking", 1)[1].split("##", 1)[0])


sys.path.insert(0, os.path.join(FIX, "word"))
import make_docx  # noqa: E402  (writes invented .docx files with zipfile)


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class DocxToTex(unittest.TestCase):
    """scripts/docx_to_tex.py on an invented Word letter (tests/fixtures/word/make_docx.py), and the scripts on its copy."""

    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = tempfile.TemporaryDirectory()
        cls.docx = os.path.join(cls.tmp.name, "letter.docx")
        make_docx.build(cls.docx, make_docx.example())
        cls.tex = os.path.join(cls.tmp.name, "letter_copy.tex")
        cls.code, cls.out = run_script("docx_to_tex.py", cls.docx, "-o", cls.tex)
        with open(cls.tex, encoding="utf-8") as fh:
            cls.t = fh.read()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_runs(self):
        self.assertEqual(self.code, 0, self.out)
        self.assertTrue(self.t.startswith("% Reading copy of letter.docx"))

    def test_front_and_headings(self):
        for line in ("\\title{Damping of spin waves in narrow permalloy strips}",
                     "\\author{A. Writer\\textsuperscript{1}, B. Coauthor\\textsuperscript{1,2}}",
                     "\\affiliation{\\textsuperscript{2}Department of Examples, Sample University}",
                     "\\begin{abstract}", "\\section{Introduction}", "\\section{Results}",
                     "\\subsection{Edge damping in narrow strips}", "\\section{Methods}", "\\section*{Data availability}",
                     "\\section*{Figure legends}"):
            self.assertIn(line, self.t)
        self.assertNotIn("References", self.t, "the reference heading becomes thebibliography")

    def test_citations_and_exponents(self):
        for cite in ("damping\\cite{r1,r2}", "often\\cite{r3,r4,r5}", "less often\\cite{r6,r7}"):
            self.assertIn(cite, self.t)
        for exponent in ("10\\textsuperscript{5}", "4 \u00b5m\\textsuperscript{2}", "A m\\textsuperscript{\u22122}"):
            self.assertIn(exponent, self.t)
        self.assertIn("runs\\textsuperscript{9}", self.t)
        self.assertIn("outside the reference list stay superscripts: 9", self.out)

    def test_references(self):
        keys = [line.split("}")[0] for line in self.t.split("\\bibitem{")[1:]]
        self.assertEqual(keys, ["r%d" % k for k in range(1, 8)])
        self.assertIn("\\bibitem{r3} C. Third, J. Invented Phys. 3, 3 (2019).", self.t)

    def test_equations(self):
        self.assertIn("\\begin{equation}\n{\u0394H}_{0} + \u03b1f\n\\label{eq:1}\n\\end{equation}", self.t)
        self.assertIn("\\label{eq:2}", self.t)
        self.assertIn("Eqs.~(\\ref{eq:1}) and (\\ref{eq:2})", self.t)
        self.assertIn("Eq. (3) is cited", self.t, "a number with no equation stays as typed")
        self.assertIn("no numbered equation of that number: 3", self.out)

    def test_legends(self):
        figs = self.t.split("\\begin{figure}")[1:]
        self.assertEqual(len(figs), 2)
        self.assertIn("\\caption{Linewidth against frequency. a, Linewidth of a 500 nm strip.", figs[0])
        self.assertIn("\\label{fig:1}", figs[0], "floats follow their numbers, not the order of the legends")
        self.assertIn("\\label{fig:2}", figs[1])
        self.assertIn("legends stand in the order 2, 1", self.out)
        self.assertEqual(self.t.count("\\begin{extdata}"), 2)
        self.assertIn("\\label{tab:1}\n\\begin{tabular}{ll}\n\\toprule\nWidth (nm) & Thickness (nm) \\\\\n\\midrule", self.t)
        self.assertNotIn("\nFigure 2\n", self.t, "the line where an image stands is left out")
        self.assertNotIn("{Extended Data 1}", self.t, "so is 'Extended Data 1' without 'Fig.'")
        self.assertIn("Extended Data Fig. 2.", self.t, "mentions stay as typed")

    def test_escapes_and_left_out(self):
        for s in ("40\\%", "sample \\#3", "R\\&D", "run\\_07", "\\{a\\}"):
            self.assertIn(s, self.t)
        self.assertNotIn("deleted clause", self.t)
        self.assertNotIn("hidden note", self.t)

    def test_scripts_read_the_copy(self):
        code, out = run_script("cite_order.py", self.tex)
        self.assertIn("0 error(s), 0 warning(s)", out)
        self.assertEqual(len([l for l in out.splitlines() if l.strip().startswith("Fig. ")]), 2,
                         "Extended Data figures are not main figures, and 'Extended Data Fig. 2' does not cite Fig. 2")
        code, out = run_script("ref_check.py", self.tex)
        self.assertIn("0 error(s), 0 warning(s)", out)
        self.assertIn("keys cited 7 | entries 7", out)
        code, out = run_script("table_check.py", self.tex)
        self.assertIn("0 error(s), 0 warning(s)", out)
        _, f = audit(self.tex, "--checks", "xrefs")
        self.assertFalse(any(x["severity"] == "CRITICAL" for x in f), [x["message"] for x in f])
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "audit.py"), self.tex, "--skip", "equations", "citations",
                               "captions", "tables", "references", "prose", "house rules", "abstract", "duplication"],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertIn("an unfinished statement, ending in an ellipsis", proc.stdout)

    def test_word_numbering_and_results_heading(self):
        """References numbered by Word's own list, and a draft with no Results heading."""
        p, b, sup = make_docx.p, make_docx.b, make_docx.sup
        blocks = [p("A short title", style="Title"), p("C. Author"),
                  p("Introduction", style="Heading1"), p("Strips guide spin waves", sup("1"), " and films damp them", sup("2"), "."),
                  p(b("Edge damping")), p("The edges add damping in every strip that we measure here."),
                  p(b("Discussion")), p("The edge term sets the length of a waveguide."),
                  p(b("References")), p("A. First, J. Invented Phys. 1, 1 (2020).", numbered=True),
                  p("B. Second, J. Invented Phys. 2, 2 (2021).", numbered=True)]
        docx = os.path.join(self.tmp.name, "noresults.docx")
        make_docx.build(docx, blocks)
        tex = os.path.join(self.tmp.name, "noresults.tex")
        code, out = run_script("docx_to_tex.py", docx, "-o", tex)
        self.assertEqual(code, 0, out)
        self.assertIn("no Results heading", out)
        t = read(tex)
        self.assertIn("\\bibitem{r2} B. Second", t)
        self.assertIn("spin waves\\cite{r1}", t)
        self.assertNotIn("\\section{Results}", t)
        run_script("docx_to_tex.py", docx, "-o", tex, "--add-results")
        t = read(tex)
        self.assertLess(t.index("\\section{Results}"), t.index("\\subsection{Edge damping}"))
        self.assertLess(t.index("\\section{Introduction}"), t.index("\\section{Results}"))

    def test_will_not_overwrite_a_source(self):
        p = write(self.tmp.name, "letter_source.tex", "\\documentclass{article}\n")
        code, out = run_script("docx_to_tex.py", self.docx, "-o", p)
        self.assertNotEqual(code, 0)
        self.assertEqual(read(p), "\\documentclass{article}\n")


class AuditTypedMentions(unittest.TestCase):
    """audit_tex.py --checks xrefs counts figure and table numbers typed as text, as Word-derived text has them."""

    TEX = ("\\documentclass{article}\n\\begin{document}\n\\section{Results}\n"
           "The map is in Fig. 2 and Extended Data Fig. 4.\n"
           "Switching is shown in Fig. 1a\u2013c and 5, and the rates in Table I.\n"
           "The long runs are in Figs. 5\u20136, with more in Supplementary Fig. 4 and Supplementary Fig. 3.\n"
           + "".join("\\begin{figure}\\caption{Panel %d.}\\label{fig:%s}\\end{figure}\n" % (k, c) for k, c in enumerate("abcdef", 1))
           + "\\begin{table}\\caption{Rates.}\\label{tab:rates}\\end{table}\n\\end{document}\n")

    def test_typed_mentions(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            _, f = audit(write(d, "typed.tex", self.TEX), "--checks", "xrefs")
        never = sorted(x["message"].split("'")[1] for x in f if "never cited" in x["message"])
        self.assertEqual(never, ["fig:c", "fig:d"], "a panel range is not a figure range; Extended Data and "
                                                     "Supplementary figures are not main figures")
        self.assertTrue(has(f, "xrefs", "CRITICAL", "Fig. 2 ('fig:b') is first cited here, before Fig. 1"))
        self.assertTrue(has(f, "xrefs", "INFO", "6 figure or table number(s) typed as text"))


class CiteOrderTypedLists(unittest.TestCase):
    """cite_order.py reads every number of a typed list or range, with the panels of each, as Word-derived text has them;
    "Fig. 1. The" is a figure, not 1 T."""

    def test_lists_and_ranges(self):
        import tempfile
        caps = {4: "(a) Trace. (b) Cut.", 5: "(a) Map. (b) Cut. (c) Phase diagram."}
        tex = ("\\begin{document}\nThe sketch is in Fig. 1. The map is in Figs. 2 and 3, the cuts in Fig. 4a,b and 5(c), "
               "and the rates in Tables I and II.\nThe long runs are in Figs. 6\u20138 and Extended Data Figs. 9 and 10.\n\n"
               + "".join("\\begin{figure}\\caption{%s}\\label{f:%d}\\end{figure}\n" % (caps.get(k, "Panel."), k) for k in range(1, 11))
               + "\\begin{table}\\caption{A.}\\label{t:a}\\end{table}\n\\begin{table}\\caption{B.}\\label{t:b}\\end{table}\n\\end{document}\n")
        with tempfile.TemporaryDirectory() as d:
            code, out = run_script("cite_order.py", write(d, "lists.tex", tex))
        never = [l.split(": ")[1].split()[1] for l in out.splitlines() if "is never cited" in l]
        self.assertEqual(never, ["9", "10"], "Extended Data figures are not main figures")
        self.assertIn("Fig. 5: panels (a), (b) named in the caption and never cited", out)
        self.assertNotIn("Fig. 4:", out, "panel (c) belongs to Fig. 5, not to Fig. 4")
        self.assertNotIn("first cited in the order", out)
        self.assertIn("10 figure or table number(s) are typed by hand", out)


class AuditWordPlaceholders(unittest.TestCase):
    """audit.py: a statement left ending in an ellipsis, and figure or table numbers left as X."""
    SKIP = ["--skip", "equations", "citations", "captions", "tables", "references", "prose", "house rules", "abstract", "duplication"]

    def cross(self, tex):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "audit.py"), write(d, "main.tex", tex)] + self.SKIP,
                                  capture_output=True, text=True, encoding="utf-8")
        return [l for l in proc.stdout.splitlines() if l.startswith("- main.tex:")]

    def test_planted(self):
        found = self.cross("\\documentclass{article}\n\\begin{document}\n\\section{Results}\n"
                           "More runs are in Supplementary Fig.~X.\n"
                           "The rates are listed in Table X.\n"
                           "The states $1, \\ldots, N$ are counted, and the labels a, b, ... and c are kept.\n"
                           "Materials such as Co, Fe, ...\nand their alloys are used.\n"
                           "\\section*{Data availability}\nThe data are publicly available via \\ldots\n"
                           "\\section*{Code availability}\nThe code is at ... . It runs on one core.\n\\end{document}\n")
        self.assertEqual(sum("left as a placeholder (\"Supplementary Fig. X\")" in l for l in found), 1, found)
        self.assertEqual(sum("left as a placeholder (\"Table X\")" in l for l in found), 1, found)
        self.assertEqual([l.split(":")[1] for l in found if "ellipsis" in l], ["10", "12"], found)
        self.assertEqual(len(found), 4, found)

    def test_roman_table_ten(self):
        """Where tables are numbered I, II, ..., "Table X" is the tenth table."""
        tables = "".join("\\begin{table}\\caption{T.}\\end{table}\n" for _ in range(10))
        found = self.cross("\\documentclass{article}\n\\begin{document}\nThe last rates are in Table X.\n" + tables + "\\end{document}\n")
        self.assertEqual(found, [])


class ProseLintAbbrevAbstract(unittest.TestCase):
    """Ground rule 5: the abstract and the main text each define an abbreviation once."""

    def test_abstract_definition_is_not_a_repeat(self):
        import tempfile
        tex = ("\\documentclass{article}\n\\begin{document}\n\\begin{abstract}\n"
               "We switch a magnetic tunnel junction (MTJ) with a short pulse of current in a thin film here.\n\\end{abstract}\n"
               "\\section{Introduction}\nA magnetic tunnel junction (MTJ) stores one bit in a thin film of iron. "
               "The MTJ is read by its resistance in this work. Each MTJ is written by a pulse of current in this work.\n\n"
               "A spin-orbit torque (SOT) switches the free layer of the film here. The spin-orbit torque (SOT) needs no field "
               "in this geometry. The SOT is strong in heavy metals such as platinum here.\n\\end{document}\n")
        with tempfile.TemporaryDirectory() as d:
            _, out = run_script("prose_lint.py", write(d, "abbr.tex", tex), "--only", "abbrev", "--show", "0")
        self.assertNotIn("MTJ is defined 2", out)
        self.assertIn("SOT is defined 2 times in the text", out)


@unittest.skipUnless(os.environ.get("CP_NETWORK") == "1", "set CP_NETWORK=1 to run network tests")
class VerifyRefsOnline(unittest.TestCase):
    def test_bib(self):
        cmd = [sys.executable, os.path.join(SCRIPTS, "verify_refs.py"), os.path.join(FIX, "refs.bib"), "--json"]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        status = {r["key"]: r["status"] for r in json.loads(proc.stdout)["results"]}
        self.assertEqual(status["epr1935"], "verified")
        self.assertEqual(status["lecun2015"], "verified")
        self.assertEqual(status["vaswani2017"], "verified")
        self.assertEqual(status["lecun_wrong"], "mismatch")
        self.assertEqual(status["phantom_doi"], "not-found")
        self.assertEqual(status["no_identifier"], "no-id")
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
