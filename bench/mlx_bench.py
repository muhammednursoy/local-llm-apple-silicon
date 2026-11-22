#!/usr/bin/env python3
import argparse
import csv
import datetime
import json
import os
import re
import subprocess
import time
import uuid

from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler

FIELDS = [
    "ts", "model", "prompt_name", "run", "warmup", "think", "max_tokens",
    "powermode", "ac_power", "swap_used_mb_before", "swap_used_mb_after", "mem_free_pct_after",
    "load_s", "prompt_tokens", "prefill_tok_s", "gen_tokens", "decode_tok_s", "wall_s", "peak_mem_gb",
]


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


def swap_used_mb():
    m = re.search(r"used = ([\d.]+)M", sh("sysctl vm.swapusage"))
    return float(m.group(1)) if m else None


def mem_free_pct():
    m = re.search(r"free percentage: (\d+)%", sh("memory_pressure"))
    return int(m.group(1)) if m else None


def powermode():
    m = re.search(r"powermode\s+(\d+)", sh("pmset -g"))
    return int(m.group(1)) if m else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--prompts", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--max-tokens", type=int, default=400)
    p.add_argument("--think", choices=["true", "false"], default="false")
    p.add_argument("--nonce", action="store_true")
    p.add_argument("--answers-dir")
    a = p.parse_args()

    t0 = time.time()
    model, tok = load(a.model)
    load_s = round(time.time() - t0, 2)
    think = a.think == "true"
    sampler = make_sampler(temp=0.0)
    prompts = json.load(open(a.prompts, encoding="utf-8"))

    new = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for name, prompt in prompts.items():
            for i in range(a.runs + 1):
                text = f"[istek {uuid.uuid4().hex[:12]}]\n{prompt}" if a.nonce else prompt
                chat = tok.apply_chat_template(
                    [{"role": "user", "content": text}],
                    add_generation_prompt=True, tokenize=False, enable_thinking=think,
                )
                row = {
                    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                    "model": a.model, "prompt_name": name, "run": i, "warmup": i == 0,
                    "think": think, "max_tokens": a.max_tokens, "powermode": powermode(),
                    "ac_power": "AC Power" in sh("pmset -g batt"), "swap_used_mb_before": swap_used_mb(),
                    "load_s": load_s if i == 0 else 0,
                }
                out, last, start = [], None, time.time()
                for resp in stream_generate(model, tok, chat, max_tokens=a.max_tokens, sampler=sampler):
                    out.append(resp.text)
                    last = resp
                row.update({
                    "prompt_tokens": last.prompt_tokens,
                    "prefill_tok_s": round(last.prompt_tps, 1),
                    "gen_tokens": last.generation_tokens,
                    "decode_tok_s": round(last.generation_tps, 1),
                    "wall_s": round(time.time() - start, 2),
                    "peak_mem_gb": round(last.peak_memory, 2),
                    "swap_used_mb_after": swap_used_mb(),
                    "mem_free_pct_after": mem_free_pct(),
                })
                w.writerow(row)
                f.flush()
                print(f"mlx {name} run={i} ptok={row['prompt_tokens']} prefill={row['prefill_tok_s']} "
                      f"decode={row['decode_tok_s']} peak={row['peak_mem_gb']}GB", flush=True)
                if a.answers_dir and i == 1:
                    os.makedirs(a.answers_dir, exist_ok=True)
                    with open(os.path.join(a.answers_dir, f"mlx-lm__{name}.md"), "w") as af:
                        af.write("".join(out))


if __name__ == "__main__":
    main()
