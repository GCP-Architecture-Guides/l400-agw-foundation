#!/bin/bash
# ============================================================================
# Lab 2 Pre-Flight Check
# ============================================================================
# Verifies whether Lab 1 setup is complete before starting Lab 2.
# If all checks pass, skip Task 0 and proceed directly to Task 1.
#
# Usage:
#   ./preflight_check.sh [PROJECT_ID]
#
# Exit codes:
#   0 = All checks passed — skip Task 0, proceed to Task 1
#   1 = Some checks failed — run Task 0 setup first
# ============================================================================

set -uo pipefail

PROJECT_ID="${1:-${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null)}}"
PASS=0
FAIL=0
SKIP_TASK0=true

check() {
  local name="$1" result="$2"
  if [ "$result" = "true" ]; then
    echo "  ✅ $name"
    PASS=$((PASS + 1))
  else
    echo "  ❌ $name"
    FAIL=$((FAIL + 1))
    SKIP_TASK0=false
  fi
}

echo ""
echo "========================================"
echo "  Lab 2 Pre-Flight Check"
echo "  Project: ${PROJECT_ID:-<not set>}"
echo "========================================"
echo ""

# ---------------------------------------------------------------------------
# Layer 1: Repository Structure
# ---------------------------------------------------------------------------
echo "📁 Layer 1: Repository"
check "foundation/ directory exists" \
  "$([ -d foundation ] && echo true || echo false)"
check "Terraform files present (01_apis.tf, variables.tf)" \
  "$([ -f foundation/01_apis.tf ] && [ -f foundation/variables.tf ] && echo true || echo false)"
check "Chat agent for RE deployment exists" \
  "$([ -f foundation/agents/chat-agent/agent.py ] && echo true || echo false)"
check "Deploy script exists" \
  "$([ -f foundation/scripts/deploy_chat_agent.sh ] && echo true || echo false)"
echo ""

# ---------------------------------------------------------------------------
# Layer 2: Python Environment
# ---------------------------------------------------------------------------
echo "🐍 Layer 2: Python Environment"
check "Virtual environment (.venv) exists" \
  "$([ -f .venv/bin/python ] || [ -f .venv/Scripts/python.exe ] && echo true || echo false)"
echo ""

# ---------------------------------------------------------------------------
# Layer 3: Environment Configuration
# ---------------------------------------------------------------------------
echo "⚙️  Layer 3: Environment Config"
check ".env file exists" \
  "$([ -f .env ] && echo true || echo false)"
if [ -f .env ]; then
  HAS_VALID_PROJECT=$(grep -qE '^GCP_PROJECT_ID=.+' .env 2>/dev/null && \
    ! grep -q 'YOUR_PROJECT_ID\|prod-proj-ge\|PLACEHOLDER' .env 2>/dev/null && \
    echo true || echo false)
  check ".env has valid project ID (not placeholder)" "$HAS_VALID_PROJECT"
fi
echo ""

# ---------------------------------------------------------------------------
# Layer 4: Agent Code (Lab 1 Completion Check)
# ---------------------------------------------------------------------------
echo "🤖 Layer 4: Agent Code (Lab 1 completion)"

# Check if agents are implemented (not None stubs from challenge template)
if [ -f agents/trial_matching_supervisor/agent.py ]; then
  check "Supervisor agent implemented (not stub)" \
    "$(grep -q 'root_agent = None' agents/trial_matching_supervisor/agent.py 2>/dev/null \
       && echo false || echo true)"
else
  check "Supervisor agent file exists" "false"
fi

if [ -f agents/clinical_cohort/cohort_agent.py ]; then
  check "Cohort agent implemented" \
    "$(grep -q 'cohort_agent = None' agents/clinical_cohort/cohort_agent.py 2>/dev/null \
       && echo false || echo true)"
else
  check "Cohort agent file exists" "false"
fi

if [ -f agents/genomic_biomarker/biomarker_agent.py ]; then
  check "Genomic agent implemented" \
    "$(grep -q 'genomic_agent = None' agents/genomic_biomarker/biomarker_agent.py 2>/dev/null \
       && echo false || echo true)"
else
  check "Genomic agent file exists" "false"
fi

if [ -f agents/pharmacovigilance/pv_agent.py ]; then
  check "Pharmacovigilance agent implemented" \
    "$(grep -q 'pv_agent = None' agents/pharmacovigilance/pv_agent.py 2>/dev/null \
       && echo false || echo true)"
else
  check "Pharmacovigilance agent file exists" "false"
fi

if [ -f agents/trial_eligibility_synthesizer/synthesizer_agent.py ]; then
  check "Synthesizer agent implemented" \
    "$(grep -q 'synthesizer_agent = None' agents/trial_eligibility_synthesizer/synthesizer_agent.py 2>/dev/null \
       && echo false || echo true)"
else
  check "Synthesizer agent file exists" "false"
fi
echo ""

# ---------------------------------------------------------------------------
# Layer 5: GCP APIs
# ---------------------------------------------------------------------------
echo "☁️  Layer 5: GCP APIs"
if [ -n "$PROJECT_ID" ]; then
  ENABLED=$(gcloud services list --enabled --project="$PROJECT_ID" \
            --format="value(config.name)" 2>/dev/null || echo "")
  if [ -n "$ENABLED" ]; then
    for api in compute.googleapis.com \
               modelarmor.googleapis.com \
               networksecurity.googleapis.com \
               aiplatform.googleapis.com \
               dlp.googleapis.com \
               iap.googleapis.com; do
      check "$api" "$(echo "$ENABLED" | grep -q "$api" && echo true || echo false)"
    done
  else
    echo "  ⚠️  Could not list APIs — check gcloud auth"
    SKIP_TASK0=false
  fi
else
  echo "  ⚠️  No PROJECT_ID set — skipping API check"
  echo "     Pass as argument: ./preflight_check.sh YOUR_PROJECT_ID"
  echo "     Or set: export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID"
  SKIP_TASK0=false
fi

echo ""
echo "========================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "========================================"
echo ""

if [ "$SKIP_TASK0" = true ]; then
  echo "✅ All checks passed — SKIP Task 0"
  echo "   Proceed directly to Task 1 (Configure terraform.tfvars)"
  echo ""
  exit 0
else
  echo "❌ Some checks failed — RUN Task 0 setup before proceeding"
  echo ""
  echo "   Quick fix:"
  echo "   1. Clone repo:  git clone https://github.com/GCP-Architecture-Guides/l400-agw-foundation.git"
  echo "   2. Install deps: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  echo "   3. Configure:   cp .env.example .env && edit .env with your project ID"
  echo "   4. Complete Lab 1 agent challenges first"
  echo "   5. Enable APIs:  see Task 1 in the lab guide"
  echo ""
  exit 1
fi
