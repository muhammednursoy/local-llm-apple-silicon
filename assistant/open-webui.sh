#!/bin/zsh
set -eu
ROOT="$HOME/.local/share/open-webui"
mkdir -p "$ROOT/data"
cd "$ROOT/data"

export DATA_DIR="$ROOT/data"
export WEBUI_AUTH=False
export OFFLINE_MODE=true
export ANONYMIZED_TELEMETRY=false DO_NOT_TRACK=true SCARF_NO_ANALYTICS=true
export ENABLE_COMMUNITY_SHARING=False

export ENABLE_OLLAMA_API=True OLLAMA_BASE_URL=http://127.0.0.1:11434
export ENABLE_OPENAI_API=False
export DEFAULT_MODELS=gemma4-assistant:latest
export DEFAULT_MODEL_PARAMS='{"think": false}'

export ENABLE_TITLE_GENERATION=False ENABLE_TAGS_GENERATION=False ENABLE_FOLLOW_UP_GENERATION=False
export ENABLE_AUTOCOMPLETE_GENERATION=False ENABLE_SEARCH_QUERY_GENERATION=False ENABLE_RETRIEVAL_QUERY_GENERATION=False
export ENABLE_IMAGE_PROMPT_GENERATION=False

export BYPASS_EMBEDDING_AND_RETRIEVAL=true

exec "$ROOT/venv/bin/open-webui" serve --host 127.0.0.1 --port 8080
