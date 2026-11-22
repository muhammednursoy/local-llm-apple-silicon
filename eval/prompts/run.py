#!/usr/bin/env python3
import argparse
import glob
import json
import os
import time
import urllib.request

R = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemma4:26b")
ap.add_argument("--prompt", default="none", help="system prompt file in this folder, or 'none'")
ap.add_argument("--set", default="dev", help="scenario set: dev or holdout")
ap.add_argument("--name", required=True, help="variant name for the output folder")
ap.add_argument("--think", default="false")
ap.add_argument("--temperature", type=float, default=0.2)
ap.add_argument("--repeat", type=int, default=1)
a = ap.parse_args()

think = {"false": False, "true": True}.get(a.think, a.think)
system = None if a.prompt == "none" else open(os.path.join(R, a.prompt), encoding="utf-8").read().strip()


def chat(messages):
    payload = {"model": a.model, "messages": messages, "stream": False, "think": think, "keep_alive": "10m",
               "options": {"num_ctx": 32768, "num_predict": 12000, "temperature": a.temperature}}
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        return json.loads(r.read())


for n in range(1, a.repeat + 1):
    out = os.path.join(R, "outputs", a.set, f"{a.name}-t{n}")
    os.makedirs(out, exist_ok=True)
    stats = {}
    for path in sorted(glob.glob(os.path.join(R, "scenarios", a.set, "*.json"))):
        sc = json.load(open(path, encoding="utf-8"))
        messages = [{"role": "system", "content": system}] if system else []
        md, t0, tokens = [], time.time(), 0
        for i, turn in enumerate(sc["turns"], 1):
            messages.append({"role": "user", "content": turn})
            r = chat(messages)
            answer = r["message"]["content"].strip()
            messages.append({"role": "assistant", "content": answer})
            tokens += r.get("eval_count", 0)
            md.append(f"## Turn {i}\n\n**User:**\n\n{turn}\n\n**Assistant:**\n\n{answer}\n")
        open(os.path.join(out, f"{sc['id']}.md"), "w", encoding="utf-8").write("\n".join(md))
        stats[sc["id"]] = {"seconds": round(time.time() - t0, 1), "gen_tokens": tokens}
        print(a.name, n, sc["id"], stats[sc["id"]], flush=True)
    json.dump({"model": a.model, "prompt": a.prompt, "think": think, "temperature": a.temperature, "scenarios": stats},
              open(os.path.join(out, "stats.json"), "w"), ensure_ascii=False, indent=1)
