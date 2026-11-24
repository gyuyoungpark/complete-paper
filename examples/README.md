# Examples

The examples live inside the skill, so that they are installed with it and the parts can point to them:

| Folder | What it shows | Used by |
|---|---|---|
| `skills/complete-paper/examples/supplement/` | a short manuscript with its supplement, its `suppmap.md` and the README of its data package | supplement, audit, the planted-fault cases |
| `skills/complete-paper/examples/brief/` | the brief of that manuscript | brief, audit |
| `skills/complete-paper/examples/methods/` | its reproducibility checklist `repro.md` | methods, audit |
| `skills/complete-paper/examples/figures/` | a figure before and after the figures part, and schematics drawn by code | figures |

All of them are invented: the physics, the numbers and the references are placeholders, and each file says so.

The skill has also been run once, end to end in audit-and-revise mode, on a real manuscript that is not yet published. Its outputs stay private until that paper is out; the faults that run found in the scripts are fixed and listed in `CHANGELOG.md`.
