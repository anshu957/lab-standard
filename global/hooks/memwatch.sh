#!/usr/bin/env bash
# memwatch — run a job while watching RAM. Kills it before it can crash the machine.
# Usage: memwatch.sh <command> [args...]        (wrap shell strings as: memwatch.sh bash -c '...')
# Env:   MEMWATCH_CAP_GB  (default 70% of physical RAM)  kill if the job's process-tree RSS exceeds this
#        MEMWATCH_MIN_FREE_GB (default 1) kill if system available memory drops below this
#        MEMWATCH_INTERVAL (default 2 s)
# Prints a RAM line every 30 s and a final summary (peak RSS, wall time, exit code);
# appends the summary to ~/.claude/memwatch.log.
if [ "$(uname)" = Darwin ]; then total_kb=$(( $(sysctl -n hw.memsize) / 1024 ))
else total_kb=$(awk '/MemTotal/{print $2}' /proc/meminfo); fi
CAP_GB=${MEMWATCH_CAP_GB:-$(awk -v k="$total_kb" 'BEGIN{printf "%.1f", 0.7*k/1048576}')}
MIN_FREE_GB=${MEMWATCH_MIN_FREE_GB:-1}
INT=${MEMWATCH_INTERVAL:-2}
LOG="$HOME/.claude/memwatch.log"
[ $# -eq 0 ] && { echo "memwatch: no command given" >&2; exit 2; }

cap_kb=$(awk -v g="$CAP_GB" 'BEGIN{printf "%d", g*1048576}')
minfree_kb=$(awk -v g="$MIN_FREE_GB" 'BEGIN{printf "%d", g*1048576}')

tree_rss_kb() {  # RSS (KB) of $1 and all its descendants
  ps -Ao pid=,ppid=,rss= | awk -v root="$1" '
    {pp[$1]=$2; r[$1]=$3}
    END{ for (p in pp) { q=p; while (q!="" && q!=0 && q!=1) { if (q==root) {s+=r[p]; break}; q=pp[q] } } print s+0 }'
}
avail_kb() {  # macOS: free + inactive + purgeable + speculative pages; Linux: MemAvailable
  if [ "$(uname)" = Darwin ]; then
    vm_stat | awk -v ps="$(sysctl -n hw.pagesize)" '/Pages (free|inactive|purgeable|speculative)/{gsub(/\./,"",$NF); s+=$NF} END{printf "%d", s*ps/1024}'
  else awk '/MemAvailable/{print $2}' /proc/meminfo; fi
}
kill_tree() {
  local pids; pids=$(ps -Ao pid=,ppid= | awk -v root="$1" '{pp[$1]=$2} END{for(p in pp){q=p; while(q!=""&&q!=0&&q!=1){if(q==root){print p;break};q=pp[q]}}}')
  kill -TERM $pids 2>/dev/null; sleep 3; kill -KILL $pids 2>/dev/null
}

start=$(date +%s)
echo "[memwatch] start $(date '+%F %T') cap=${CAP_GB}GB min_free=${MIN_FREE_GB}GB avail=$(( $(avail_kb)/1048576 ))GB :: $*"
"$@" &
pid=$!
trap 'kill_tree $pid; exit 130' INT TERM
peak=0; killed=""; n=0
while kill -0 "$pid" 2>/dev/null; do
  rss=$(tree_rss_kb "$pid"); av=$(avail_kb)
  [ "$rss" -gt "$peak" ] && peak=$rss
  if [ "$rss" -gt "$cap_kb" ]; then killed="RSS $((rss/1024)) MB > cap ${CAP_GB} GB"; fi
  if [ "$av" -lt "$minfree_kb" ]; then killed="system available $((av/1024)) MB < ${MIN_FREE_GB} GB"; fi
  if [ -n "$killed" ]; then echo "[memwatch] KILLING job: $killed" >&2; kill_tree "$pid"; break; fi
  n=$((n+1)); if [ $((n*INT % 30)) -lt "$INT" ]; then echo "[memwatch] t=$(( $(date +%s)-start ))s rss=$((rss/1024))MB peak=$((peak/1024))MB avail=$((av/1024))MB"; fi
  sleep "$INT"
done
wait "$pid"; rc=$?
[ -n "$killed" ] && rc=137
summary="[memwatch] done rc=$rc peak_rss=$((peak/1024))MB wall=$(( $(date +%s)-start ))s${killed:+ KILLED($killed)} :: $*"
echo "$summary"
echo "$(date '+%F %T') $PWD $summary" >> "$LOG"
exit $rc
