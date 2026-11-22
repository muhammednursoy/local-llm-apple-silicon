# Local LLMs on Apple Silicon: benchmarks and setup

What it takes to run open models locally for everyday work on a MacBook Pro (Apple M4 Pro, 48 GB unified memory, 273 GB/s memory bandwidth per Apple's spec): which tasks they handle, how fast five models run on two inference engines, and how to set up a private assistant and OpenCode agents around them. Measured in October 2026 with Ollama 0.40.1 and mlx-lm.

The workload is Turkish on purpose: the benchmark prompts, the assistant's system prompts and the model answers are in Turkish. Everything else (code, configs, docs) is in English.

## Why run a model locally

The project started with three goals:

1. **Privacy.** Some work involves data that should not leave the machine. The model runs on the Mac, and prompts and answers stay there. For Ollama this was checked by sampling open network connections during generation (see [Findings](#findings)).
2. **Understanding.** Be able to explain from measurements why a model runs at the speed and memory it does: quantization, mixture-of-experts (MoE, where only some of the weights are read per token), the memory-bandwidth limit, the KV cache, GGUF vs MLX (see [Findings](#findings)).
3. **Everyday use.** Hand the local model the tasks that are fairly mechanical but touch sensitive data, and keep cloud models for the rest.

## Use cases tried

Answer quality was scored by a blind judge (Claude Opus): it saw outputs under shuffled labels, never the model or prompt behind them, and scored them against an answer key written before the runs (for the news summary, against the source text). Agent tasks were scored pass/fail by scripted checks. "Judge score" below is the judge's 1-5 usefulness score.

| Use case | Model | What was tried | Result |
|---|---|---|---|
| Taking notes and answering from them | Gemma 4 26B NVFP4, as an OpenCode agent | 8 scenarios × 3 runs: new note, append, answer from notes, answer not in the notes, a request to research online, delete, write and read outside the notes folder | 24 of 24 passed; dictated text was copied verbatim |
| Generating a monthly invoice from a template | Gemma 4 26B NVFP4, as an OpenCode agent | 7 scenarios × 4 runs on a throwaway copy of the invoice folder. The agent may only run the invoice scripts, and the only input is the number of hours | 26 of 28 passed; both failures only re-asked for the hours and changed nothing. The agent config is not in this repo because it contains personal paths |
| Summarizing a daily news digest | Qwen3.6-35B-A3B GGUF first, then Gemma 4 26B and others | One day's three digests (~150 KB), "top 5 items, one sentence each" | Qwen3.6: 5 of 15 items had errors, one reversing a number's meaning. Same input in a later blind round: Gemma 4 26B (GGUF and NVFP4) 15 of 15 fully correct, the same as Claude Opus; Gemma 4 31B 13; gpt-oss-20b 9. One day only, so a spot check |
| Questions over a document archive | Gemma 4 26B GGUF, Gemma 4 26B NVFP4, Qwen3.6-35B-A3B | 3 days of digests (~28K tokens), 6 questions, one of them a trap | Correct / partial / wrong: Gemma GGUF 5/1/0, Gemma NVFP4 4/2/0, Qwen3.6 3/1/2 (twice "not in the archive" when the answer was there). All quotes were real |
| Data analysis on a long table | Gemma 4 26B NVFP4 with the assistant prompt | Summing and grouping in chat, 4 prompt versions | Judge score 1 of 5 in every version. Correct when the OpenCode agent wrote and ran Python (78 s) |
| Small coding task | Gemma 4 26B NVFP4, Gemma 4 26B GGUF, Qwen3.6-35B-A3B, gpt-oss-20b | Make 5 failing tests pass in a small Python project without changing the tests (`eval/coding-agent.sh`, `eval/coding-fixture/`) | All four passed all 7 tests (the 5 target tests plus 2 existing ones) without touching the tests, in 138-316 s |

Notes on the table:
- In a later single round with a 9th notes scenario, the model summarized a note containing hidden instructions, did not follow them and warned the user.
- Coding: Gemma NVFP4 had the cleanest diff; Qwen3.6 had a sorting bug the tests did not catch; gpt-oss needed 26 tool calls.
- The archive and coding runs used no assistant system prompt; it was written later the same day.
- Production code and design documents were never a goal; the coding task only checks how far a local model gets.

The speed numbers below are reproducible from the raw CSVs in `results/`. The use-case results come from private scenarios (personal notes, a real invoice folder, real digests). They are reported here, but cannot be reproduced from this repo.

## Local assistant (`assistant/`)

An Ollama model with a built-in system prompt on top of Gemma 4 26B (`Modelfile`), an offline Open WebUI setup and the OpenCode agents. Details: [assistant/README.md](assistant/README.md).

The system prompt was tuned on Gemma 4 26B NVFP4 (thinking off, temperature 0.2) with 7 everyday-use scenarios, such as note-taking, answering from notes, data analysis, source review, news summary and chat. A separate holdout set of 7 scenarios was never seen while the prompt was written. Each number below is one full run: the judge scores each of the 7 answers from 1 to 5, so the maximum is 35. Violations are the number of broken rules across the 7 answers, such as invented facts or pretending to search the web.

| System prompt | Dev set score | Holdout set score | Holdout violations |
|---|---|---|---|
| None | 15 | 17, 15 | 7, 9 |
| `eval/prompts/v3.md` | 22, 20, 22, 21 | 20, 19 | 1, 3 |

The score gain is small next to the run-to-run spread (about 2 points); the clearer effect is fewer violations (1-3 against 7-9). Mean dev-set scores per version: v1 20, v2 21, v3 21.5, v4 (v3 plus worked examples) 20, so v3 was kept. One use-specific section and its example were removed from the published prompt versions after the measurements; the scores above were measured with them. The run and judge scripts (`eval/prompts/run.py`, `blind.py`, `judge-prompt.md`) work with your own scenarios in `eval/prompts/scenarios/<set>/*.json`, each with an `id` and a list of user `turns`.

## Speed (mean of 3 warm runs, tokens/s)

On AC power, Low Power Mode off, Docker and IDE closed. Runs taken on battery were discarded and re-measured by the script. Thinking off for every model except gpt-oss-20b, which cannot turn it off and ran with `think: low`.

| Model | Architecture | Engine and format | Decode, short prompt | Decode, ~32K context | Prefill, ~32K context |
|---|---|---|---|---|---|
| Qwen3.6-35B-A3B | MoE | mlx-lm, MLX 4-bit | 93.0 | 65.4 | 755 |
| Qwen3.6-35B-A3B | MoE | Ollama, NVFP4 | 65.6 | 52.9 | 628 |
| Qwen3.6-35B-A3B | MoE | Ollama, GGUF Q4_K_M | 62.9 | 46.6 | 505 |
| Gemma 4 26B-A4B | MoE | mlx-lm, MLX 4-bit | 81.4 | 55.4 | 615 |
| Gemma 4 26B-A4B | MoE | Ollama, GGUF Q4_K_M | 61.6 | 46.9 | 466 |
| gpt-oss-20b | MoE | mlx-lm, MXFP4-Q8 | 75.8 | 51.2 | 690 |
| gpt-oss-20b | MoE | Ollama | 52.0 | 43.5 | 549 |
| Qwen3.6-27B | dense | mlx-lm, MLX 4-bit | 15.2 | 13.3 | 117 |
| Qwen3.6-27B | dense | Ollama, GGUF Q4_K_M | 13.7 | 10.8 | 101 |
| Gemma 4 31B | dense | mlx-lm, MLX 4-bit | 13.4 | 10.7 | 91 |
| Gemma 4 31B | dense | Ollama, GGUF Q4_K_M | 7.9* | 7.0* | 76* |

\* Ollama's `gemma4:31b` tag turns on speculative decoding with a hidden draft model; it did not speed up this workload.

Source: `results/stage2-*.csv` and `results/stage3-*.csv`, rows with `warmup=False` and `ac_power=True`. Gemma 4 26B GGUF on Ollama was measured twice, so its short and 32K cells are means of 6 warm runs. The Gemma 4 26B NVFP4 build used by the assistant is not in this table; it was picked mainly because, asked for a current figure in repeated chat runs, it never made one up (0 of 4 runs against 3 of 4 for GGUF, a small sample).

## Findings

- **The engine matters more than the format.** For Qwen3.6-35B-A3B, Ollama's NVFP4 build decoded 19-29% slower than mlx-lm (put the other way, mlx-lm was 24-42% faster). mlx-lm was the fastest engine for every model.
- **Under mlx-lm, dense models get closer to the bandwidth ceiling than MoE models** (81-88% against 58-72%); under Ollama the pattern is weaker. The decode ceiling is 273 GB/s divided by the bytes read per token, estimated from each model's config before measuring. It differs per format because the bytes per weight differ. Short-prompt decode against that ceiling (ceiling in tokens/s, derived as measured ÷ share):

  | Model | Ollama GGUF: ceiling, share | mlx-lm: ceiling, share |
  |---|---|---|
  | Qwen3.6-35B-A3B (MoE) | ~131-161, 39-48% | ~131-160, 58-71% |
  | gpt-oss-20b (MoE) | ~74, 70% | ~105, 72% |
  | Gemma 4 26B-A4B (MoE) | ~101, 61% | ~118, 69% |
  | Qwen3.6-27B (dense) | ~18, 78% | ~19, 81% |
  | Gemma 4 31B (dense) | ~14, 57%* | ~15, 88% |

  Qwen3.6-35B-A3B is a range because its weights read per token were estimated as 1.7-2.1 GB. \* with Ollama's speculative decoding, see the Speed table.

  Likely explanation (an inference, not tested): the engine has a fixed cost per token, which takes a larger share as the time per token shrinks.
- **Ollama's default context is 4,096 tokens.** Longer prompts are truncated silently; set `num_ctx` on every request or in the Modelfile.
- **llama.cpp does not use Gemma 4's K=V sharing**: the KV cache came out exactly twice the size computed from `config.json` (measured from "KV buffer size" in the llama-server load log).
- **MLX does not split layers when it runs out of memory**; it stops with `kIOGPUCommandBufferCallbackErrorOutOfMemory`.
- **Ollama 0.40.1 copies GGUF models on first load**, and `ollama rm` does not delete the copy.
- **Low Power Mode on battery** halved the speed. The benchmark scripts check the power source and mode with `pmset`.
- **Rosetta trap:** if Homebrew is installed under Intel, Ollama runs as the Intel build and does not use the GPU.
- **Privacy:** Ollama listens on 127.0.0.1 only. No outbound connections were seen during generation (`lsof -i` sampled once a second). mlx-lm connects to the Hugging Face CDN while loading a model unless `HF_HUB_OFFLINE=1` is set. Ollama's update check queries GitHub hourly even with updates turned off.
- **Hugging Face downloads** ran at 0.4 MB/s without a token and 9.3 MB/s with one. Xet transfer stalled; `HF_HUB_DISABLE_XET=1` switched to plain HTTP.

## OpenCode with a local model

The most useful lessons, in short (details and measurements in the OpenCode section of [assistant/README.md](assistant/README.md)):

- Turn thinking off with `provider.ollama.models.<model>.options.reasoningEffort: "none"`, and cap output with `num_predict` in the Modelfile. With thinking on, Gemma 4 26B looped for minutes, and OpenCode's own output limit did not stop it on Ollama.
- Start every permission block with `"*": "deny"`. Otherwise the 2.0 `execute` tool (JavaScript with network access) stays on, and the outside-directory guard does not cover shell arguments.
- A system message in the request makes Ollama drop the Modelfile prompt entirely.

`harness/` holds two small comparisons. `smoke.sh` runs a three-step file task through a minimal OpenCode agent (`local`, defined in `harness/opencode-minimal.json`) and checks the result independently. `experiment.sh` measures how much prompt OpenCode's default setup sends compared with that minimal agent.

## Layout

| Folder | Contents |
|---|---|
| `bench/` | Ollama and mlx-lm benchmark scripts, prompts, the stage 3 batch runner. Sources of the long prompts are in `bench/SOURCES.md` |
| `results/` | Raw benchmark CSVs and model answers |
| `assistant/` | Modelfiles, system prompts, Open WebUI launcher, OpenCode agent config, temperature proxy |
| `harness/` | OpenCode smoke test and config comparison |
| `eval/` | System prompt versions (v1-v4), blind-judge scripts, the coding-agent test and its synthetic fixture |

## Running

```bash
python3.11 -m venv .venv
```

```bash
.venv/bin/pip install mlx-lm huggingface_hub
```

```bash
.venv/bin/python bench/ollama_bench.py --help
```

```bash
.venv/bin/python bench/mlx_bench.py --help
```

The long prompts (`bench/prompts-stage2.json`) are not in the repo; rebuild them first as described in [bench/SOURCES.md](bench/SOURCES.md). Stage 2 was run by calling the two benchmark scripts by hand. `bench/stage3.sh` runs stage 3 end to end: download, measure both engines, delete.

Assistant model: run `assistant/build.sh`, then `ollama run gemma4-assistant --think=false`. In the temperature proxy's launchd file, replace `REPO_DIR` and `HOME_DIR` with your own paths.

A benchmark round takes minutes and keeps the GPU fully loaded; run it on AC power with other heavy apps closed.

## License

MIT, see [LICENSE](LICENSE).
