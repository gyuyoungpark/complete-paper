"""Keep the version of complete-paper in one state across the files that carry it, and cut releases.

The version lives in two files: .claude-plugin/plugin.json ("version") and skills/complete-paper/SKILL.md
(metadata: version). Claude Code delivers a plugin update only when plugin.json's version changes, so every
release raises it. CHANGELOG.md collects changes under "## [Unreleased]" until a release names them.

Usage:
    python tools/version.py show                 the current version (fails if the two files disagree)
    python tools/version.py bump 0.2.0           set both files to 0.2.0 and turn "## [Unreleased]" into
                                                 "## [0.2.0] - <today>", with a new empty [Unreleased] above
    python tools/version.py bump 0.2.0 --date 2026-12-01
    python tools/version.py check [v0.2.0]       the two files agree, CHANGELOG has the section, the tag matches
    python tools/version.py notes 0.2.0          print the CHANGELOG section of 0.2.0 (the release notes)

The release workflow (.github/workflows/release.yml) runs check and notes when a tag v<version> is pushed.
Standard library only. Exit status 1 on any mismatch.
"""
import argparse
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, ".claude-plugin", "plugin.json")
SKILL = os.path.join(ROOT, "skills", "complete-paper", "SKILL.md")
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
SKILL_VERSION = re.compile(r'^(  version: ")([^"]*)(")\s*$', re.M)
UNRELEASED = "## [Unreleased]"


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def parse(v):
    m = SEMVER.match(v)
    if not m:
        sys.exit(f"version: '{v}' is not of the form MAJOR.MINOR.PATCH")
    return tuple(int(x) for x in m.groups())


def versions():
    plugin = json.loads(read(PLUGIN)).get("version")
    m = SKILL_VERSION.search(read(SKILL))
    return plugin, (m.group(2) if m else None)


def current():
    plugin, skill = versions()
    if plugin != skill:
        sys.exit(f"version: plugin.json says {plugin!r} and SKILL.md says {skill!r}; run bump to set both")
    return plugin


def section(text, v):
    """The body of the CHANGELOG section '## [v]' (without its heading), or None."""
    m = re.search(r"^## \[" + re.escape(v) + r"\][^\n]*\n", text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"^## \[", rest, re.M)
    return (rest[:nxt.start()] if nxt else rest).strip("\r\n")


def cmd_show(_):
    print(current())


def cmd_bump(a):
    new, old = a.version, current()
    if parse(new) < parse(old):
        sys.exit(f"version: {new} is lower than the current {old}")
    log = read(CHANGELOG)
    if section(log, new) is not None:
        sys.exit(f"version: CHANGELOG.md already has a section for {new}")
    if parse(new) == parse(old) and section(log, old) is not None:
        sys.exit(f"version: {new} is already released; choose a higher version")
    if UNRELEASED not in log:
        sys.exit(f"version: CHANGELOG.md has no '{UNRELEASED}' section to release")
    body = section(log, "Unreleased") or ""
    if not re.search(r"^\s*-\s+\S", body, re.M) and not a.allow_empty:
        sys.exit("version: the [Unreleased] section lists no change; add one, or pass --allow-empty")
    date = a.date or datetime.date.today().isoformat()
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        sys.exit(f"version: date '{date}' is not YYYY-MM-DD")
    nl = "\r\n" if "\r\n" in log else "\n"
    log = log.replace(UNRELEASED, f"{UNRELEASED}{nl}{nl}## [{new}] - {date}", 1)
    plugin = read(PLUGIN)
    plugin, n = re.subn(r'("version"\s*:\s*")[^"]*(")', r"\g<1>" + new + r"\g<2>", plugin, count=1)
    if n != 1:
        sys.exit("version: no version field in plugin.json")
    skill, n = SKILL_VERSION.subn(r"\g<1>" + new + r"\g<3>", read(SKILL), count=1)
    if n != 1:
        sys.exit("version: no 'version:' line in the SKILL.md metadata")
    write(PLUGIN, plugin)
    write(SKILL, skill)
    write(CHANGELOG, log)
    print(f"version: {old} -> {new} (plugin.json, SKILL.md, CHANGELOG.md section dated {date})")
    print("next:")
    print(f'  git commit -am "Release v{new}"')
    print(f"  git tag v{new}")
    print("  git push origin HEAD --tags")


def cmd_check(a):
    plugin, skill = versions()
    problems = []
    if plugin != skill:
        problems.append(f"plugin.json says {plugin!r}, SKILL.md says {skill!r}")
    if plugin and not SEMVER.match(plugin):
        problems.append(f"plugin.json version {plugin!r} is not MAJOR.MINOR.PATCH")
    if a.tag:
        tag = a.tag[1:] if a.tag.startswith("v") else a.tag
        if tag != plugin:
            problems.append(f"tag {a.tag} does not match the version {plugin}: run bump {tag} before tagging")
        if section(read(CHANGELOG), tag) is None:
            problems.append(f"CHANGELOG.md has no section '## [{tag}]'")
    for p in problems:
        print("check:", p)
    if problems:
        sys.exit(1)
    print(f"check: version {plugin} is consistent" + (f" with tag {a.tag}" if a.tag else ""))


def cmd_notes(a):
    body = section(read(CHANGELOG), a.version)
    if body is None:
        sys.exit(f"version: CHANGELOG.md has no section for {a.version}")
    print(body.replace("\r\n", "\n"))


def main():
    try:  # print non-ASCII text when output is piped on Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Version and release helper for complete-paper.")
    ap.add_argument("--root", default=ROOT, help="repository root (default: the folder above tools/)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show", help="print the current version").set_defaults(func=cmd_show)
    b = sub.add_parser("bump", help="set a new version in every file and date the CHANGELOG section")
    b.add_argument("version")
    b.add_argument("--date", help="release date, YYYY-MM-DD (default: today)")
    b.add_argument("--allow-empty", action="store_true", help="release even if [Unreleased] lists nothing")
    b.set_defaults(func=cmd_bump)
    c = sub.add_parser("check", help="check that the files, the CHANGELOG and an optional tag agree")
    c.add_argument("tag", nargs="?")
    c.set_defaults(func=cmd_check)
    n = sub.add_parser("notes", help="print the CHANGELOG section of a version")
    n.add_argument("version")
    n.set_defaults(func=cmd_notes)
    a = ap.parse_args()
    global PLUGIN, SKILL, CHANGELOG
    PLUGIN = os.path.join(a.root, ".claude-plugin", "plugin.json")
    SKILL = os.path.join(a.root, "skills", "complete-paper", "SKILL.md")
    CHANGELOG = os.path.join(a.root, "CHANGELOG.md")
    a.func(a)


if __name__ == "__main__":
    main()
