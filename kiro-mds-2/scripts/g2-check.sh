#!/bin/bash
# g2-check.sh — mechanical part of the G2 code gate (lean flow). Zero tokens: the lead and the gate read only the result.
#
# Usage: g2-check.sh <work> T<n> <round> <repo>=<base> [<repo>=<base> ...]   (repos in merge order)
# Writes: <work>/T<n>/notes/g2-r<round>.md  (line 1: G2-SCRIPT: PASS|FAIL)
#         <work>/T<n>/notes/g2-r<round>-<repo>.log  (raw Maven output per repo)
# Checks: G2.1 full build + tests per repo (deps first, installed locally; Docker up when the repo uses Testcontainers),
#         G2.4 files not named in the design, G2.6 rule checks on added lines (rule-check.sh + ~/.kiro/checks/rules.tsv),
#         G2.8 internal IDs in added lines and commit messages. Everything else is the gate agent's job.
# Bash 3.2 compatible (macOS default).

set -u
if [ $# -lt 4 ]; then
  echo "usage: $0 <work> T<n> <round> <repo>=<base> [...]" >&2
  exit 64
fi
WORK=$1; TASK=$2; ROUND=$3; shift 3
T="$WORK/$TASK"
NOTES="$T/notes"
OUT="$NOTES/g2-r$ROUND.md"
mkdir -p "$NOTES"
ID_RE='(\bT[0-9]+-)?\b(TC|AC)-?[0-9]+\b|\bRV[0-9]+-[0-9]+\b|\bR[0-9]+\.[0-9]+\b|\bG[0-9]\.[0-9]+\b'
CHARTER_HOST="artifactory.se-charter.net"

DESIGN="$T/architecture.md"
[ -f "$DESIGN" ] || DESIGN="$T/overview.md"

status=PASS
heads=""
builds=""
details=""

note() { details="$details$1
"; }

java_home_for() {  # pom java version -> JDK path (steering maven-charter-cert.md)
  local v
  v=$(grep -oE '<(java\.version|maven\.compiler\.release|release)>[0-9]+' "$1/pom.xml" 2>/dev/null | head -1 | grep -oE '[0-9]+$')
  if [ -n "$v" ] && [ -d "/Library/Java/JavaVirtualMachines/jdk-$v.jdk/Contents/Home" ]; then
    echo "/Library/Java/JavaVirtualMachines/jdk-$v.jdk/Contents/Home"
  else
    echo "${JAVA_HOME:-}"
  fi
}

charter_truststore() {  # per-JDK trust store with the Charter cert, no sudo
  local jh=$1 key store cert
  key=$(echo "$jh" | sed 's#[/ ]#_#g')
  store="/tmp/charter-ssl/$key/cacerts"
  mkdir -p "$(dirname "$store")"
  if [ ! -f "$store" ]; then cp "$jh/lib/security/cacerts" "$store" && chmod u+w "$store"; fi
  if ! "$jh/bin/keytool" -list -alias secharter -keystore "$store" -storepass changeit >/dev/null 2>&1; then
    cert=$(mktemp /tmp/secharter-XXXX.crt)
    openssl s_client -connect "${CHARTER_HOST}:443" </dev/null 2>/dev/null \
      | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > "$cert"
    "$jh/bin/keytool" -importcert -alias secharter -keystore "$store" -file "$cert" -storepass changeit -noprompt >/dev/null 2>&1
    rm -f "$cert"
  fi
  echo "$store"
}

for spec in "$@"; do
  repo=${spec%%=*}; base=${spec#*=}
  wt="$WORK/wt/$TASK/$repo"
  if [ ! -d "$wt" ]; then
    status=FAIL; note "- $repo: worktree missing ($wt)"; continue
  fi
  git -C "$wt" fetch -q origin 2>/dev/null
  sha=$(git -C "$wt" rev-parse --short HEAD)
  heads="$heads $repo@$sha"

  # Testcontainers needs Docker: fail fast instead of a 10-minute red build
  if grep -rqsi testcontainers "$wt/pom.xml" "$wt/src/test" 2>/dev/null && ! docker info >/dev/null 2>&1; then
    status=FAIL
    builds="$builds- $repo @ $sha: NOT BUILT — repo uses Testcontainers and Docker is not running (start Docker Desktop, re-run)
"
    continue
  fi

  # G2.1 build + tests
  if [ -f "$wt/pom.xml" ]; then
    log="$NOTES/g2-r$ROUND-$repo.log"
    jh=$(java_home_for "$wt")
    mvn_cmd=mvn; [ -x "$wt/mvnw" ] && mvn_cmd=./mvnw
    extra=""
    if grep -q "$CHARTER_HOST" "$wt/pom.xml" "$HOME/.m2/settings.xml" 2>/dev/null && [ -n "$jh" ]; then
      store=$(charter_truststore "$jh")
      extra="-Djavax.net.ssl.trustStore=$store -Djavax.net.ssl.trustStorePassword=changeit"
    fi
    echo "▶ $repo @ $sha: $mvn_cmd -B clean install (log: $log)"
    start=$(date +%s)
    # install, so later repos in the merge order build against this change
    (cd "$wt" && JAVA_HOME="$jh" $mvn_cmd -B $extra clean install) > "$log" 2>&1
    rc=$?
    secs=$(( $(date +%s) - start ))
    summary=$(grep -E 'Tests run: [0-9]+, Failures: [0-9]+, Errors: [0-9]+, Skipped: [0-9]+$' "$log" | tail -1 | sed 's/.*Tests run/Tests run/')
    [ -n "$summary" ] || summary="Tests run: none found"
    if [ $rc -eq 0 ] && grep -q "BUILD SUCCESS" "$log"; then result="BUILD SUCCESS"; else result="BUILD FAILURE"; status=FAIL; fi
    line="$repo @ $sha: $result — $summary ($((secs / 60))m$((secs % 60))s)"
    echo "$line"
    builds="$builds- $line
"
    if [ "$result" = "BUILD FAILURE" ]; then
      note "- $repo: build failed. Last errors:"
      details="$details$(grep -E '^\[ERROR\]' "$log" | head -15 | sed 's/^/    /')
"
    fi
  else
    builds="$builds- $repo @ $sha: no pom.xml, no build (config repo)
"
  fi

  # G2.4 files not named in the design
  changed=$(git -C "$wt" --no-pager diff --name-only "$base"...HEAD)
  unnamed=""
  for f in $changed; do
    b=$(basename "$f")
    case "$b" in CHANGELOG.md|pom.xml) continue ;; esac
    if ! grep -qF -- "$b" "$DESIGN" 2>/dev/null && ! grep -qF -- "$f" "$DESIGN" 2>/dev/null; then
      unnamed="$unnamed    - $f
"
    fi
  done
  stat=$(git -C "$wt" --no-pager diff --stat "$base"...HEAD | tail -1)
  note "- $repo diff: $stat"
  if [ -n "$unnamed" ]; then
    note "  Files not named in $(basename "$DESIGN") (gate checks G2.4):"
    details="$details$unnamed"
  fi

  # G2.6 rule checks (added lines only)
  rules_out=$("$(dirname "$0")/rule-check.sh" "$wt" "$base")
  rc_rules=$?
  if [ -n "$rules_out" ]; then
    note "  Rule checks (G2.6; error = FAIL, warn = gate judges):"
    details="$details$(echo "$rules_out" | sed 's/^/    /')
"
  fi
  [ $rc_rules -eq 1 ] && status=FAIL
  [ $rc_rules -eq 2 ] && note "  Rule checks NOT run: rules file missing (gate checks G2.6 by hand)"

  # G2.8 internal IDs in added lines and commit messages
  hits=$(git -C "$wt" --no-pager diff "$base"...HEAD | grep -E '^\+[^+]' | grep -nE "$ID_RE" | head -10)
  mhits=$(git -C "$wt" --no-pager log --format=%B "$base"..HEAD | grep -nE "$ID_RE" | head -10)
  if [ -n "$hits$mhits" ]; then
    status=FAIL
    note "  Internal IDs found (G2.8):"
    [ -n "$hits" ] && details="$details$(echo "$hits" | sed 's/^/    diff: /')
"
    [ -n "$mhits" ] && details="$details$(echo "$mhits" | sed 's/^/    commit msg: /')
"
  fi
done

{
  echo "G2-SCRIPT: $status"
  echo "Head:$heads"
  echo "Round: $ROUND | Run: $(date '+%Y-%m-%d %H:%M')"
  echo
  echo "## Builds (G2.1)"
  printf '%s' "$builds"
  echo
  echo "## Checks (G2.4, G2.6, G2.8)"
  printf '%s' "$details"
} > "$OUT"

echo "G2-SCRIPT: $status -> $OUT"
[ "$status" = PASS ]
