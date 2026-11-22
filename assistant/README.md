# gemma4-assistant

A local assistant with a built-in system prompt on top of `gemma4:26b`, which in Ollama is the NVFP4 build of Gemma 4 26B-A4B. It shares weights with `gemma4:26b` and takes no extra disk space. The NVFP4 build is not in the root README's speed table (the GGUF build is). It was chosen over GGUF because in repeated runs it never invented current figures (0 of 4 runs, against 3 of 4 for GGUF). The system prompts are in Turkish because the assistant is used in Turkish.

## Usage

```bash
./build.sh
```

```bash
ollama run gemma4-assistant --think=false
```

In the Ollama app, pick `gemma4-assistant` from the model list and turn the thinking switch off.

Use it with thinking off: with thinking on, given long notes, tables or sources, the model thought for more than 12K tokens without reaching an answer and returned empty (6 of 6 tries).

## Settings
- Prompt: `eval/prompts/v3.md` (single source). After changing it, run `./build.sh` again; it generates `Modelfile`.
- `num_ctx 32768`: Ollama's default is 4,096; longer text is truncated silently.
- `temperature 0.2`: every test used this value.
- `Modelfile.agent`: a prompt-less alias for the OpenCode agents (`gemma4-agent`), with a `num_predict 3000` cap.

## Good for, not good for
- Good: note-taking, answering from notes, news summaries (15 of 15 items correct in one blind spot check), comparing sources, chat, small calculations.
- Data analysis on long tables: makes summing errors in chat. In OpenCode, running Python, the numbers came out right.
- No web search; paste text and it works on that.

## Open WebUI (chat UI)

Start with `./open-webui.sh`, then open http://127.0.0.1:8080. Install: `~/.local/share/open-webui/venv` (pip, no Docker, 1.8 GB); data in `~/.local/share/open-webui/data`.
- Listens on 127.0.0.1 only, no login screen (single user), offline mode, telemetry and community sharing off.
- Background requests (title, tags, follow-up questions, autocomplete, search queries) are off: each would be a separate request to the local model.
- Default model `gemma4-assistant`, thinking off for all models (`DEFAULT_MODEL_PARAMS`).
- Document upload works without an embedding model: the document goes into the chat as is (`BYPASS_EMBEDDING_AND_RETRIEVAL`); documents longer than 32K tokens do not fit.
- Measured: first answer 8.7 s (including model load), later ones 6.2 s; thinking text 0; outbound connections during chat 0; 194 MB idle.
- These settings are written to the database on first start; change them later under Admin Settings in the UI.
- The prompt is also set in Open WebUI's model settings (`gemma4-assistant:latest`, `params.system`). Reason: if the request contains a system message, Ollama drops the Modelfile prompt entirely (measured: 1,132 → 28 tokens). `./build.sh` updates this copy too when Open WebUI is running.
- Memories do not work in this setup: they need an embedding model, which offline mode does not download.

## OpenCode agents (`opencode-agents.json`)

Tested with OpenCode 2.0.26 to 2.0.28. The file uses OpenCode's config format; copy it to the global config (`~/.config/opencode/opencode.jsonc`) or to a folder's `opencode.json`. Prompt paths (`{file:./...}`) are relative to the file's location.

| Agent | What it does | Permissions |
|---|---|---|
| `assistant` | General local assistant: reads and searches files, answers questions | Read, search, list allowed; `ls`, `pwd`, relative `cat` allowed; other commands, writes and edits ask; network, `execute`, `skill`, `task` denied |
| `notes` | Takes notes in an Obsidian vault, appends to existing notes, answers from notes | File reads only via `cat` and only with relative paths (the read tool's line numbers were being copied into notes); write/edit (except `opencode.json`); search; other commands ask; network denied |

- The background service does not reload when the config file changes; run `opencode reload` (measured on 2.0.28).
- Thinking off: `provider.ollama.models.gemma4-agent.options.reasoningEffort: "none"`. Measured by capturing requests: this key reaches the request as `reasoning_effort: "none"` and the reply has no thinking part; the same key at agent level never reaches the request. Reason: in one agent session the model spun in its thinking channel for 4.5 minutes on a simple question (36K characters, 86 "Actually"), never calling a tool.
- Output cap: `num_predict 3000` in `Modelfile.agent`. When the client sends no `max_tokens`, the `/v1` endpoint applies the Modelfile's `num_predict` and counts thinking tokens too. The `max_completion_tokens: 8192` that OpenCode sends did not stop the loop (about 12K tokens were generated).
- Permissions are "everything denied, listed items allowed" (`"*": "deny"` as the first rule). The `execute` tool in 2.0 (JavaScript + `fetch`, network access) is only closed this way; it stays open unless denied. At agent level the `skill`, `websearch` and `task` keys do not make it into the resolved rules, and `tools: {x: false}` (deprecated) is overridden because it is written before the `"*"` rule; these tools close only with `"*": "deny"` (checked with `opencode debug agents`).
- In 2.0 the outside-directory guard (`external_directory`) does not apply to arguments of shell commands such as `cat`: a `cat` with an absolute path read outside the vault (2 of 3 rounds). That is why absolute paths, `~`, `..`, `$`, backticks, `;`, `&`, `|`, `>`, `<` and `://` are denied in the command rules.
- Neither 1.18.35 nor 2.0 puts the agent's `temperature` into the request (requests captured; 5 ways tried at agent and model level). Ollama's `/v1` endpoint also ignores the Modelfile value when the request has no temperature. The agents therefore run at temperature 1.
- When a command is denied, the model tries to get around it with `python3`, `sh`, `zsh -c`; all of them hit `"*": "deny"`.
- Notes agent test (2.0.26): 8 scenarios × 3 rounds, 24/24, including "read a file outside the vault". In a later single round with 9 scenarios, it summarized a note containing hidden instructions, did not follow them, and warned the user.

## Temperature proxy (`temperature-proxy.py`, off by default)

Listens on port 11436; if a `/v1` request has no temperature, it adds the model's Modelfile value and forwards the request to Ollama. It worked with plain curl (two answers identical at temperature 0), but in one OpenCode test the connection hung (600 s timeout, Ollama idle); the cause was not found. To run it with launchd, replace `REPO_DIR` and `HOME_DIR` in `local.llm.temperature-proxy.plist` and put it under `~/Library/LaunchAgents/`.

## Open issues
- **Thinking tags leaking into answers.** With `reasoningEffort: "none"` there is no thinking part, but in one session 5 of 16 answers started with `thought`, `<channel|>` or `落地` (a stray Chinese token); all five came right after a tool result. Likely explanation (inference, requests not captured): the model opens its thinking channel, and since thinking is off, Ollama passes it into the text without stripping it.
- **Saying instead of doing.** The model sometimes said "opening it" and wrote the command only as text, then stopped.
- **Web access is off.** Instructions inside web content (prompt injection) combined with file reads and commands could send file contents out; the 26B model was not tested against such instructions.
