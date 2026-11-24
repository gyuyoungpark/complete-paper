"""Write small Word files (.docx) with the standard library, for the tests of docx_to_tex.py.

    python make_docx.py OUT.docx        writes the example manuscript

Every name, number and sentence here is invented.
"""
import sys
import zipfile
from xml.sax.saxutils import escape

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')


class X(str):
    """A piece of XML, as opposed to plain text."""


def r(text, sup=False, bold=False, hidden=False):
    """One run. A tab in the text becomes Word's own tab element."""
    props = ("<w:b/>" if bold else "") + ("<w:vanish/>" if hidden else "") + ('<w:vertAlign w:val="superscript"/>' if sup else "")
    pieces = []
    for k, chunk in enumerate(text.split("\t")):
        if k:
            pieces.append("<w:tab/>")
        if chunk:
            pieces.append(f'<w:t xml:space="preserve">{escape(chunk)}</w:t>')
    return X(f'<w:r>{"<w:rPr>" + props + "</w:rPr>" if props else ""}{"".join(pieces)}</w:r>')


def sup(text):
    return r(text, sup=True)


def b(text):
    return r(text, bold=True)


def deleted(text):
    """A tracked deletion: Word keeps the text, and the copy must leave it out."""
    return X(f'<w:del w:id="1" w:author="x"><w:r><w:delText>{escape(text)}</w:delText></w:r></w:del>')


def mr(text):
    return X(f"<m:r><m:t>{escape(text)}</m:t></m:r>")


def msub(base, sub):
    return X(f"<m:sSub><m:e>{mr(base)}</m:e><m:sub>{mr(sub)}</m:sub></m:sSub>")


def math(*parts):
    return X("<m:oMath>" + "".join(x if isinstance(x, X) else mr(x) for x in parts) + "</m:oMath>")


def display(formula):
    return X("<m:oMathPara>" + formula + "</m:oMathPara>")


def p(*runs, style=None, numbered=False):
    ppr = ""
    if style or numbered:
        ppr = ("<w:pPr>" + (f'<w:pStyle w:val="{style}"/>' if style else "")
               + ('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>' if numbered else "") + "</w:pPr>")
    return X("<w:p>" + ppr + "".join(x if isinstance(x, X) else r(x) for x in runs) + "</w:p>")


def table(rows, borders=("top", "bottom"), head_rule=True):
    """A table of text cells; borders of the whole table, and a rule under the first row."""
    tb = "".join(f'<w:{s} w:val="single" w:sz="4"/>' for s in borders)
    out = [f"<w:tbl><w:tblPr><w:tblBorders>{tb}</w:tblBorders></w:tblPr>"]
    for k, row in enumerate(rows):
        cells = []
        for c in row:
            rule = '<w:tcBorders><w:bottom w:val="single" w:sz="4"/></w:tcBorders>' if (k == 0 and head_rule) else ""
            cells.append(f"<w:tc><w:tcPr>{rule}</w:tcPr>{p(c)}</w:tc>")
        out.append("<w:tr>" + "".join(cells) + "</w:tr>")
    return X("".join(out) + "</w:tbl>")


def equation_table(formula, number):
    """A formula in one cell and its number "(n)" in the next, the usual layout of numbered equations in Word."""
    return X(f'<w:tbl><w:tblPr/><w:tr><w:tc>{p(formula)}</w:tc>'
             f'<w:tc>{p(f"({number})")}</w:tc></w:tr></w:tbl>')


STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {NS}>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>
<w:pPr><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>
<w:pPr><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/></w:rPr></w:style>
</w:styles>"""
CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""
RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""


def build(path, blocks):
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document {NS}><w:body>'
                + "\n".join(blocks) + "<w:sectPr/></w:body></w:document>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", STYLES)


def example():
    """An invented letter on spin-wave damping, with one instance of every pattern the converter reads."""
    linewidth = math(msub("ΔH", "0"), " + αf")
    return [
        p("Damping of spin waves in narrow permalloy strips", style="Title"),
        p("A. Writer", sup("1"), ", B. Coauthor", sup("1,2")),
        p(sup("1"), "Institute of Invented Physics, Example City"),
        p(sup("2"), "Department of Examples, Sample University"),
        p(b("Abstract")),
        p("Spin waves carry information without charge currents, and narrow strips are the natural waveguides for "
          "magnonic circuits. Here we measure the damping of spin waves in permalloy strips by spin-wave resonance (SWR) "
          "and show that the edges add a damping term that grows as the strip narrows below 200 nm."),
        p("Introduction", style="Heading1"),
        p("Magnonic circuits need waveguides with low damping", sup("1,2"), ". Films of permalloy have been measured often",
          sup("3–5"), ", and narrow strips less often", sup("6"), sup(","), sup("7"),
          ". We use spin-wave resonance (SWR) on strips with 10", sup("5"), " averages per field, over an area of 4 µm",
          sup("2"), ", at a current density of 2 A m", sup("−2"), deleted(" with a deleted clause"), r(" and a hidden note", hidden=True),
          ". The SWR linewidth of the strips grows at the edges, and the SWR signal of each strip is fitted alone. "
          "An earlier field sweep is shown in Extended Data Fig. 2."),
        p("Results", style="Heading1"),
        p(b("Edge damping in narrow strips")),
        p("To measure the damping, we record the linewidth against frequency (Fig. 1a). The linewidth follows ",
          math("ΔH"), " of Eq. (1), and the edge term follows Eqs. (1) and (2). A value of Eq. (3) is cited here "
          "although no third equation exists. The strips in Fig. 1b and Fig. 2 are listed in Table 1."),
        equation_table(linewidth, 1),
        p(display(math(msub("α", "e"), " = c/w")), "\t(2)"),
        p("The yield rose by 40% for sample #3, and the R&D code is in run_07 with weights {a}. "
          "The films were grown as in earlier runs", sup("9"), "."),
        p(b("Figure 2")),
        p("Methods"),
        p("We grow the strips by sputtering and lift-off. The SWR spectra are fitted as in Extended Data Fig. 1."),
        p(b("Data availability")),
        p("The data are publicly available via …"),
        p(b("References")),
        p("1\tA. First, J. Invented Phys. 1, 1 (2020)."),
        p("2\tB. Second, J. Invented Phys. 2, 2 (2021)."),
        p("3\tC. Third, J. Invented Phys. 3, 3 (2019)."),
        p("4\tD. Fourth, J. Invented Phys. 4, 4 (2018)."),
        p("5\tE. Fifth, J. Invented Phys. 5, 5 (2017)."),
        p("6\tF. Sixth, J. Invented Phys. 6, 6 (2016)."),
        p("7\tG. Seventh, J. Invented Phys. 7, 7 (2015)."),
        p(b("Figure legends")),
        p("Fig. 2 | Edge damping against strip width. The line is a fit to Eq. (1)."),
        p("Fig. 1 | Linewidth against frequency."),
        p("a, Linewidth of a 500 nm strip. b, Linewidth of a 100 nm strip."),
        p("Table 1 | Strips."),
        table([["Width (nm)", "Thickness (nm)"], ["500", "20"], ["100", "20"]]),
        p(b("Extended Data 1")),
        p("Extended Data Fig. 1 | Fit of one spectrum."),
        p("Extended Data Fig. 2 | Field sweep of a film."),
    ]


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "example.docx", example())
