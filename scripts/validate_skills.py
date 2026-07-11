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
  4. Self-containment: no `../` parent-directory references in SKILL.md or
     references/*.md (an ellipsis like `/mnt/.../x.png` is fine).
  5. Manifest coverage: every skill folder is listed in BOTH
     marketplace.json plugins[0].skills and plugin.json skills (and vice
     versa).
  6. Copy-sync: same-named references/*.md files that appear in more than one
     skill must be byte-identical (self-containment forces the copies; this
     stops them drifting).

Run from the repo root: python3 scripts/validate_skills.py
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", ".claude-plugin", "scripts", "node_modules"}
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def parse_frontmatter(text: str, path: Path) -> dict:
    """Minimal YAML-subset frontmatter parser: scalars (including plain
    multi-line continuations) and >- / > / | / |- block scalars."""
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        err(f"{path}: missing frontmatter block")
        return {}
    data: dict = {}
    lines = m.group(1).split("\n")
    key_re = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")
    i = 0
    while i < len(lines):
        km = key_re.match(lines[i])
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2).strip()
        i += 1
        if val in (">-", ">", "|", "|-"):
            block: list[str] = []
            while i < len(lines) and (
                lines[i].startswith("  ") or lines[i].strip() == ""
            ):
                block.append(lines[i].strip())
                i += 1
            data[key] = " ".join(b for b in block if b)
        else:
            # plain scalar — absorb indented continuation lines
            parts = [val.strip("\"'")] if val else []
            while (
                i < len(lines)
                and lines[i].startswith("  ")
                and lines[i].strip()
                and not key_re.match(lines[i])
            ):
                parts.append(lines[i].strip())
                i += 1
            data[key] = " ".join(parts)
    return data


def skill_dirs() -> list[Path]:
    """A skill is any directory containing SKILL.md (discovered, not listed)."""
    dirs = []
    for skill_md in sorted(ROOT.rglob("SKILL.md")):
        rel_parts = skill_md.relative_to(ROOT).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue
        dirs.append(skill_md.parent)
    return dirs


# Flags `../` used as a parent-directory path, not an ellipsis (`/mnt/.../x`).
PARENT_REF_RE = re.compile(r"(?<!\.)\.\./")


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

    ref_hashes: dict[str, dict[str, str]] = {}  # filename -> {skill: sha256}

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
                digest = hashlib.sha256(f.read_bytes()).hexdigest()
                ref_hashes.setdefault(f.name, {})[str(d.relative_to(ROOT))] = digest

        # self-containment
        for f in [skill_md, *(refs_dir.glob("*.md") if refs_dir.is_dir() else [])]:
            if PARENT_REF_RE.search(f.read_text(encoding="utf-8")):
                err(f"{f.relative_to(ROOT)}: contains a '../' parent-directory reference")

    # copy-sync: same-named reference docs shared across skills must not drift
    for fname, owners in sorted(ref_hashes.items()):
        if len(owners) > 1 and len(set(owners.values())) > 1:
            err(
                f"references/{fname}: copies differ across skills "
                f"({', '.join(sorted(owners))}) — sync them (self-contained "
                f"copies must stay identical)"
            )

    # manifests
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    for p in (plugin_path, market_path):
        if not p.is_file():
            err(f"{p.relative_to(ROOT)}: missing")
    if plugin_path.is_file() and market_path.is_file():
        try:
            plugin = json.loads(plugin_path.read_text())
            market = json.loads(market_path.read_text())
        except (OSError, json.JSONDecodeError) as e:
            err(f".claude-plugin: unreadable JSON ({e})")
        else:
            actual = {str(d.relative_to(ROOT)) for d in skills}
            if plugin.get("version") != version:
                err(f"plugin.json version {plugin.get('version')!r} != VERSION {version!r}")

            plugins = market.get("plugins")
            if not plugins:
                err("marketplace.json: plugins array missing/empty")
                plugins = [{}]
            if plugins[0].get("version") != version:
                err(f"marketplace.json plugins[0].version {plugins[0].get('version')!r} != VERSION {version!r}")

            for label, listed_raw in (
                ("plugin.json skills", plugin.get("skills", [])),
                ("marketplace.json plugins[0].skills", plugins[0].get("skills", [])),
            ):
                listed = {re.sub(r"^\./", "", s) for s in listed_raw}
                for missing in sorted(actual - listed):
                    err(f"{label}: skill folder {missing!r} not listed")
                for ghost in sorted(listed - actual):
                    err(f"{label}: lists {ghost!r} which has no SKILL.md")

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK — {len(skills)} skills validated at version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
