#!/bin/zsh
set -u
H="${0:A:h}"
O=~/.opencode/bin/opencode
OUT="$H/smoke-$(date +%Y%m%d-%H%M).md"
PROMPTS=(
  'Write a file named hello.py that takes a name and prints "Hello, <name>!". Then run python3 hello.py Alice and show the output.'
  'Read hello.py. Change it so that it prints "Hello, world!" when no name is given. Run both cases and show the output.'
  'Which packages are in requirements.txt? Do not guess, look.'
)

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

for model in "$@"; do
  W=$(mktemp -d /tmp/oc-smoke.XXXX)
  print -r -- "## $model ($W)" >> "$OUT"
  for i in {1..3}; do
    typeset -a cont=()
    (( i > 1 )) && cont=(--continue)
    t0=$(date +%s)
    reply=$(cd "$W" && run_with_limit 600 env OPENCODE_CONFIG="$H/opencode-minimal.json" OPENCODE_DISABLE_CLAUDE_CODE=1 \
      "$O" run "${PROMPTS[$i]}" --model "ollama/$model" --agent local "${cont[@]}" 2>&1 | sed 's/\x1b\[[0-9;]*m//g')
    t1=$(date +%s)
    print -r -- "### Prompt $i ($((t1 - t0)) s)" >> "$OUT"
    print -r -- "> ${PROMPTS[$i]}" >> "$OUT"
    print -r -- '```' >> "$OUT"; print -r -- "$reply" | tail -40 >> "$OUT"; print -r -- '```' >> "$OUT"
    print -r -- "$model prompt $i: $((t1 - t0)) s"
  done
  print -r -- "### Independent check" >> "$OUT"
  print -r -- '```' >> "$OUT"
  { ls -la "$W"; print -- "--- hello.py:"; cat "$W/hello.py" 2>&1; print -- "--- python3 hello.py Alice:"; (cd "$W" && python3 hello.py Alice 2>&1 </dev/null);
    print -- "--- python3 hello.py:"; (cd "$W" && python3 hello.py 2>&1 </dev/null); } >> "$OUT" 2>&1
  print -r -- '```' >> "$OUT"
  ollama stop "$model" >/dev/null 2>&1; sleep 3
done
print -r -- "result: $OUT"
