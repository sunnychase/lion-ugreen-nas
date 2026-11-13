#!/usr/bin/env bash
# nas-poweroff-gated.sh  -- run ON THE NAS (or over ssh): power off ONLY if nothing is using it. Changes nothing otherwise.
# Gates, all read-only:
#   1. no established NFS connection (port 2049)      -- a client with the share mounted keeps one open for ~90 s after use
#   2. no copy, download or index job running          -- edit the pattern to your own job names
#   3. no systemd service you name below is active    -- e.g. an indexer that rewrites a file you must not truncate
#   4. no container running                           -- `docker ps -q` empty; a failed `docker ps` counts as busy (fail safe)
# Lesson from 2026-10-16: the power-off must be INSIDE the gate's success branch. Printing "idle" and then powering off
# in a second step once cut an index job that had started in between.
set -u
JOBS_PATTERN='rsync|hf download|git clone|_fetch'
GUARD_UNITS='nas-index.service'
nfs=$(ss -Htn state established '( sport = :2049 )' | wc -l)
# (if this script's own text rides on a command line, e.g. `ssh nas 'bash -s' < this`, the pattern can match itself: that fails safe, the NAS stays on)
jobs=$(ps -eo args | grep -E "$JOBS_PATTERN" | grep -vE 'grep|nas-poweroff-gated' | wc -l)
busy=0
for u in $GUARD_UNITS; do systemctl is-active --quiet "$u" 2>/dev/null && busy=1; done
ctr=0
if command -v docker >/dev/null 2>&1; then out=$(docker ps -q 2>/dev/null) || out=BUSY; ctr=$(printf '%s' "$out" | grep -c .); fi
echo "nfs connections: $nfs | jobs: $jobs | guarded units active: $busy | containers: $ctr"
if [ "$nfs" -eq 0 ] && [ "$jobs" -eq 0 ] && [ "$busy" -eq 0 ] && [ "$ctr" -eq 0 ]; then
  echo "idle: powering off"
  sync
  sudo /usr/bin/systemctl poweroff
else
  echo "NOT idle: leaving the NAS on (nothing changed)"
  exit 1
fi
