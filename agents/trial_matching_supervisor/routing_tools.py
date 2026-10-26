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

"""Routing and perimeter interceptor tools for Trial Matching Supervisor.

TASK 1: HIPAA De-Identification & GINA Title II Isolation Interceptor.
TASK 5: Downscoped IAM OIDC service token validation and calling permissions.
"""

from __future__ import annotations

import logging
from typing import Any

from app.contracts import ClinicalIntakeEnvelope
from lego_blocks.block_1_hipaa_gina_rules import (
    sanitize_hipaa_pii,
    quarantine_gina_germline_data,
)
from lego_blocks.block_6_oidc_auth_guard import verify_oidc_service_token

logger = logging.getLogger(__name__)


def intercept_and_deidentify_intake(
    patient_id: str,
    raw_clinical_notes: str,
    trial_id: str = "NCT-AEGIS-001",
) -> dict[str, Any]:
    """Intercepts raw intake text at the security perimeter.

    Sanitizes HIPAA Safe Harbor direct identifiers and quarantines GINA Title II
    hereditary risk markers before distributing work to domain sub-agents.
    """
    # Step 1: Scrub HIPAA PII (SSN, MRN, Name, DOB, Street Address)
    hipaa_clean, has_pii = sanitize_hipaa_pii(raw_clinical_notes)

    # Step 2: Quarantine GINA germline markers (BRCA1/2, PALB2, Lynch, etc.)
    fully_sanitized, quarantined_markers, has_germline = quarantine_gina_germline_data(hipaa_clean)

    # Step 3: Build the ClinicalIntakeEnvelope
    envelope = ClinicalIntakeEnvelope(
        patient_id=patient_id,
        trial_id=trial_id,
        raw_text=raw_clinical_notes,
        sanitized_text=fully_sanitized,
        sanitized_clinical_notes=fully_sanitized,
        has_pii_violation=has_pii,
        pii_redacted=has_pii,
        has_gina_violation=has_germline,
        gina_quarantined=has_germline,
        quarantined_germline_markers=quarantined_markers,
    )

    return {
        "envelope": envelope.model_dump(),
        "somatic_notes_for_genomics": fully_sanitized,
        "patient_id": patient_id,
        "trial_id": trial_id,
    }


def verify_mesh_caller_authorization(
    token: str,
    expected_target: str,
) -> dict[str, Any]:
    """Validates downscoped IAM OIDC service token and caller permissions."""
    return verify_oidc_service_token(token, expected_target)
