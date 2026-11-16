#!/bin/bash

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
#
# This code is for PoC environment only.
# This demo code is not built for production workload.

# Auto-provisions the SGP Engine and extracts the dynamic pscServiceAttachment string.
# Returns a JSON object required by Terraform external data source.
#
# IMPORTANT: This script is called by Terraform data.external — it MUST:
#   1. Output valid JSON to stdout on ALL code paths (success AND failure)
#   2. Exit 0 on ALL code paths (exit 1 causes Terraform plan to abort)
#   3. Not write non-JSON to stdout (stderr is fine for diagnostics)

set -uo pipefail
# NOTE: -e is intentionally omitted — we handle errors explicitly to ensure
# valid JSON output and exit 0 for Terraform data.external compatibility.

PROJECT_ID=$1
LOCATION=$2

# Check jq availability — required for valid JSON output
if ! command -v jq &>/dev/null; then
  echo '{"error":"jq is not installed. Install jq and re-run terraform apply."}' >&2
  # Return valid JSON even on error — Terraform data.external needs it
  echo '{"psc_service_attachment":"ERROR_JQ_NOT_INSTALLED"}'
  exit 0
fi

# Kick off the Google-managed provisioning (this command is asynchronous internally if the VPC networking is not yet ready)
# We omit gateway-config to just trigger the judge service creation
gcloud beta ai semantic-governance-policy-engine update \
  --location="$LOCATION" \
  --project="$PROJECT_ID" >/dev/null 2>&1 || true


# Poll the describe command until the Google judge service exposes the PSC attachment URI
# Timeout after 20 minutes (1200 seconds / 15 seconds = 80 attempts)
MAX_ATTEMPTS=80
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  # Extract the pscServiceAttachment string
  ATTACHMENT=$(gcloud beta ai semantic-governance-policy-engine describe \
    --location="$LOCATION" \
    --project="$PROJECT_ID" \
    --format="value(pscServiceAttachment)" 2>/dev/null)
  
  if [ -n "$ATTACHMENT" ]; then
    # Return valid JSON for Terraform to parse
    jq -n --arg psc "$ATTACHMENT" '{"psc_service_attachment":$psc}'
    exit 0
  fi
  
  sleep 15
  ATTEMPT=$((ATTEMPT + 1))
done

# Timeout — return valid JSON with error info AND exit 0 (not exit 1).
# Terraform data.external treats exit 1 as a hard error that aborts the entire
# plan. With exit 0 + an error sentinel value, Terraform can still complete the
# plan phase and the user can re-run after the SGP engine finishes provisioning.
echo "ERROR: Timed out waiting for SGP Engine pscServiceAttachment after $((MAX_ATTEMPTS * 15))s" >&2
jq -n '{"psc_service_attachment":"ERROR_TIMEOUT_WAITING_FOR_SGP_ENGINE"}'
exit 0
