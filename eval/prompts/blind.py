#!/usr/bin/env python3
import glob
import json
import os
import random
import shutil
import sys

R = os.path.dirname(os.path.abspath(__file__))
setname, rnd, variants = sys.argv[1], sys.argv[2], sys.argv[3:]

jd = os.path.join(R, "judge", f"{setname}-{rnd}")
mapping = {}
ids = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(R, "scenarios", setname, "*.json")))
for sid in ids:
    vs = variants[:]
    random.SystemRandom().shuffle(vs)
    mapping[sid] = dict(zip("ABCDEFGH", vs))
    os.makedirs(os.path.join(jd, sid), exist_ok=True)
    for label, v in mapping[sid].items():
        shutil.copy(os.path.join(R, "outputs", setname, v, f"{sid}.md"), os.path.join(jd, sid, f"{label}.md"))
json.dump(mapping, open(os.path.join(R, "judge", f"mapping-{setname}-{rnd}.json"), "w"), indent=1)
print("ready:", jd, len(ids), "scenarios,", len(variants), "variants")
