#!/bin/bash
# rule-check.sh — deterministic rule checks on the lines a branch ADDS (lean flow, idea "turn rules into checks").
# Usage: rule-check.sh <worktree> <base> [rules.tsv]     (default rules: ~/.kiro/checks/rules.tsv)
# Output: one line per hit: <severity> <path>:<line> [<rule id>] <message> | <code>
# Exit: 1 if any error-severity hit, else 0. Bash 3.2 / BWK awk compatible.
set -u
WT=$1; BASE=$2; RULES=${3:-$HOME/.kiro/checks/rules.tsv}
[ -f "$RULES" ] || { echo "rule-check: rules file missing: $RULES" >&2; exit 2; }
ADDED=$(mktemp /tmp/rule-check-XXXX)
trap 'rm -f "$ADDED"' EXIT
# path<TAB>line<TAB>content for every added line
git -C "$WT" --no-pager diff -U0 --no-color "$BASE"...HEAD | awk '
  /^\+\+\+ / { path = substr($0, 7); if (path == "/dev/null") path = ""; next }
  /^@@ / { split($3, a, ","); line = substr(a[1], 2) + 0; next }
  /^\+/ { if (path != "") printf "%s\t%d\t%s\n", path, line, substr($0, 2); line++; next }
' > "$ADDED"
fail=0
while IFS='	' read -r id sev scope match unless msg; do
  case "$id" in ''|'#'*) continue ;; esac
  case "$scope" in
    main) P='src/main/.*\.java$' ;; test) P='src/test/' ;; java) P='\.java$' ;;
    config) P='\.(ya?ml|properties)$' ;; code) P='\.(java|ya?ml|properties)$' ;; *) P='.' ;;
  esac
  hits=$(P="$P" M="$match" U="$unless" awk -F'\t' '
    $1 ~ ENVIRON["P"] && $3 ~ ENVIRON["M"] && (ENVIRON["U"] == "-" || $3 !~ ENVIRON["U"]) {
      c = $3; sub(/^[ \t]+/, "", c); if (length(c) > 100) c = substr(c, 1, 100) "…"
      printf "%s:%s | %s\n", $1, $2, c }' "$ADDED")
  [ -z "$hits" ] && continue
  echo "$hits" | while IFS= read -r h; do
    loc=${h%% | *}; code=${h#* | }
    echo "$sev $loc [$id] $msg | $code"
  done
  [ "$sev" = error ] && fail=1
done < "$RULES"
exit $fail
