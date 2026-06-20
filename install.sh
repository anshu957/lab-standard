#!/usr/bin/env bash
# Wire the Lab Standard's global pieces into ~/.claude on THIS machine. Idempotent.
#
# What it touches (all under ~/.claude):
#   - copies global/skills/{new-project,new-experiment} -> ~/.claude/skills/   (overwrites those two)
#   - copies global/hooks/guard_paths.py               -> ~/.claude/hooks/     (overwrites it)
#   - inserts/refreshes a marked block in              ~/.claude/CLAUDE.md     (backup made)
#   - merges the PreToolUse hook into                  ~/.claude/settings.json (backup made)
# Backups are written next to the originals as *.bak-<timestamp>. Re-run after `git pull` to update.
set -euo pipefail

LSTD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CL="$HOME/.claude"
TS="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$CL/skills" "$CL/hooks"

echo "[lab-standard] installing skills + hook..."
cp -r "$LSTD/global/skills/new-project"    "$CL/skills/"
cp -r "$LSTD/global/skills/new-experiment" "$CL/skills/"
cp    "$LSTD/global/hooks/guard_paths.py"  "$CL/hooks/"
chmod +x "$CL/hooks/guard_paths.py"

echo "[lab-standard] refreshing CLAUDE.md block..."
python3 - "$CL/CLAUDE.md" "$LSTD/global/CLAUDE.snippet.md" "$TS" <<'PY'
import sys, pathlib, re
claude_md, snippet_path, ts = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(claude_md)
snippet = pathlib.Path(snippet_path).read_text().strip("\n")
existing = p.read_text() if p.exists() else ""
if existing:
    pathlib.Path(claude_md + f".bak-{ts}").write_text(existing)
pat = re.compile(r"<!-- LAB-STANDARD:BEGIN.*?LAB-STANDARD:END -->", re.S)
new = pat.sub(snippet, existing) if pat.search(existing) else (existing.rstrip() + "\n\n" + snippet + "\n")
p.write_text(new)
print("  CLAUDE.md updated")
PY

echo "[lab-standard] merging hook into settings.json..."
python3 - "$CL/settings.json" "$LSTD/global/settings.fragment.json" "$TS" <<'PY'
import sys, json, pathlib
settings_path, frag_path, ts = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(settings_path)
settings = json.loads(p.read_text()) if p.exists() else {}
if p.exists():
    pathlib.Path(settings_path + f".bak-{ts}").write_text(p.read_text())
frag = json.loads(pathlib.Path(frag_path).read_text())
entry = frag["hooks"]["PreToolUse"][0]
cmd = entry["hooks"][0]["command"]
hooks = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
already = any(h.get("command") == cmd for e in hooks for h in e.get("hooks", []))
if already:
    print("  guard hook already present — skipped")
else:
    hooks.append(entry)
    p.write_text(json.dumps(settings, indent=2) + "\n")
    print("  guard hook added")
PY

echo "[lab-standard] done. Restart Claude Code sessions to pick up the changes."
