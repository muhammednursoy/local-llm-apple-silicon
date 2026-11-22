#!/bin/zsh
set -u
cd "${0:A:h}/.."

MODELS=(
  "gpt-oss-20b|gpt-oss:20b|mlx-community/gpt-oss-20b-MXFP4-Q8|low"
  "gemma4-26b-a4b|gemma4:26b-a4b-it-q4_K_M|mlx-community/gemma-4-26b-a4b-it-4bit|false"
  "qwen3.6-27b|qwen3.6:27b-q4_K_M|mlx-community/Qwen3.6-27B-4bit|false"
  "gemma4-31b|gemma4:31b-it-q4_K_M|mlx-community/gemma-4-31b-it-4bit|false"
)
PROMPTS=bench/prompts-stage2.json
KEEP_CONV="llamacpp:b52ca43760e9d78765c095f8eae18551b9268262e216d38637e93a67b09d9e71"
export HF_HOME=$PWD/.hf HF_HUB_DISABLE_XET=1 HF_HUB_DOWNLOAD_TIMEOUT=60 HF_HUB_ETAG_TIMEOUT=30

log() { print -r -- "== $(date +%T) $*"; }

free_gb() { df -g /System/Volumes/Data | awk 'NR==2 {print $4}'; }

conditions_ok() {
  pmset -g batt | grep -q "AC Power" || { print "not on AC power"; return 1; }
  pmset -g | grep -qE "powermode[[:space:]]+0" || { print "powermode is not 0"; return 1; }
  pgrep -f "Virtualization.VirtualMachine" >/dev/null && { print "docker is running"; return 1; }
  pgrep -x idea >/dev/null && { print "IntelliJ is running"; return 1; }
  return 0
}

wait_conditions() {
  local i reason
  for i in {1..720}; do
    reason=$(conditions_ok) && { (( i > 1 )) && log "conditions met"; return 0; }
    (( i == 1 )) && log "waiting for conditions: $reason"
    sleep 60
  done
  log "conditions not met within 12 hours: $reason"
  return 1
}

hf_download() {
  local repo=$1 attempt
  for attempt in 1 2 3 4 5; do
    HF_TOKEN=${HF_TOKEN:?HF_TOKEN is required} .venv/bin/python -I -c "
import sys
from huggingface_hub import HfApi, snapshot_download
import os
info = HfApi().model_info('$repo', files_metadata=True)
path = snapshot_download('$repo', max_workers=4)
bad = [s.rfilename for s in info.siblings if not os.path.exists(os.path.join(path, s.rfilename)) or os.path.getsize(os.path.join(path, s.rfilename)) != s.size]
print('hf files', len(info.siblings), 'mismatched', len(bad))
sys.exit(1 if bad else 0)
" && return 0
    log "hf download attempt $attempt failed"
    sleep 60
  done
  return 1
}

llamacpp_entries() { ollama list | awk 'NR>1 && $1 ~ /^llamacpp:/ {print $1}' | sort; }

gguf_clean() { /opt/homebrew/bin/python3.11 -I bench/clean_check.py results/stage3-ollama.csv tag "$1"; }
mlx_clean() { /opt/homebrew/bin/python3.11 -I bench/clean_check.py results/stage3-mlx.csv model "$1"; }
measured() { gguf_clean "$1" >/dev/null && mlx_clean "$2" >/dev/null; }

run_gguf() {
  local tag=$1 think=$2 attempt
  for attempt in 1 2 3; do
    gguf_clean "$tag" >/dev/null && return 0
    wait_conditions || return 1
    log "GGUF measurement starting (attempt $attempt)"
    /opt/homebrew/bin/python3.11 -I bench/ollama_bench.py --tag "$tag" --prompts $PROMPTS \
      --out results/stage3-ollama.csv --answers-dir results/stage3-answers --runs 3 \
      --num-ctx 40960 --think "$think" --num-predict 400 --nonce
    log "GGUF exit=$? $(gguf_clean "$tag")"
    ollama stop "$tag"; sleep 5
  done
  gguf_clean "$tag" >/dev/null
}

run_mlx() {
  local repo=$1 think=$2 name=$3 attempt
  for attempt in 1 2 3; do
    mlx_clean "$repo" >/dev/null && return 0
    wait_conditions || return 1
    log "mlx-lm measurement starting (attempt $attempt)"
    HF_HUB_OFFLINE=1 .venv/bin/python -I -u bench/mlx_bench.py --model "$repo" --prompts $PROMPTS \
      --out results/stage3-mlx.csv --answers-dir "results/stage3-answers/$name" --runs 3 \
      --max-tokens 400 --think "$think" --nonce
    log "mlx-lm exit=$? $(mlx_clean "$repo")"
  done
  mlx_clean "$repo" >/dev/null
}

for entry in "${MODELS[@]}"; do
  IFS='|' read -r name tag repo think <<< "$entry"
  if measured "$tag" "$repo"; then log "$name already measured, skipped"; continue; fi
  log "MODEL $name ($tag | $repo) free ${$(free_gb)}GB"
  if (( $(free_gb) < 40 )); then log "less than 40GB free, $name skipped"; continue; fi

  ollama pull "$tag" > "results/stage3-$name-pull.log" 2>&1 || { log "ollama pull failed: $tag"; continue; }
  log "ollama pull done"
  hf_download "$repo" || { log "hf download failed: $repo"; ollama rm "$tag"; continue; }
  log "hf download done, free ${$(free_gb)}GB"

  run_gguf "$tag" "$think" || { log "$name GGUF arm could not be measured cleanly, stopping"; exit 1; }
  mlx_think=$([[ $think == true ]] && echo true || echo false)
  run_mlx "$repo" "$mlx_think" "$name" || { log "$name mlx-lm arm could not be measured cleanly, stopping"; exit 1; }

  git add results bench && git commit -q -m "Stage 3: $name measurement (GGUF + mlx-lm)" && log "commit $(git rev-parse --short HEAD)"

  ollama rm "$tag" >/dev/null
  for conv in $(llamacpp_entries); do
    [[ $conv == "$KEEP_CONV" ]] && continue
    ollama rm "$conv" >/dev/null && log "removed Ollama conversion copy: $conv"
  done
  rm -rf "$HF_HOME/hub/models--${repo//\//--}"
  log "$name removed, free ${$(free_gb)}GB"
done
log "STAGE 3 DONE"
