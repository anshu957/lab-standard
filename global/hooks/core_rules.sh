#!/usr/bin/env bash
# UserPromptSubmit hook: inject the 3 core rules into EVERY prompt, in every project.
# Source of truth: ~/.claude/lab-standard/global/RULES.md (versioned in the lab-standard repo).
# Fails open: missing file -> no output, exit 0. Never blocks a prompt.
f="$HOME/.claude/lab-standard/global/RULES.md"
[ -r "$f" ] && cat "$f"
exit 0
