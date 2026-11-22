# Long-prompt sources

The `summary-8k` and `summary-32k` prompts were built from the text of the pages below (fetched in October 2026). The texts belong to their copyright holders and are not in this repo, so `bench/prompts-stage2.json` is not tracked.

To rebuild it, save each source as plain text under the file name below in one folder, then run:

```bash
python3 bench/make_long_prompts.py <source-dir> bench/prompts-stage2.json
```

The script concatenates the files in name order and keeps the first 30,000 / 118,000 characters. If your extracts are cut differently, the prompts and token counts will not match the measured ones exactly.

| File | Source |
|---|---|
| `apple-m4pro-newsroom.md` | https://www.apple.com/newsroom/2024/10/apple-introduces-m4-pro-and-m4-max/ (relevant paragraphs) |
| `arxiv-2211.17192-abs.md` | https://arxiv.org/abs/2211.17192 (title, authors, abstract) |
| `arxiv-2402.16363-abs.md` | https://arxiv.org/abs/2402.16363 |
| `arxiv-2407.09141-abs.md` | https://arxiv.org/abs/2407.09141 |
| `arxiv-2411.17691-abs.md` | https://arxiv.org/abs/2411.17691 |
| `arxiv-2412.06464-abs.md` | https://arxiv.org/abs/2412.06464 |
| `arxiv-2503.07103-abs.md` | https://arxiv.org/abs/2503.07103 |
| `arxiv-2504.19874-abs.md` | https://arxiv.org/abs/2504.19874 |
| `arxiv-2505.19645-abs.md` | https://arxiv.org/abs/2505.19645 |
| `arxiv-2505.20276-abs.md` | https://arxiv.org/abs/2505.20276 |
| `arxiv-2511.05502-abs.md` | https://arxiv.org/abs/2511.05502 |
| `cisco-shodan-ollama.md` | https://blogs.cisco.com/security/detecting-exposed-llm-servers-shodan-case-study-on-ollama |
| `epoch-consumer-gpu-model-gap.md` | https://epoch.ai/data-insights/consumer-gpu-model-gap |
| `epoch-open-models-report.md` | https://epoch.ai/blog/open-models-report (summary and findings) |
| `github-mlx-lm-issue-883.md` | https://github.com/ml-explore/mlx-lm/issues/883 (title, body summary, start of comments) |
| `gpt-oss-arxiv-2508.10925-sec2.md` | https://arxiv.org/html/2508.10925 (§2) |
| `hf-gemma-4-31b-README.md` | Gemma 4 31B Hugging Face model card |
| `hf-gpt-oss-20b-README.md` | gpt-oss-20b Hugging Face model card |
| `hf-mlx-qwen3.6-35b-a3b-4bit-README.md` | https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit |
| `hf-qwen3.6-27b-README.md` | https://huggingface.co/Qwen/Qwen3.6-27B |
