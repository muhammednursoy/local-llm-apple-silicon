#!/usr/bin/env python3
import argparse
import csv
import datetime
import json
import os
import re
import subprocess
import urllib.request
import uuid

HOST = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")

FIELDS = [
    "ts", "tag", "model_digest", "prompt_name", "run", "warmup", "think", "num_ctx",
    "powermode", "ac_power", "swap_used_mb_before", "swap_used_mb_after", "mem_free_pct_after",
    "load_s", "prompt_tokens", "prefill_s", "prefill_tok_s",
    "gen_tokens", "decode_s", "decode_tok_s", "total_s",
    "ps_size_gb", "ps_vram_gb", "ps_gpu_pct", "ps_context",
]


def api(path, payload=None, timeout=900):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(HOST + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


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


def ac_power():
    return "AC Power" in sh("pmset -g batt")


def digest(tag):
    for m in api("/api/tags")["models"]:
        if m["name"] == tag or m["model"] == tag:
            return m["digest"][:12]
    return None


def ps(tag):
    for m in api("/api/ps").get("models", []):
        if m["name"] == tag or m["model"] == tag:
            size, vram = m.get("size", 0), m.get("size_vram", 0)
            return {
                "ps_size_gb": round(size / 1e9, 2),
                "ps_vram_gb": round(vram / 1e9, 2),
                "ps_gpu_pct": round(100 * vram / size) if size else None,
                "ps_context": m.get("context_length"),
            }
    return {}


def run_once(tag, prompt, think, num_ctx, num_predict, nonce):
    if nonce:
        prompt = f"[istek {uuid.uuid4().hex[:12]}]\n{prompt}"
    options = {"num_ctx": num_ctx, "temperature": 0, "seed": 1}
    if num_predict:
        options["num_predict"] = num_predict
    payload = {
        "model": tag,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": think,
        "keep_alive": "15m",
        "options": options,
    }
    r = api("/api/chat", payload)
    ns = 1e9
    pe_n, pe_d = r.get("prompt_eval_count", 0), r.get("prompt_eval_duration", 0) / ns
    ev_n, ev_d = r.get("eval_count", 0), r.get("eval_duration", 0) / ns
    return {
        "load_s": round(r.get("load_duration", 0) / ns, 2),
        "prompt_tokens": pe_n,
        "prefill_s": round(pe_d, 3),
        "prefill_tok_s": round(pe_n / pe_d, 1) if pe_d else None,
        "gen_tokens": ev_n,
        "decode_s": round(ev_d, 3),
        "decode_tok_s": round(ev_n / ev_d, 1) if ev_d else None,
        "total_s": round(r.get("total_duration", 0) / ns, 2),
    }, r["message"]["content"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tag", required=True)
    p.add_argument("--prompts", required=True, help="JSON file: {name: prompt}")
    p.add_argument("--out", required=True)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--num-ctx", type=int, default=40960)
    p.add_argument("--think", choices=["true", "false", "low", "medium", "high"], default="false")
    p.add_argument("--answers-dir")
    p.add_argument("--num-predict", type=int, default=0)
    p.add_argument("--nonce", action="store_true", help="unique prefix per request to bypass the prompt cache")
    a = p.parse_args()

    prompts = json.load(open(a.prompts))
    think = {"true": True, "false": False}.get(a.think, a.think)
    new = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for name, prompt in prompts.items():
            for i in range(a.runs + 1):
                row = {
                    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                    "tag": a.tag, "model_digest": digest(a.tag), "prompt_name": name,
                    "run": i, "warmup": i == 0, "think": think, "num_ctx": a.num_ctx,
                    "powermode": powermode(), "ac_power": ac_power(),
                    "swap_used_mb_before": swap_used_mb(),
                }
                stats, answer = run_once(a.tag, prompt, think, a.num_ctx, a.num_predict, a.nonce)
                row.update(stats)
                row.update(ps(a.tag))
                row["swap_used_mb_after"] = swap_used_mb()
                row["mem_free_pct_after"] = mem_free_pct()
                w.writerow(row)
                f.flush()
                print(f"{a.tag} {name} run={i} prefill={row['prefill_tok_s']} decode={row['decode_tok_s']} "
                      f"gpu={row.get('ps_gpu_pct')}% ctx={row.get('ps_context')}")
                if a.answers_dir and i == 1:
                    os.makedirs(a.answers_dir, exist_ok=True)
                    safe = a.tag.replace(":", "_").replace("/", "_")
                    with open(os.path.join(a.answers_dir, f"{safe}__{name}.md"), "w") as af:
                        af.write(answer)


if __name__ == "__main__":
    main()
