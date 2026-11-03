#!/usr/bin/env bash
# Lab-Standard UserPromptSubmit hook.
#
# On EVERY prompt, inside a Lab-Standard project (a dir tree containing a `.labstd`
# marker), inject the project's CONCLUSIONS.md ledger + the grounding rule into the
# turn's context. This makes the established/open/retracted conclusions physically
# present every turn, so they can't drift out of attention over a long session and
# contradicting one becomes glaring. Silent (exit 0, no output) outside a
# Lab-Standard project. Fails OPEN — it must never block a prompt.
#
# Contract: stdout is added to the model's context for this turn; exit 0 always.

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
root=""
d="$dir"
while [ -n "$d" ] && [ "$d" != "/" ]; do
  if [ -e "$d/.labstd" ]; then root="$d"; break; fi
  d="$(dirname "$d")"
done
[ -z "$root" ] && exit 0   # not a Lab-Standard project -> stay silent

echo "[grounding — Lab Standard] Reconcile with the ledger below BEFORE you assert or act this turn:"
echo "- Do NOT contradict an Established conclusion without flagging it and re-deriving from evidence"
echo "  (if evidence overturns it, move it to Retracted THIS turn)."
echo "- State established facts before new interpretation; mark new interpretation as tentative."
echo "- Reached or overturned a conclusion? Update CONCLUSIONS.md the same turn."
if [ -f "$root/CONCLUSIONS.md" ]; then
  echo "----- $root/CONCLUSIONS.md (ledger; truncated at 90 lines) -----"
  sed -n '1,90p' "$root/CONCLUSIONS.md"
else
  echo "(No CONCLUSIONS.md at the project root yet — create one: '## Established / ## Open / ## Retracted'.)"
fi
exit 0
