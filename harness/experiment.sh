#!/bin/zsh
set -u
H="${0:A:h}"
O=~/.opencode/bin/opencode
LOG=~/.ollama/logs/server.log
MODEL="qwen3.6:35b-a3b-q4_K_M"
MSG="${MSG:-hi, how are you}"
OUT="$H/result-$(date +%Y%m%d-%H%M).tsv"
WORK=$(mktemp -d /tmp/oc-experiment.XXXX)

print -r -- "variant	power	powermode	total_s	prompt_tokens	prefill_s	prefill_tok_s	gen_tokens	decode_tok_s	reply" > "$OUT"

run_variant() {
  local name=$1 cfg=$2; shift 2
  ollama stop "$MODEL" >/dev/null 2>&1; sleep 3
  local start_line=$(wc -l < "$LOG")
  local t0=$(date +%s)
  local reply
  local -a agentargs=()
  [[ -n $AGENT ]] && agentargs=(--agent "$AGENT")
  reply=$(cd "$WORK" && env OPENCODE_CONFIG="$cfg" "$@" "$O" run "$MSG" --model "ollama/$MODEL" "${agentargs[@]}" 2>/dev/null | tr '\n' ' ' | cut -c1-160)
  local t1=$(date +%s)
  local stats=$(tail -n +$((start_line + 1)) "$LOG" | /opt/homebrew/bin/python3.11 -I -c '
import re, sys
big = None
for line in sys.stdin:
    m = re.search(r"task (\d+) \| prompt eval time = +([\d.]+) ms / +(\d+) tokens", line)
    if m:
        cur = {"task": m.group(1), "pms": float(m.group(2)), "ptok": int(m.group(3))}
        if big is None or cur["ptok"] > big["ptok"]:
            big = cur
        last_task = m.group(1)
    m = re.search(r"task (\d+) \| +eval time = +([\d.]+) ms / +(\d+) tokens", line)
    if m and big and m.group(1) == big["task"]:
        big["ems"], big["etok"] = float(m.group(2)), int(m.group(3))
if not big:
    print("\t".join(["?"] * 5)); sys.exit()
print("\t".join(str(x) for x in [big["ptok"], round(big["pms"] / 1000, 1), round(big["ptok"] / big["pms"] * 1000), big.get("etok", "?"), round(big["etok"] / big["ems"] * 1000, 1) if big.get("ems") else "?"]))
')
  local power=$(pmset -g batt | grep -q "AC Power" && echo ac || echo battery)
  local pm=$(pmset -g | awk '/powermode/ {print $2}')
  print -r -- "$name	$power	$pm	$((t1 - t0))	$stats	$reply" >> "$OUT"
  print -r -- "== $name: $((t1 - t0)) s | $stats | $reply"
}

AGENT=local run_variant "1-minimal-agent+claude-off" "$H/opencode-minimal.json" OPENCODE_DISABLE_CLAUDE_CODE=1 OPENCODE_DISABLE_EXTERNAL_SKILLS=1
AGENT= run_variant "2-default+claude-off" "$H/opencode-default.json" OPENCODE_DISABLE_CLAUDE_CODE=1 OPENCODE_DISABLE_EXTERNAL_SKILLS=1
AGENT= run_variant "3-default" "$H/opencode-default.json"
print -r -- "result: $OUT"
