# Releasing

One push of the repository reaches most places where the skill is listed. Three things need a step for every version: the version number, the GitHub release, and any registry that takes uploads. The first two are automated.

## Every release

1. List the changes under `## [Unreleased]` in `CHANGELOG.md`.
2. Set the new version everywhere and date the changelog section:

   ```
   python tools/version.py bump 0.2.0
   ```

   This writes the version into `.claude-plugin/plugin.json` and the metadata of `skills/complete-paper/SKILL.md`, and turns `## [Unreleased]` into `## [0.2.0] - <today>` with a new, empty `[Unreleased]` above it. It refuses a lower or already released version, and an `[Unreleased]` section that lists nothing. For the first release, run it with the current version (`bump 0.1.0`).
3. Commit, tag and push:

   ```
   git commit -am "Release v0.2.0"
   git tag v0.2.0
   git push origin HEAD --tags
   ```

4. The tag starts `.github/workflows/release.yml`. It checks that the tag, both version files and the changelog agree (`python tools/version.py check v0.2.0`), runs the tests, builds `dist/complete-paper.skill` and publishes a GitHub release with that file and the changelog section as its notes.

Raising the version is not optional. Claude Code delivers a plugin update only when the version in `plugin.json` changes; commits pushed under an unchanged version stay invisible to users who installed the plugin.

## Where the release goes by itself

| Place | How it gets the new version |
|---|---|
| GitHub | the push and the release above |
| skills.sh and `npx skills add gyuyoungpark/complete-paper` | new installs fetch the repository's current contents; users who installed earlier run `npx skills update` |
| Claude Code, through this repository's marketplace | users run `/plugin marketplace update complete-paper`, or turn on auto-update for the marketplace under `/plugin`; it is off by default |
| Anthropic's plugin directory (after an accepted submission at claude.ai/directory/manage) | the directory follows the branch or tag set at submission, checks each new commit and publishes it; no new submission |
| Directories that crawl GitHub (for example SkillsMP) | their next crawl |
| Claude app | users download `complete-paper.skill` from the new release |

## Places that need an upload

- **ClawHub**, if the skill is listed there: `clawhub skill publish ./skills/complete-paper --version 0.2.0` with the same version.
- **Directories with a manual upload** (for example skillhub.club): upload `skills/complete-paper/SKILL.md` and the folder again.

## Check before tagging

```
python tools/version.py check
python -m unittest discover -s tests
claude plugin validate .
```
