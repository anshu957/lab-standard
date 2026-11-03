#!/usr/bin/env bash
# Lab-Standard SessionStart hook — the START "read what's been done" guarantee.
#
# In a Lab-Standard project (a dir tree with a `.labstd` marker), inject the current
# project STATE into the session's opening context so every session begins knowing
# what's already been done and what's in flight:
#   - recent git history + working-tree status  (NEVER-STALE ground truth of changes)
#   - the tail of WORKLOG.md                     (what recent sessions actually did)
#   - the CONCLUSIONS.md ledger                  (established/open/retracted findings)
# Silent outside a Lab-Standard project. Fails OPEN (never blocks a session).

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
root=""; d="$dir"
while [ -n "$d" ] && [ "$d" != "/" ]; do
  [ -e "$d/.labstd" ] && { root="$d"; break; }
  d="$(dirname "$d")"
done
[ -z "$root" ] && exit 0
cd "$root" 2>/dev/null || exit 0

echo "[project state — READ THIS before starting work]  root: $root"
echo "Before doing anything: check whether the task (or part of it) is already done below."
if git rev-parse --git-dir >/dev/null 2>&1; then
  echo "--- recent work (git log --oneline -15) ---"
  git log --oneline -15 2>/dev/null
  echo "--- uncommitted right now (git status -s) ---"
  git status -s 2>/dev/null | head -40
fi
if [ -f WORKLOG.md ]; then
  echo "--- WORKLOG.md (last 30 lines) ---"; tail -n 30 WORKLOG.md
else
  echo "(No WORKLOG.md yet — create one at the root and log what each session does.)"
fi
if [ -f CONCLUSIONS.md ]; then
  echo "--- CONCLUSIONS.md ---"; sed -n '1,90p' CONCLUSIONS.md
fi
exit 0
