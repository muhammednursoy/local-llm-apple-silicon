#!/usr/bin/env python3
import glob
import json
import os
import sys

if len(sys.argv) < 2:
    sys.exit("usage: make_long_prompts.py <source-dir> [out.json]")
SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "bench/prompts-stage2.json"
TARGETS = {"summary-8k": 30000, "summary-32k": 118000}

INSTRUCTION = (
    "Aşağıdaki teknik belgeleri oku. Türkçe olarak, yerel LLM çalıştırmak isteyen bir mühendis için "
    "en önemli 5 bulguyu madde madde yaz.\n\n<belgeler>\n"
)

docs = []
for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
    docs.append(f"### {os.path.basename(path)}\n{open(path, encoding='utf-8').read()}\n")
corpus = "".join(docs)

prompts = {"short-tr": "Bir ödeme sisteminde idempotency anahtarı neden gereklidir? Üç cümleyle açıkla."}
for name, chars in TARGETS.items():
    if len(corpus) < chars:
        sys.exit(f"not enough material for {name}: {len(corpus)} < {chars}")
    prompts[name] = INSTRUCTION + corpus[:chars] + "\n</belgeler>"

json.dump(prompts, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in prompts.items()})
