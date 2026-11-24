# Agent-level evals

Cases for `claude plugin eval`. Each case is a folder with a `prompt.md` (the request, with its input written into it) and a `graders/` folder. The script-level checks live elsewhere, in `skills/complete-paper/evals/` (planted-fault cases) and `tests/` (unit tests).

Each case runs the skill in a Claude Code session twice, with the plugin and without it, and grades what the session does. The grader `skill_fired` is an indicator that the skill was loaded and is not scored.

| Case | Rule it tests | Scored graders |
|---|---|---|
| `abstract-no-invented-numbers` | First principle 2 and ground rule 1: a value the brief does not give is not written, it is marked or reported; simulation results are not described as observations | `no_invented_numbers` (judge), `marks_the_gap` (regex) |
| `audit-reports-and-asks` | Audit mode reports and does not rewrite; it names priority claims, wrong evidence verbs, the passive, evaluative tone, a limitation in the abstract and a clause-joining colon, then hands the next step back to the author | `names_problems`, `no_rewrite`, `hands_back` (judge) |
| `conclusion-limits-once` | Ground rule 10: the conclusion states no limitation as a shortcoming and looks forward; scope words stay; ground rule 14 | `forward_not_back` (judge) |
| `intro-no-invented-citations` | Ground rule 1 for references: no work cited from memory, a `[CITE: ...]` placeholder instead; the gap as a need | `placeholders_not_references` (judge), `no_doi`, `has_placeholder` (regex) |
| `title-matches-evidence` | The title part: a noun phrase, the system and the result, no experiment words for a simulation, no praise, plain-text formula | `title_within_claim` (judge) |

Run, from the repository root:

```
claude plugin eval . --runs 1 --no-publish --judge-model sonnet
```

`--runs 1` keeps the run to ten sessions (five cases, two arms); the default is three runs per case. `--no-publish` keeps the HTML report on your machine. `--judge-model sonnet` replaces the default judge, which failed the long answers of the audit case (see below). The raw output goes to `evals/results/`, which is not committed because it holds local paths. The command-line client must be signed in (`claude auth status`); the desktop app's sign-in does not carry over.

## Results

Run on 2026-11-24 with Claude Code 2.1.275, one run per case and arm. The sessions had the tools Read, Glob, Grep and Skill, so the skill's scripts could not run; the cases test what the skill makes the agent write.

All five cases, default judge (haiku), 120 s, US$ 2.44:

| Case | With the plugin | Without |
|---|---|---|
| `abstract-no-invented-numbers` | pass | pass |
| `audit-reports-and-asks` | fail | fail |
| `conclusion-limits-once` | pass | pass |
| `intro-no-invented-citations` | pass | pass |
| `title-matches-evidence` | pass | fail |
| Suite score | 0.8 | 0.6 |

The audit case failed in both arms, although both answers listed the problems, rewrote nothing and handed the next step back. Its single grader was then split into three (`names_problems`, `no_rewrite`, `hands_back`). With the default judge all three still failed 3 of 3 votes in both arms; with `--judge-model sonnet` all three passed 3 of 3 in both arms (US$ 0.70). The failure lies in the default judge on long, table-formatted answers, not in the skill.

What the numbers say: where the request itself states the rule ("the threshold is not yet computed", "I have not given you any references"), a capable model without the skill already behaves well, and the skill adds little. The skill made the difference on the title, where the rules are its own (a noun phrase, no experiment words for a simulation, plain-text formula). Cases that leave more unsaid, and runs with the shell so that the scripts can work, are the next step.
