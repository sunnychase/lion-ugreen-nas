#!/usr/bin/env bash
# scrub_check.sh [repo dir]  -- one-line privacy check of the working tree AND the whole git history (`git log -p`).
# Flags: IPv4 addresses outside the documentation ranges (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24; Docker's own
# default bridge 172.17.0.0/16 is also allowed, it is Docker's, not ours) and the
# loopback / unspecified / broadcast addresses; MAC addresses other than the 02:00:00:00:00:xx placeholders; e-mail
# addresses other than GitHub noreply ones; long hex strings (32+, except a published "sha256 <hex>" checksum); GitHub,
# Hugging Face, OpenAI and AWS token shapes. Add your own host, user, project and domain names in a file OUTSIDE the repository and point
# SCRUB_PRIVATE at it (one extended regex per line); that file is never committed.
# Text files only (grep -I): the media in docs/media are covered by being regenerated from text by scripts/make_reel.py.
# Prints exactly one line: "SCRUB CLEAN ..." (exit 0) or "SCRUB FOUND <n> ..." (exit 1) followed by the hits on stderr.
set -u
cd "${1:-.}" || exit 2
tmp=$(mktemp) || exit 2
trap 'rm -f "$tmp"' EXIT
{ git ls-files -z 2>/dev/null | xargs -0 grep -nHI . 2>/dev/null | sed 's/^/tree: /'
  git log -p --all 2>/dev/null | sed 's/^/history: /'; } > "$tmp"
hits=$(mktemp); trap 'rm -f "$tmp" "$hits"' EXIT
grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$tmp" | grep -vE '\b(192\.0\.2|198\.51\.100|203\.0\.113)\.[0-9]{1,3}\b|\b127\.0\.0\.1\b|\b0\.0\.0\.0\b|\b255\.255\.255\.(255|0)\b|\b172\.17\.0\.[01]\b' >> "$hits"
grep -nE "\b(Paci""fic|P[SD]T)\b" "$tmp" >> "$hits"   # time zone names (M12, M17); the words are split so this line does not match itself
grep -nEi '\b([0-9a-f]{2}:){5}[0-9a-f]{2}\b' "$tmp" | grep -vEi '\b02:00:00:00:00:[0-9a-f]{2}\b' >> "$hits"
grep -nEi '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}' "$tmp" | grep -vEi 'users\.noreply\.github\.com|noreply@anthropic\.com' >> "$hits"
grep -nE '\b[0-9a-f]{32,}\b' "$tmp" | grep -vE 'history: (index |[-+]{3} |commit |parent |tree )|sha256 [0-9a-f]{64}' >> "$hits"
grep -nE '\b(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,})' "$tmp" >> "$hits"
if [ -n "${SCRUB_PRIVATE:-}" ] && [ -r "$SCRUB_PRIVATE" ]; then grep -nEi -f "$SCRUB_PRIVATE" "$tmp" >> "$hits"; fi
n=$(sort -u "$hits" | grep -c .)
if [ "$n" -eq 0 ]; then
  echo "SCRUB CLEAN tree+history $(git rev-parse --short HEAD 2>/dev/null || echo no-commit) ($(git ls-files | wc -l) files, $(git rev-list --all --count 2>/dev/null || echo 0) commits, private list: ${SCRUB_PRIVATE:+yes}${SCRUB_PRIVATE:-none})" | sed "s#yes/[^)]*#yes#"
else
  echo "SCRUB FOUND $n line(s) in tree+history $(git rev-parse --short HEAD 2>/dev/null || echo no-commit)"
  sort -u "$hits" | cut -c1-200 >&2
  exit 1
fi
