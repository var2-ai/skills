#!/usr/bin/env python3
"""Validate the var2-ai/skills package.

Checks (mirrors CONTRIBUTING.md / CLAUDE.md):
  1. Every skill's SKILL.md has frontmatter with:
     - name  == its directory name
     - version == VERSION (single source of truth)
     - description: non-empty, <=1024 chars, contains "Use when" and "NOT for"
  2. Version sync: VERSION == every SKILL.md version
     == .claude-plugin/plugin.json version
     == .claude-plugin/marketplace.json plugins[0].version
  3. References contract: every references/*.md is linked from its SKILL.md,
     and every `references/...` link in SKILL.md resolves to a file.
  4. Self-containment: no `../` references in SKILL.md or references/*.md.
  5. Marketplace coverage: every skill folder is listed in
     marketplace.json plugins[0].skills (and vice versa).

Run from the repo root: python3 scripts/validate_skills.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def parse_frontmatter(text: str, path: Path) -> dict:
    """Minimal YAML-subset frontmatter parser: scalars and >- folded blocks."""
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        err(f"{path}: missing frontmatter block")
        return {}
    data: dict = {}
    lines = m.group(1).split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        km = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if km:
            key, val = km.group(1), km.group(2).strip()
            if val in (">-", ">", "|", "|-"):
                block: list[str] = []
                i += 1
                while i < len(lines) and (
                    lines[i].startswith("  ") or lines[i].strip() == ""
                ):
                    block.append(lines[i].strip())
                    i += 1
                data[key] = " ".join(b for b in block if b)
                continue
            data[key] = val.strip("\"'")
        i += 1
    return data


def skill_dirs() -> list[Path]:
    dirs = []
    for pattern in ("var2-*", "skills/*"):
        for d in sorted(ROOT.glob(pattern)):
            if d.is_dir() and (d / "SKILL.md").is_file():
                dirs.append(d)
    return dirs


def main() -> int:
    version_file = ROOT / "VERSION"
    if not version_file.is_file():
        print("FATAL: VERSION file missing")
        return 1
    version = version_file.read_text().strip()
    if not version:
        err("VERSION: empty")

    skills = skill_dirs()
    if not skills:
        err("no skill directories found")

    for d in skills:
        skill_md = d / "SKILL.md"
        rel = skill_md.relative_to(ROOT)
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text, rel)

        if fm.get("name") != d.name:
            err(f"{rel}: frontmatter name {fm.get('name')!r} != directory name {d.name!r}")
        if fm.get("version") != version:
            err(f"{rel}: frontmatter version {fm.get('version')!r} != VERSION {version!r}")
        desc = fm.get("description", "")
        if not desc:
            err(f"{rel}: description missing/empty")
        else:
            if len(desc) > 1024:
                err(f"{rel}: description is {len(desc)} chars (max 1024)")
            if "Use when" not in desc:
                err(f"{rel}: description lacks a 'Use when' trigger phrase")
            if "NOT for" not in desc:
                err(f"{rel}: description lacks a 'NOT for' boundary")

        # references contract
        linked = set(re.findall(r"references/[\w.\-]+\.md", text))
        for link in linked:
            if not (d / link).is_file():
                err(f"{rel}: dead link {link}")
        refs_dir = d / "references"
        if refs_dir.is_dir():
            for f in sorted(refs_dir.glob("*.md")):
                ref = f"references/{f.name}"
                if ref not in linked:
                    err(f"{rel}: orphan reference {ref} (not linked from SKILL.md)")

        # self-containment
        for f in [skill_md, *(refs_dir.glob("*.md") if refs_dir.is_dir() else [])]:
            if "../" in f.read_text(encoding="utf-8"):
                err(f"{f.relative_to(ROOT)}: contains a '../' parent-directory reference")

    # manifests
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    for p in (plugin_path, market_path):
        if not p.is_file():
            err(f"{p.relative_to(ROOT)}: missing")
    if not errors or (plugin_path.is_file() and market_path.is_file()):
        try:
            plugin = json.loads(plugin_path.read_text())
            market = json.loads(market_path.read_text())
        except (OSError, json.JSONDecodeError) as e:
            err(f".claude-plugin: unreadable JSON ({e})")
        else:
            if plugin.get("version") != version:
                err(f"plugin.json version {plugin.get('version')!r} != VERSION {version!r}")
            plugins = market.get("plugins") or [{}]
            if plugins[0].get("version") != version:
                err(f"marketplace.json plugins[0].version {plugins[0].get('version')!r} != VERSION {version!r}")
            listed = {re.sub(r"^\./", "", s) for s in plugins[0].get("skills", [])}
            actual = {str(d.relative_to(ROOT)) for d in skills}
            for missing in sorted(actual - listed):
                err(f"marketplace.json: skill folder {missing!r} not listed in plugins[0].skills")
            for ghost in sorted(listed - actual):
                err(f"marketplace.json: plugins[0].skills lists {ghost!r} which has no SKILL.md")

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK — {len(skills)} skills validated at version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
