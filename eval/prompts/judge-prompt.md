Do the work inline yourself. No sub-agents, no web. Use Read, Write and Bash (`grep`, `python3` for checking arithmetic) only.
The evaluation is BLIND: do NOT read any `mapping-*.json`, anything under `outputs/`, any `*.md` prompt file in the folder root, or any other `judge/` subfolder than the one named below. Do not try to guess which system wrote what.

Folder: `{REPO}/eval/prompts`
Set: `{SET}` · Round folder: `judge/{SET}-{ROUND}/`

A private local Turkish assistant was run on a set of everyday-use scenarios (e.g. note-taking, note-reading, data-analysis, source-review, news-summary, chat). For each scenario, several runs are labelled A, B, C… (labels shuffled independently per scenario). Scenario inputs: `scenarios/{SET}/<id>.json` (the user turns; materials are inside them). Answer key: `scenarios/{SET}/key.md` (must-haves, must-nots, exact numbers, rubric). Outputs: `judge/{SET}-{ROUND}/<id>/<label>.md` (full transcripts).

For every scenario and every label:
- Check each must-have and must-not in the key. Recompute any number the output gives that the key also gives; quote the number the output gave.
- `missing`: list of must-haves missed (short phrases; [] if none).
- `violations`: list of must-nots violated, including fabrication (facts not in the materials or presented as current), pretending to search the web, adding content to a dictated note (short phrases; [] if none).
- `number_errors`: list of wrong numbers as "given → correct" ([] if none).
- `score`: 1-5 overall usefulness per the key's rubric line.
- `length`: "short" / "ok" / "too long" for what the user asked.
- `note`: one short sentence: the decisive strength or flaw.
Then per scenario `ranking`: labels best to worst.

Code instead of hand arithmetic: if an output declines to hand-compute a large table and instead gives Python code, extract the table from the scenario into a file, run the code with `python3` against it, and compare its printed results with the key. Numeric must-haves the code gets right count as met (write "by code" in `note`); wrong or crashing code counts as missed. Numbers the output states in prose are still checked as numbers.

Apply the same bar to every label. A clean, short answer that meets all must-haves beats a long one that also meets them.

Write `judge/{SET}-{ROUND}/result.json`:
{"<id>": {"A": {"missing": [], "violations": [], "number_errors": [], "score": 4, "length": "ok", "note": "..."}, "B": {...}, "ranking": ["B","A","C"]}, ...}

Report back ≤10 lines: per scenario one line with each label's score and its most serious flaw.
