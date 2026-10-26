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

"""Clinical Cohort tools for functional performance scoring and FHIR lab normalization."""

from __future__ import annotations

import logging
from typing import Any

from lego_blocks.block_3_fhir_lab_normalizer import (
    extract_ecog_status,
    normalize_fhir_renal_labs,
)

logger = logging.getLogger(__name__)


def evaluate_clinical_cohort(
    clinical_notes: str,
    creatinine_value: float | None = None,
    creatinine_unit: str = "mg/dL",
    unparseable_labs: bool = False,
) -> dict[str, Any]:
    """Evaluates patient ECOG fitness and renal laboratory acceptability.

    Combines ECOG extraction (zero-safe) and FHIR R4 lab normalization
    from block_3 into a unified ClinicalCohortReport.
    """
    # Step 1: Extract ECOG score (zero-safe)
    ecog_result = extract_ecog_status(clinical_notes)
    ecog_score = ecog_result.get("ecog_score", 1)
    ecog_conf = ecog_result.get("confidence", 0.90)

    # Step 2: Normalize renal labs if provided
    lab_result = None
    renal_status = "NOT_ASSESSED"
    normalized_creatinine = None
    normalized_unit = None
    lab_confidence = 0.95

    if creatinine_value is not None:
        lab_result = normalize_fhir_renal_labs(
            lab_type="serum_creatinine",
            raw_value=creatinine_value,
            raw_unit=creatinine_unit,
            unparseable_labs=unparseable_labs,
        )
        renal_status = lab_result.get("renal_status", "NOT_ASSESSED")
        normalized_creatinine = lab_result.get("normalized_value")
        normalized_unit = lab_result.get("normalized_unit")
        lab_confidence = lab_result.get("confidence", 0.95)
        unparseable_labs = lab_result.get("unparseable_labs", unparseable_labs)

    # Step 3: Determine cohort eligibility
    ecog_eligible = ecog_score <= 2
    renal_eligible = renal_status in ("ACCEPTABLE", "NOT_ASSESSED")
    cohort_eligible = ecog_eligible and renal_eligible and not unparseable_labs

    overall_confidence = min(ecog_conf, lab_confidence)
    cohort_status = "COHORT_ELIGIBLE" if cohort_eligible else "COHORT_INELIGIBLE"

    if unparseable_labs:
        cohort_status = "INCONCLUSIVE"
        overall_confidence = min(overall_confidence, 0.70)

    return {
        "patient_id": "UNKNOWN",
        "trial_id": "NCT-AEGIS-001",
        "cohort_status": cohort_status,
        "cohort_eligible": cohort_eligible,
        "ecog_score": ecog_score,
        "ambulatory_status": ecog_result.get("ambulatory_status", "UNKNOWN"),
        "ecog_confidence": ecog_conf,
        "renal_status": renal_status,
        "normalized_serum_creatinine": normalized_creatinine,
        "normalized_unit": normalized_unit,
        "creatinine_mg_dl": creatinine_value,
        "unparseable_labs": unparseable_labs,
        "confidence": round(overall_confidence, 2),
        "lab_normalizations": lab_result or {},
        "clinical_summary": (
            f"ECOG {ecog_score} ({ecog_result.get('ambulatory_status', 'UNKNOWN')}), "
            f"Renal: {renal_status}. "
            f"{'Unparseable labs flagged for HITL.' if unparseable_labs else 'All labs normalized.'}"
        ),
        "details": ecog_result.get("clinical_note", ""),
    }
