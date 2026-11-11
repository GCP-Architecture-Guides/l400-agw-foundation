#!/usr/bin/env bash
# Copyright 2026 Google LLC
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

set -euo pipefail

echo "======================================================================"
echo "🚀 Aegis TrialShield Lab: Qwiklabs Environment Bootstrap"
echo "======================================================================"

# -----------------------------------------------------------------------------
# 1. Environment & Project Resolution
# -----------------------------------------------------------------------------
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo "prod-proj-ge")}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
BQ_DATASET_ID="${BQ_DATASET_ID:-meddra_ontology_v26}"

echo "Project ID: ${PROJECT_ID}"
echo "Region:     ${REGION}"
echo "BQ Dataset: ${BQ_DATASET_ID}"
echo "----------------------------------------------------------------------"

# -----------------------------------------------------------------------------
# 2. Enable Required Google Cloud APIs
# -----------------------------------------------------------------------------
echo "Step 1: Enabling Required GCP APIs..."
REQUIRED_APIS=(
    "aiplatform.googleapis.com"
    "run.googleapis.com"
    "bigquery.googleapis.com"
    "iam.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "logging.googleapis.com"
    "monitoring.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    echo "  Checking API: ${api}..."
    if ! gcloud services list --enabled --project="${PROJECT_ID}" --filter="config.name:${api}" --format="value(config.name)" | grep -q "${api}"; then
        echo "    Enabling ${api}..."
        gcloud services enable "${api}" --project="${PROJECT_ID}"
    else
        echo "    Already enabled: ${api}"
    fi
done

# -----------------------------------------------------------------------------
# 3. Provision Least-Privilege IAM Service Accounts & Legacy Audit Account
# -----------------------------------------------------------------------------
echo "----------------------------------------------------------------------"
echo "Step 2: Provisioning IAM Service Accounts (Idempotent)..."

SERVICE_ACCOUNTS=(
    "sa-matching-supervisor:Trial Matching Supervisor Agent Identity"
    "sa-genomic-biomarker:Genomic Biomarker Sub-Agent Identity"
    "sa-pharmacovigilance:Pharmacovigilance Sub-Agent Identity"
    "sa-clinical-cohort:Clinical Cohort Sub-Agent Identity"
    "sa-trial-synthesizer:Trial Eligibility Synthesizer Identity"
    "sa-legacy-god-mode:Legacy Monolithic Over-Permissioned Identity"
)

for sa_entry in "${SERVICE_ACCOUNTS[@]}"; do
    sa_name="${sa_entry%%:*}"
    sa_desc="${sa_entry##*:}"
    sa_email="${sa_name}@${PROJECT_ID}.iam.gserviceaccount.com"

    echo "  Checking Service Account: ${sa_name}..."
    if gcloud iam service-accounts describe "${sa_email}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
        echo "    Already exists: ${sa_email}"
    else
        echo "    Creating: ${sa_email} (${sa_desc})..."
        gcloud iam service-accounts create "${sa_name}" \
            --display-name="${sa_desc}" \
            --project="${PROJECT_ID}"
    fi
done

# -----------------------------------------------------------------------------
# 4. Provision BigQuery meddra_ontology_v26 Dataset
# -----------------------------------------------------------------------------
echo "----------------------------------------------------------------------"
echo "Step 3: Provisioning BigQuery Dataset: ${BQ_DATASET_ID}..."

if bq show --project_id="${PROJECT_ID}" "${BQ_DATASET_ID}" >/dev/null 2>&1; then
    echo "  BigQuery dataset '${BQ_DATASET_ID}' already exists."
else
    echo "  Creating BigQuery dataset '${BQ_DATASET_ID}' in location '${REGION}'..."
    bq mk --project_id="${PROJECT_ID}" --location="${REGION}" --dataset "${BQ_DATASET_ID}"
    echo "  BigQuery dataset '${BQ_DATASET_ID}' created successfully."
fi

# -----------------------------------------------------------------------------
# 5. Deploy TrialShield POC Agent to Vertex AI Agent Runtime
# -----------------------------------------------------------------------------
echo "----------------------------------------------------------------------"
echo "Step 4: Deploying TrialShield POC Agent to Vertex AI Agent Runtime..."

if [ "${SKIP_POC_DEPLOY:-false}" = "true" ]; then
    echo "  SKIP_POC_DEPLOY is set to true; skipping POC Agent deployment."
elif command -v agents-cli >/dev/null 2>&1; then
    echo "  Deploying TrialShield POC Agent via agents-cli..."
    agents-cli deploy \
        --deployment-target agent_runtime \
        --service-name "TrialShield POC Agent" \
        --project "${PROJECT_ID}" \
        --region "${REGION}" \
        --agent-identity \
        --env-vars "GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_ENTERPRISE=true" \
        --no-confirm-project || {
            echo "  ⚠️ Warning: agents-cli deploy completed with warnings or non-fatal status."
        }
else
    echo "  ⚠️ agents-cli tool not found in PATH; skipping automated deployment."
fi

echo "======================================================================"
echo "✅ Qwiklabs Environment Bootstrap Complete!"
echo "======================================================================"
