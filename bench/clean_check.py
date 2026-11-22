#!/usr/bin/env python3
import csv
import os
import sys
from collections import defaultdict

path, keycol, key, runs = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 3
prompts = ["short-tr", "summary-8k", "summary-32k"]

if not os.path.exists(path):
    print(f"{key}: no results")
    sys.exit(1)

by_prompt = defaultdict(list)
for r in csv.DictReader(open(path)):
    if r[keycol] == key:
        by_prompt[r["prompt_name"]].append(r)

dirty = []
for p in prompts:
    last = [r for r in by_prompt.get(p, [])[-(runs + 1):] if r["warmup"] == "False"]
    if len(last) < runs:
        dirty.append(f"{p}: missing ({len(last)}/{runs})")
        continue
    bad = [r["ts"] for r in last if r["powermode"] != "0" or r["ac_power"] != "True"]
    if bad:
        dirty.append(f"{p}: on battery/low power {bad}")

if dirty:
    print(f"{key}: DIRTY -> " + "; ".join(dirty))
    sys.exit(1)
print(f"{key}: clean")
