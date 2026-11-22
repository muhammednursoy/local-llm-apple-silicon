#!/bin/zsh
set -u
R="${0:A:h}"
H="$R/../harness"
O=~/.opencode/bin/opencode
OUT="$R/results/coding"
FIX="$R/coding-fixture"
PROMPT='The tests in tests/test_summary.py fail in this project. Make them pass by adding a monthly_summary(records, year, month) function to the expenses.report module and a --month YYYY-MM option to the command line. Do not change the tests. When you are done, run all tests with python3 -m unittest and show the result.'

run_with_limit() {
  local limit=$1; shift
  "$@" &
  local pid=$!
  ( sleep $limit; kill $pid 2>/dev/null ) >/dev/null 2>&1 </dev/null &
  local watcher=$!
  wait $pid; local rc=$?
  kill $watcher 2>/dev/null
  return $rc
}

mkdir -p "$OUT"
for model in "$@"; do
  pmset -g batt | grep -q "AC Power" || { print "not on AC power, stopped: $model"; exit 1; }
  slug=${model//[:\/]/-}${RUN_SUFFIX:-}
  W=$(mktemp -d /tmp/oc-coding.XXXX)
  cp -R "$FIX/." "$W/"
  t0=$(date +%s)
  (cd "$W" && run_with_limit 900 env OPENCODE_CONFIG="$H/opencode-minimal.json" OPENCODE_DISABLE_CLAUDE_CODE=1 \
    "$O" run "$PROMPT" --model "ollama/$model" --agent local 2>&1 | sed 's/\x1b\[[0-9;]*m//g') > "$OUT/$slug.log"
  t1=$(date +%s)
  find "$W" -name __pycache__ -prune -exec rm -rf {} +
  {
    print -r -- "model: $model"
    print -r -- "duration_s: $((t1 - t0))"
    print -r -- "workdir: $W"
    print -r -- "--- changed files (vs fixture):"
    diff -rq "$FIX" "$W" | sed "s|$FIX|fixture|; s|$W|workdir|"
    print -r -- "--- tests changed:"
    diff -r "$FIX/tests" "$W/tests" >/dev/null && print "no" || print "YES"
    print -r -- "--- independent test run:"
    (cd "$W" && python3 -m unittest 2>&1 | tail -15)
    print -r -- "--- code diff:"
    diff -ru "$FIX/expenses" "$W/expenses" | sed "s|$FIX|fixture|; s|$W|workdir|"
  } > "$OUT/$slug.check.txt" 2>&1
  print -r -- "$model: $((t1 - t0)) s, $(grep -E '^(OK|FAILED)' "$OUT/$slug.check.txt" | tail -1)"
  ollama stop "$model" >/dev/null 2>&1; sleep 3
done
