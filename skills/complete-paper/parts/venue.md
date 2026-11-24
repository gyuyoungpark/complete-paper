# Venue

Stage A · Reads: `brief.md`, the venue's author guidelines, the publisher's style guide and policies, the official template, recent articles of the same type · Writes: `paper-state/venue.md`

Every other part has rules that the target journal or conference can override: how long the abstract may be, how equations are cited, which statements are mandatory, what files are submitted. This part finds those rules for the venue the user names, records them in `venue.md` with their sources, and tells each part what changes.

Venue rules are facts with a date, not knowledge. Guidelines are revised, differ by article type, and are often misquoted on third-party sites. So the rule for this part is: look it up, cite where it came from, and mark what could not be confirmed. Never fill a rule from memory without saying so.

## Modes

- **Write** (set up): the user names a venue; build `venue.md`.
- **Revise** (retarget): the manuscript moves from one venue to another; build the new `venue.md` and list what must change in the manuscript.
- **Audit** (check): compare a manuscript with `venue.md` and report every rule it breaks.

## Inputs

Fix the target. Ask for, or confirm, three things before looking anything up:

1. **The venue**, by its full name. Resolve ambiguous names ("PRB Letter", "Nature Comms") to the exact journal.
2. **The article type** (Letter, Regular Article, Brief Report, Perspective, conference paper, ...). Limits and structure differ by type; if the user has not chosen, list the types that fit the manuscript's length and claim and ask.
3. **The stage**: first submission, revision, or resubmission after a transfer. Some rules apply only at acceptance (figure resolution, source files).

If the user gives no venue and cannot be asked, write `venue.md` with every rule set to the default of the corresponding part and the status "no venue chosen". Every venue check then stays unchecked.

## Steps

### Step 1. Look up the rules

Use sources in this order, and record which one each rule came from:

1. The journal's own author guidelines for the chosen article type, on the publisher's site.
2. The publisher-wide style guide and policies (style and notation guide, length guide, data and AI policies).
3. The official template or document class and its documentation.
4. About ten recent articles of the same type in that journal, for habits the guidelines do not state (heading style, use of a summary paragraph, how equations and figures are cited).
5. Third-party summaries. These are leads, never sources: follow them back to an official page or mark the rule "unverified".

- A journal-specific rule overrides the publisher-wide one. An instruction from the editor to this author overrides both; record it with its date.
- Without web access, ask the user for the guidelines page, a PDF or pasted text. Rules you can only recall are entered as "recalled, unverified".
- "Not stated" is a valid entry. Do not turn the absence of a rule into a rule.
- Record how a limit is counted, not only its size: words or characters, with or without spaces, whether figures, equations, references and captions count, and whether the journal offers a length-check tool.

### Step 2. Collect every item

Collect every item; write "not stated" where the guidelines are silent.

| Group | Items |
|---|---|
| Identity and criteria | publisher; article type; scope; what the editors select for (for example importance, broad interest, validity); review model (single or double blind) |
| Length | main-text limit and how it is counted; limits on figures, tables and references; abstract cap; title cap; supplement limits |
| Structure | required sections and their order; whether headings are allowed; where Methods go; abstract plain or structured; extra front matter (summary paragraph, keywords, highlights, significance statement, graphical abstract) |
| Title and abstract | capitalization; acronyms; citations in the abstract; required items |
| Authors | name and affiliation format; identifiers; corresponding-author and equal-contribution marks; contribution statement and its taxonomy |
| Statements | data availability; code availability; competing interests; funding; ethics; acknowledgments; disclosure of AI use; where each one goes and whether it is mandatory |
| Language and notation | spelling variety; unit system; vector typeface; treatment of d, e and i; percent spacing; decimal sign |
| Equations | numbering style; citation form; appendix and supplement numbering |
| Figures | file formats; resolution; column widths and largest height; smallest and largest text, or lettering height; thinnest line; colour policy and charges; panel labels; policy on AI-generated images; caption style; "Fig." or "Figure"; permissions for reused material |
| Tables | numbering (arabic or roman); where the title goes and how it begins; rules; marks for footnotes |
| References | style; whether titles and DOIs are included; author-list truncation; limits; how preprints, data and software are cited; the bibliography style file |
| Supplement | its official name; numbering prefix; how the main text cites it, and whether every item must be cited there; limits on supplementary items; what the venue offers between main text and supplement (appendix, End Matter, Extended Data, online Methods); whether references cited only there go in the main list; file formats and any required description file; whether it is reviewed and edited |
| Submission | manuscript format and template; line numbers and spacing; anonymization; cover letter and any required justification; suggested referees; reporting forms or checklists; preprint policy; licence and open-access options; charges |

### Step 3. Write `venue.md`

Keep it in `paper-state/`. Every rule has a value, a source and a status, so that a later reader can re-check it.

```markdown
# Venue: <journal>, <article type>
Checked: <date>   Stage: <first submission | revision | transfer>

## Rules
| Group | Rule | Value | Source | Status |
|---|---|---|---|---|
| Length | Abstract cap | 600 characters, spaces included | <URL> | verified |
| Length | Main text | <limit and how it is counted> | <URL> | verified |
| Statements | AI-use disclosure | not stated | <URL of policy page searched> | not stated |
| References | Titles in references | <value> | third-party summary | unverified |

## Directives for other parts
- title: <case, cap, acronym rule>
- abstract: <cap, plain or structured, citations allowed, required items>
- notation: <unit system, typeface choices, spelling>
- equations: <numbering, citation form, supplement prefix>
- figures / tables / captions: <formats, widths, labels, numbering>
- body: <where methods go, whether Results and Discussion are separate, rules and length of headings>
- references: <style file, fields>
- authors: <form of names and affiliations, contact author, marks>
- statements: <which are mandatory and where they go>
- prose: <spelling variety, person and voice, rules for abbreviations and numbers>
- supplement: <official name, numbering, citation form, required citations, limits, middle tier, rule for references>
- submit: <template, line numbers, cover letter, forms>

## Open items
- <rules marked unverified or not stated that matter for this manuscript>
- <instructions from the editor, with date>
```

Status is one of: **verified** (read on an official page, with its URL), **inferred** (from recent articles in the journal), **unverified** (third-party or recalled), **not stated**.

The directives are the part that other parts read first. Write one line per part, containing only what differs from that part's default.

### Step 4. Retarget (Revise mode)

When the venue changes, the manuscript usually has to change more than its formatting.

1. Build the new `venue.md` (Steps 1 to 3).
2. Compare old and new rule by rule and list every difference that touches the manuscript, largest first: length and what must be cut or may be added; article structure; abstract cap and form; editorial criteria (a paper framed for broad interest reads differently from one framed for specialists); title rules; reference style; statements that become mandatory; supplement name and numbering; template.
3. For each difference name the part that handles it (abstract, title, bibliography, ...), so the work can be done in order.
4. Flag claims of importance or breadth written for the old venue that the new venue's criteria do not ask for, and the reverse.

### Step 5. Check (Audit mode)

Run through `venue.md` against the manuscript and report each rule as met, broken or not checkable. Count; do not estimate (`scripts/abstract_stats.py` for the abstract, the journal's own length tool or its counting method for the main text). A rule with status "unverified" is reported as not checkable, not as met.

### Keep it current

- Re-verify the hard limits (length, abstract cap, file formats, mandatory statements) on the day of submission; `parts/submit.md` calls for this.
- Rebuild `venue.md` when the article type changes, when the editor gives new instructions, or when the file is more than a few months old.

### When rules pull in different directions

An editor's instruction to this author first, then the journal's guidelines for the article type, then the publisher-wide guide, then the habits seen in recent articles, then this skill's defaults.

## Checks

1. **Target**: venue, article type and stage are fixed and recorded.
2. **Sources**: every rule has a source; every "verified" rule has an official URL and the date checked.
3. **No silent memory**: nothing recalled or taken from a third-party page is marked verified.
4. **Complete**: every item of Step 2 has a value or "not stated".
5. **Counting**: each limit says how it is counted.
6. **Directives**: one line per part, limited to deviations from that part's default.
7. **Open items**: every unverified or unstated rule that affects this manuscript is listed.

## Report

Reply in the user's language. Keep it short:

1. **Target**: journal, article type, stage, date checked.
2. **Rules that bind this manuscript most**: the five or six that will change the work (length, abstract cap, structure, mandatory statements, template).
3. **Open items**: what could not be confirmed and how the user can confirm it.
4. `venue.md` in full.

In Revise (retarget) mode, the ordered change list in place of item 2.

Do not recommend a venue unless the user asks. If asked, compare the candidates on the rules that matter for this manuscript (length fit, criteria, article type, charges) and leave the choice to the user.

## Relation to other parts

Every part reads its line under "Directives" before applying its own defaults, and reports the venue check as "unchecked" when the rule it needs is unverified or missing. Venue rules override the style choices of every part; they never override accuracy (no part overclaims to satisfy a venue's taste for impact).
