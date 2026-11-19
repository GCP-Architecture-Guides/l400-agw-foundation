#!/usr/bin/env bash
# =============================================================================
# discover_lab5_resources.sh — Auto-discover Lab 5 deployed resources
#
# Discovers Reasoning Engines, Cloud Run services, and service accounts
# deployed during Lab 5 (Aegis TrialShield agent mesh).
#
# Usage:
#   ./scripts/discover_lab5_resources.sh --project YOUR_PROJECT_ID [--region us-central1]
#
# Outputs:
#   - lab5_resources.json  (machine-readable summary)
#   - Human-readable table to stdout
#
# Exit codes:
#   0  All required resources found and healthy
#   1  One or more required resources missing or unhealthy
# =============================================================================
set -euo pipefail

# ── Color helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Defaults ─────────────────────────────────────────────────────────────────
PROJECT_ID=""
REGION="us-central1"
OUTPUT_FILE="lab5_resources.json"

# ── Expected resources ───────────────────────────────────────────────────────
RE_DISPLAY_NAME="trial_matching_supervisor"
EXPECTED_SERVICES=("genomic-biomarker" "pharmacovigilance" "clinical-cohort" "trial-synthesizer")
EXPECTED_SAS=("sa-matching-supervisor" "sa-genomic-biomarker" "sa-pharmacovigilance" "sa-clinical-cohort" "sa-trial-synthesizer" "sa-legacy-god-mode")

# ── Parse arguments ──────────────────────────────────────────────────────────
usage() {
  echo "Usage: $0 --project PROJECT_ID [--region REGION] [--output FILE]"
  echo ""
  echo "  --project   GCP project ID (required)"
  echo "  --region    GCP region (default: us-central1)"
  echo "  --output    Output JSON file (default: lab5_resources.json)"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)  PROJECT_ID="$2"; shift 2 ;;
    --region)   REGION="$2"; shift 2 ;;
    --output)   OUTPUT_FILE="$2"; shift 2 ;;
    -h|--help)  usage ;;
    *)          echo "Unknown argument: $1"; usage ;;
  esac
done

if [[ -z "$PROJECT_ID" ]]; then
  echo -e "${RED}ERROR: --project is required${NC}"
  usage
fi

echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}  Lab 5 Resource Discovery — Aegis TrialShield${NC}"
echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Project:  ${BOLD}${PROJECT_ID}${NC}"
echo -e "  Region:   ${BOLD}${REGION}${NC}"
echo ""

ERRORS=0

# ── Helper: print status ────────────────────────────────────────────────────
print_status() {
  local label="$1"
  local status="$2"
  if [[ "$status" == "OK" ]]; then
    printf "  %-45s ${GREEN}✅ %s${NC}\n" "$label" "$status"
  elif [[ "$status" == "WARN" || "$status" == "SKIP" ]]; then
    printf "  %-45s ${YELLOW}⚠️  %s${NC}\n" "$label" "$status"
  else
    printf "  %-45s ${RED}❌ %s${NC}\n" "$label" "$status"
    ((ERRORS++)) || true
  fi
}

# =============================================================================
# 1. Discover Reasoning Engines
# =============================================================================
echo -e "${BOLD}▸ Discovering Reasoning Engines...${NC}"

TOKEN=$(gcloud auth print-access-token 2>/dev/null) || {
  echo -e "${RED}  Failed to get access token. Run: gcloud auth login${NC}"
  TOKEN=""
}

RE_API_RESPONSE=""
if [[ -n "$TOKEN" ]]; then
  RE_API_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/reasoningEngines" 2>/dev/null) || true
fi

# Convert REST response to a JSON array matching gcloud format
RE_LIST_JSON=$(echo "$RE_API_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    engines = data.get('reasoningEngines', [])
    print(json.dumps(engines))
except:
    print('[]')
" 2>/dev/null) || RE_LIST_JSON="[]"

if [[ "$RE_LIST_JSON" == "[]" && -z "$RE_API_RESPONSE" ]]; then
  echo -e "${RED}  Failed to list Reasoning Engines. Check permissions & APIs.${NC}"
  ((ERRORS++)) || true
fi

RE_COUNT=$(echo "$RE_LIST_JSON" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo -e "  Found ${BOLD}${RE_COUNT}${NC} Reasoning Engine(s) in ${REGION}"

# Find the supervisor RE by displayName
RE_ID=""
RE_STATE=""
RE_NAME_FULL=""
RE_CREATE_TIME=""

if [[ "$RE_COUNT" -gt 0 ]]; then
  RE_MATCH=$(echo "$RE_LIST_JSON" | python3 -c "
import sys, json
engines = json.load(sys.stdin)
for e in engines:
    if e.get('displayName','') == '${RE_DISPLAY_NAME}':
        # Extract numeric ID from resource name
        name = e.get('name','')
        rid = name.split('/')[-1] if '/' in name else name
        state = e.get('state', 'ACTIVE')  # REST API omits state; if listed, it's active
        create_time = e.get('createTime','')
        print(f'{rid}|{state}|{name}|{create_time}')
        break
" 2>/dev/null) || true

  if [[ -n "$RE_MATCH" ]]; then
    IFS='|' read -r RE_ID RE_STATE RE_NAME_FULL RE_CREATE_TIME <<< "$RE_MATCH"
    print_status "RE: ${RE_DISPLAY_NAME} (ID: ${RE_ID})" \
      "$( [[ "$RE_STATE" == "ACTIVE" ]] && echo "OK" || echo "UNHEALTHY ($RE_STATE)" )"
  else
    print_status "RE: ${RE_DISPLAY_NAME}" "NOT FOUND"
  fi

  # List all REs for reference
  echo ""
  echo -e "  ${CYAN}All Reasoning Engines:${NC}"
  echo "$RE_LIST_JSON" | python3 -c "
import sys, json
engines = json.load(sys.stdin)
for e in engines:
    name = e.get('name','')
    rid = name.split('/')[-1] if '/' in name else name
    dn = e.get('displayName','N/A')
    state = e.get('state','ACTIVE')  # REST API omits state; if listed, it's active
    marker = ' ◄── TARGET' if dn == '${RE_DISPLAY_NAME}' else ''
    print(f'    {dn:40s}  ID: {rid:25s}  State: {state}{marker}')
" 2>/dev/null || true
else
  print_status "RE: ${RE_DISPLAY_NAME}" "NO ENGINES FOUND"
fi

echo ""

# =============================================================================
# 2. Discover Cloud Run Services
# =============================================================================
echo -e "${BOLD}▸ Discovering Cloud Run Services...${NC}"

RUN_LIST_JSON=$(gcloud run services list \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --format=json 2>/dev/null) || {
  echo -e "${RED}  Failed to list Cloud Run services. Check permissions & APIs.${NC}"
  RUN_LIST_JSON="[]"
  ((ERRORS++)) || true
}

RUN_COUNT=$(echo "$RUN_LIST_JSON" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo -e "  Found ${BOLD}${RUN_COUNT}${NC} Cloud Run service(s) in ${REGION}"
echo ""

# Build associative-style data for each expected service
declare -a SVC_NAMES=()
declare -a SVC_URLS=()
declare -a SVC_SAS=()
declare -a SVC_STATUSES=()
declare -a SVC_HEALTHY=()

for expected_svc in "${EXPECTED_SERVICES[@]}"; do
  SVC_INFO=$(echo "$RUN_LIST_JSON" | python3 -c "
import sys, json
services = json.load(sys.stdin)
for s in services:
    meta = s.get('metadata', {})
    name = meta.get('name', s.get('name',''))
    # Cloud Run v2 format uses 'name' at top level as full resource path
    if isinstance(name, str) and '/' in name:
        name = name.split('/')[-1]
    if name == '${expected_svc}':
        url = s.get('status',{}).get('url', s.get('uri',''))
        sa = s.get('spec',{}).get('template',{}).get('spec',{}).get('serviceAccountName','')
        if not sa:
            # v2 format
            tmpl = s.get('template',{})
            sa = tmpl.get('serviceAccount','')
        # Health: check ready condition
        healthy = 'UNKNOWN'
        conditions = s.get('status',{}).get('conditions', s.get('conditions',[]))
        if conditions:
            for c in (conditions if isinstance(conditions, list) else []):
                ctype = c.get('type','')
                cstatus = c.get('status','')
                if ctype == 'Ready':
                    healthy = 'HEALTHY' if cstatus == 'True' else 'UNHEALTHY'
                    break
        print(f'{name}|{url}|{sa}|{healthy}')
        break
" 2>/dev/null) || true

  if [[ -n "$SVC_INFO" ]]; then
    IFS='|' read -r svc_name svc_url svc_sa svc_health <<< "$SVC_INFO"
    SVC_NAMES+=("$svc_name")
    SVC_URLS+=("$svc_url")
    SVC_SAS+=("$svc_sa")
    SVC_STATUSES+=("FOUND")
    SVC_HEALTHY+=("$svc_health")
    print_status "Cloud Run: ${expected_svc}" \
      "$( [[ "$svc_health" == "HEALTHY" ]] && echo "OK" || echo "$svc_health" )"
  else
    SVC_NAMES+=("$expected_svc")
    SVC_URLS+=("")
    SVC_SAS+=("")
    SVC_STATUSES+=("NOT FOUND")
    SVC_HEALTHY+=("MISSING")
    print_status "Cloud Run: ${expected_svc}" "NOT FOUND"
  fi
done

echo ""

# =============================================================================
# 3. Discover Service Accounts
# =============================================================================
echo -e "${BOLD}▸ Discovering Service Accounts...${NC}"

SA_LIST_JSON=$(gcloud iam service-accounts list \
  --project="$PROJECT_ID" \
  --format=json 2>/dev/null) || {
  echo -e "${RED}  Failed to list service accounts.${NC}"
  SA_LIST_JSON="[]"
  ((ERRORS++)) || true
}

declare -a FOUND_SAS=()
declare -a FOUND_SA_EMAILS=()

for expected_sa in "${EXPECTED_SAS[@]}"; do
  SA_EMAIL=$(echo "$SA_LIST_JSON" | python3 -c "
import sys, json
accounts = json.load(sys.stdin)
for a in accounts:
    email = a.get('email','')
    display = a.get('displayName','')
    # Match by prefix in email (before @)
    local_part = email.split('@')[0] if '@' in email else ''
    if local_part == '${expected_sa}':
        print(email)
        break
" 2>/dev/null) || true

  if [[ -n "$SA_EMAIL" ]]; then
    FOUND_SAS+=("$expected_sa")
    FOUND_SA_EMAILS+=("$SA_EMAIL")
    print_status "SA: ${expected_sa}" "OK"
  else
    FOUND_SAS+=("$expected_sa")
    FOUND_SA_EMAILS+=("")
    print_status "SA: ${expected_sa}" "NOT FOUND"
  fi
done

echo ""

# =============================================================================
# 4. Generate JSON summary
# =============================================================================
echo -e "${BOLD}▸ Generating ${OUTPUT_FILE}...${NC}"

# Build Cloud Run services JSON array
SVC_JSON_ARRAY="["
for i in "${!SVC_NAMES[@]}"; do
  [[ $i -gt 0 ]] && SVC_JSON_ARRAY+=","
  SVC_JSON_ARRAY+=$(python3 -c "
import json
print(json.dumps({
  'name': '${SVC_NAMES[$i]}',
  'url': '${SVC_URLS[$i]}',
  'serviceAccount': '${SVC_SAS[$i]}',
  'status': '${SVC_STATUSES[$i]}',
  'healthy': '${SVC_HEALTHY[$i]}'
}))
" 2>/dev/null)
done
SVC_JSON_ARRAY+="]"

# Build service accounts JSON array
SA_JSON_ARRAY="["
for i in "${!FOUND_SAS[@]}"; do
  [[ $i -gt 0 ]] && SA_JSON_ARRAY+=","
  SA_JSON_ARRAY+=$(python3 -c "
import json
print(json.dumps({
  'name': '${FOUND_SAS[$i]}',
  'email': '${FOUND_SA_EMAILS[$i]}',
  'found': $([ -n '${FOUND_SA_EMAILS[$i]}' ] && echo 'True' || echo 'False')
}))
" 2>/dev/null)
done
SA_JSON_ARRAY+="]"

# Write full JSON — pass pre-built JSON arrays via env vars to avoid
# pasting JSON true/false into Python source (NameError).
SVC_JSON="$SVC_JSON_ARRAY" SA_JSON="$SA_JSON_ARRAY" python3 -c "
import json, datetime, os
data = {
  'discoveredAt': datetime.datetime.utcnow().isoformat() + 'Z',
  'projectId': '${PROJECT_ID}',
  'region': '${REGION}',
  'reasoningEngine': {
    'displayName': '${RE_DISPLAY_NAME}',
    'id': '${RE_ID}',
    'fullName': '${RE_NAME_FULL}',
    'state': '${RE_STATE}',
    'createTime': '${RE_CREATE_TIME}',
    'found': $([ -n "$RE_ID" ] && echo 'True' || echo 'False')
  },
  'cloudRunServices': json.loads(os.environ.get('SVC_JSON', '[]')),
  'serviceAccounts': json.loads(os.environ.get('SA_JSON', '[]')),
  'healthy': $([ "$ERRORS" -eq 0 ] && echo 'True' || echo 'False'),
  'errorCount': ${ERRORS}
}
with open('${OUTPUT_FILE}', 'w') as f:
  json.dump(data, f, indent=2)
print(json.dumps(data, indent=2))
" 2>/dev/null

echo ""

# =============================================================================
# 5. Human-readable summary table
# =============================================================================
echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}  Lab 5 Resource Discovery Summary${NC}"
echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo ""
printf "  ${BOLD}%-20s %-30s %-15s${NC}\n" "Resource Type" "Name / ID" "Status"
printf "  %-20s %-30s %-15s\n" "────────────────────" "──────────────────────────────" "───────────────"

# RE row
if [[ -n "$RE_ID" ]]; then
  re_status=$([[ "$RE_STATE" == "ACTIVE" ]] && echo "✅ ACTIVE" || echo "❌ $RE_STATE")
  printf "  %-20s %-30s %-15s\n" "Reasoning Engine" "${RE_DISPLAY_NAME} (${RE_ID})" "$re_status"
else
  printf "  %-20s %-30s %-15s\n" "Reasoning Engine" "${RE_DISPLAY_NAME}" "❌ NOT FOUND"
fi

# Cloud Run rows
for i in "${!SVC_NAMES[@]}"; do
  if [[ "${SVC_STATUSES[$i]}" == "FOUND" ]]; then
    svc_status=$([[ "${SVC_HEALTHY[$i]}" == "HEALTHY" ]] && echo "✅ HEALTHY" || echo "⚠️  ${SVC_HEALTHY[$i]}")
  else
    svc_status="❌ NOT FOUND"
  fi
  printf "  %-20s %-30s %-15s\n" "Cloud Run" "${SVC_NAMES[$i]}" "$svc_status"
done

# SA rows
for i in "${!FOUND_SAS[@]}"; do
  if [[ -n "${FOUND_SA_EMAILS[$i]}" ]]; then
    printf "  %-20s %-30s %-15s\n" "Service Account" "${FOUND_SAS[$i]}" "✅ FOUND"
  else
    printf "  %-20s %-30s %-15s\n" "Service Account" "${FOUND_SAS[$i]}" "❌ NOT FOUND"
  fi
done

echo ""
printf "  %-20s %-30s\n" "────────────────────" "──────────────────────────────"

if [[ $ERRORS -eq 0 ]]; then
  echo -e "  ${GREEN}${BOLD}All Lab 5 resources discovered and healthy ✅${NC}"
  echo -e "  Output: ${OUTPUT_FILE}"
  echo ""
  exit 0
else
  echo -e "  ${RED}${BOLD}${ERRORS} issue(s) found — Lab 5 may not be fully deployed ❌${NC}"
  echo -e "  Output: ${OUTPUT_FILE}"
  echo ""
  exit 1
fi
