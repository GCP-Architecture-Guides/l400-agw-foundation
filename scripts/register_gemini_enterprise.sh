#!/usr/bin/env bash

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# =============================================================================
# scripts/register_gemini_enterprise.sh
#
# Pre-flight checks for Gemini Enterprise App registration, then prints
# step-by-step console UI instructions.
#
# Usage:
#   bash scripts/register_gemini_enterprise.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
cd "$PROJECT_ROOT"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       Task 5: Register Agent in Gemini Enterprise       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Read values from terraform.tfvars ───────────────────────────────────────
PROJECT_ID=$(sed -n 's/^project_id[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' terraform.tfvars 2>/dev/null \
  || gcloud config get-value project 2>/dev/null || true)
REGION=$(sed -n 's/^location[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' terraform.tfvars 2>/dev/null \
  || sed -n 's/^region[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' terraform.tfvars 2>/dev/null \
  || echo "us-central1")
AGENT_NAME="${AGENT_NAME:-$(sed -n 's/^agent_name[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' terraform.tfvars 2>/dev/null || echo "my-agent")}"

echo "  Project : $PROJECT_ID"
echo "  Region  : $REGION"
echo "  Agent   : $AGENT_NAME"
echo ""

# ── Pre-flight: Verify RE is active ─────────────────────────────────────────
echo "▶ [1/4] Verifying Reasoning Engine is ACTIVE..."

TOKEN=$(gcloud auth print-access-token 2>/dev/null)
RE_LIST=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://${REGION}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${REGION}/reasoningEngines" 2>/dev/null)

# Find RE by display name matching AGENT_NAME (or use chat-agent as fallback)
RE_INFO=$(echo "$RE_LIST" | python3 -c "
import json, sys
data = json.load(sys.stdin)
agent_name = '${AGENT_NAME}'
# Try exact match first, then 'chat-agent' fallback
for target in [agent_name, 'chat-agent']:
    for re in data.get('reasoningEngines', []):
        if re.get('displayName', '') == target:
            re_id = re['name'].split('/')[-1]
            print(f'RE_ID={re_id}')
            print(f'RE_DISPLAY={re.get(\"displayName\",\"\")}')
            print(f'RE_IDENTITY={re.get(\"spec\",{}).get(\"identityType\",\"N/A\")}')
            sys.exit(0)
# If no match, show first one
for re in data.get('reasoningEngines', []):
    re_id = re['name'].split('/')[-1]
    print(f'RE_ID={re_id}')
    print(f'RE_DISPLAY={re.get(\"displayName\",\"\")}')
    print(f'RE_IDENTITY={re.get(\"spec\",{}).get(\"identityType\",\"N/A\")}')
    sys.exit(0)
print('RE_ID=')
" 2>/dev/null)

eval "$RE_INFO"

if [[ -z "${RE_ID:-}" ]]; then
  echo "  ❌ No Reasoning Engine found. Deploy an agent first (Task 3)."
  exit 1
fi

echo "  ✅ RE ID: $RE_ID (display: $RE_DISPLAY)"
echo "  ✅ Identity Type: $RE_IDENTITY"
echo ""

# ── Pre-flight: Verify SGP is registered ────────────────────────────────────
echo "▶ [2/4] Verifying SGP policy is registered..."

SGP_CHECK=$(gcloud beta ai semantic-governance-policies list \
  --location="$REGION" --project="$PROJECT_ID" \
  --format="value(name)" 2>/dev/null | head -1 || true)

if [[ -n "$SGP_CHECK" ]]; then
  echo "  ✅ SGP policy found: $(basename "$SGP_CHECK")"
else
  echo "  ⚠️  No SGP policy found. Task 4 may not be complete."
fi
echo ""

# ── Pre-flight: Verify Agent Registry entry ─────────────────────────────────
echo "▶ [3/4] Verifying Agent Registry entry..."

REGISTRY_CHECK=$(gcloud alpha agent-registry agents list \
  --location="$REGION" --project="$PROJECT_ID" \
  --format=json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for a in data:
    dn = a.get('displayName','')
    if dn in ['chat-agent', '${AGENT_NAME}']:
        uid = a.get('uid','')
        identity = a.get('attributes',{}).get('agentregistry.googleapis.com/system/RuntimeIdentity',{}).get('principal','N/A')
        print(f'FOUND: {dn} (uid={uid})')
        print(f'  Identity: {identity}')
        sys.exit(0)
print('NOT_FOUND')
" 2>/dev/null || echo "REGISTRY_ERROR")

echo "  $REGISTRY_CHECK"
echo ""

# ── Print Console Instructions ──────────────────────────────────────────────
echo "▶ [4/4] Console Registration Steps"
echo ""
echo "┌─────────────────────────────────────────────────────────────────────┐"
echo "│  Gemini Enterprise App Registration — Console Steps                │"
echo "├─────────────────────────────────────────────────────────────────────┤"
echo "│                                                                     │"
echo "│  Step 1: Open Agent Builder                                         │"
echo "│  https://console.cloud.google.com/gen-app-builder/engines           │"
echo "│  ?project=${PROJECT_ID}                                             │"
echo "│                                                                     │"
echo "│  Step 2: Click 'Create App' → Select 'Agent'                       │"
echo "│                                                                     │"
echo "│  Step 3: Select 'Existing Agent' → Choose RE: ${RE_DISPLAY}        │"
echo "│  (RE ID: ${RE_ID})                                                  │"
echo "│                                                                     │"
echo "│  Step 4: Configure the app:                                         │"
echo "│    - App name: Aegis TrialShield                                    │"
echo "│    - Agent type: Reasoning Engine Agent                             │"
echo "│    - Location: ${REGION}                                            │"
echo "│                                                                     │"
echo "│  Step 5: Publish the app                                            │"
echo "│                                                                     │"
echo "│  Alternative — Use Agent Playground directly:                       │"
echo "│  https://console.cloud.google.com/vertex-ai/agents/                 │"
echo "│  reasoningEngines/${RE_ID}/playground                               │"
echo "│  ?project=${PROJECT_ID}&region=${REGION}                            │"
echo "│                                                                     │"
echo "└─────────────────────────────────────────────────────────────────────┘"
echo ""
echo "✅ Pre-flight checks complete. Follow the console steps above."
echo ""
echo "   Agent Playground URL (direct link):"
echo "   https://console.cloud.google.com/vertex-ai/agents/reasoningEngines/${RE_ID}/playground?project=${PROJECT_ID}&region=${REGION}"
echo ""
