#!/usr/bin/env bash
# Lab-Standard Stop hook — the FINISH "record what you did" guarantee.
#
# In a Lab-Standard project, if this session made SUBSTANTIVE changes (any changed
# file that is NOT a .md doc — scripts, data, figures, notebooks, configs) but did
# NOT append to WORKLOG.md, BLOCK finishing and require a log entry. Doc-only and
# WORKLOG-only edits do not trigger it. Loop-safe (honors stop_hook_active). Fails OPEN.
#
# Contract: exit 0 = allow stop; exit 2 + stderr = block (reason shown to the agent).

input="$(cat 2>/dev/null)"
# already blocked once this stop cycle -> allow, so we never loop forever
printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
root=""; d="$dir"
while [ -n "$d" ] && [ "$d" != "/" ]; do
  [ -e "$d/.labstd" ] && { root="$d"; break; }
  d="$(dirname "$d")"
done
[ -z "$root" ] && exit 0
cd "$root" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

changed="$(git status --porcelain 2>/dev/null | sed 's/^...//')"
[ -z "$changed" ] && exit 0
# substantive = any changed path that is NOT a markdown doc
substantive="$(printf '%s\n' "$changed" | grep -v '\.md$' || true)"
[ -z "$substantive" ] && exit 0

# GATE 1 — the WORKLOG must be updated when real work changed.
if ! printf '%s\n' "$changed" | grep -Eq '(^|/)WORKLOG\.md$'; then
  {
    echo "[FINISH gate] You changed files this session but did NOT update WORKLOG.md."
    echo "Append a dated entry to the project's WORKLOG.md — what you did / why / result / what's next —"
    echo "then finish. (Doc-only edits are exempt; this fires only when real work went unlogged.)"
    echo "Changed non-doc files:"
    printf '%s\n' "$substantive" | head -20
  } >&2
  exit 2
fi

# GATE 2 — the commit-gate. Substantive (non-.md) work must be COMMITTED, not just logged, so git
# stays the never-stale ground truth and every run's manifest points at code that actually exists.
# Fires only at turn-end when non-.md changes are still uncommitted (staged, unstaged, or untracked);
# a read-only turn changes nothing, so it never triggers. Doc-only turns are exempt (as above).
uncommitted_substantive="$(git status --porcelain 2>/dev/null | grep -vE '\.md$' || true)"
if [ -n "$uncommitted_substantive" ]; then
  {
    echo "[FINISH gate] Non-doc work is uncommitted — commit before finishing so git matches reality."
    echo "Commit at this logical boundary (e.g. one experiment / one coherent change), then finish."
    echo "A run's manifest.json records the commit hash; leaving code uncommitted breaks that provenance."
    echo "Uncommitted non-doc paths:"
    printf '%s\n' "$uncommitted_substantive" | sed 's/^/    /' | head -20
  } >&2
  exit 2
fi
exit 0
