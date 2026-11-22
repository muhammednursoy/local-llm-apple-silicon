#!/bin/zsh
set -eu
cd "${0:A:h}"
PROMPT=../eval/prompts/v3.md
{
  print -r -- "FROM gemma4:26b"
  print -r -- "PARAMETER num_ctx 32768"
  print -r -- "PARAMETER temperature 0.2"
  print -r -- 'SYSTEM """'
  cat "$PROMPT"
  print -r -- '"""'
} > Modelfile
ollama create gemma4-assistant -f Modelfile
ollama show gemma4-assistant --parameters
ollama create gemma4-agent -f Modelfile.agent

OWUI=http://127.0.0.1:8080
if curl -sf -o /dev/null "$OWUI/health"; then
  TOK=$(curl -s -X POST "$OWUI/api/v1/auths/signin" -H 'Content-Type: application/json' -d '{"email":"","password":""}' \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
  python3 -c "
import json,sys
s=open(sys.argv[1],encoding='utf-8').read().strip()
print(json.dumps({'id':'gemma4-assistant:latest','base_model_id':None,'name':'gemma4-assistant',
  'meta':{'description':'Gemma 4 26B + local assistant prompt'},'params':{'system':s,'think':False},'is_active':True}))" "$PROMPT" \
    | curl -sf -X POST "$OWUI/api/v1/models/model/update" -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' --data @- >/dev/null \
    && print "Open WebUI model prompt updated" || print "WARNING: could not update the Open WebUI model prompt"
else
  print "Open WebUI is not running; run ./build.sh again once it is up"
fi
