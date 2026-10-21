#!/usr/bin/env bash
# PreToolUse(Bash) gate: any command that runs python / Rscript / R / just run / jupyter must go through memwatch.sh.
cmd=$(jq -r '.tool_input.command // ""')
# already wrapped → allow
printf '%s' "$cmd" | grep -q 'memwatch' && exit 0
# trivial version checks → allow
printf '%s' "$cmd" | grep -Eq '^[[:space:]]*(python[0-9.]*|Rscript|R) +(--version|-V)[[:space:]]*$' && exit 0
if printf '%s' "$cmd" | grep -Eq '(^|[;&|(]|\$\()[[:space:]]*([A-Za-z_][A-Za-z0-9_]*=[^ ]*[[:space:]]+)*((time|/usr/bin/time( -l)?|nohup|env|caffeinate|(mamba|conda|micromamba) run( -n [^ ]+)?)[[:space:]]+)*([^ ;&|]*/)?(python[0-9.]*|ipython|Rscript|R|jupyter|papermill|just[[:space:]]+(run|submit))([[:space:]]|$)'; then
  jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",
    permissionDecisionReason:"BLOCKED: jobs must run under the RAM monitor. Prefix the job with  bash ~/.claude/hooks/memwatch.sh  (e.g. `... && bash ~/.claude/hooks/memwatch.sh python script.py`; for shell strings: memwatch.sh bash -c '...'). Set MEMWATCH_CAP_GB if the job needs more than the default cap (70% of RAM). Report the peak_rss line to the user when the job finishes."}}'
  exit 0
fi
exit 0
