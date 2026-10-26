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

"""Pharmacovigilance tools for washout calculation and adverse event surveillance."""

from __future__ import annotations

import logging
from typing import Any

from lego_blocks.block_2_fastmcp_washout import calculate_drug_clearance_fastmcp
from lego_blocks.block_4_meddra_adverse_events import evaluate_adverse_event_safety

logger = logging.getLogger(__name__)


def evaluate_patient_pharmacovigilance(
    drug_name: str,
    days_since_last_dose: int,
    required_washout_days: int | None = None,
    clinical_history: str = "",
) -> dict[str, Any]:
    """Evaluates drug washout clearance and adverse event safety.

    Combines FastMCP washout calculation (block_2) and MedDRA adverse event
    evaluation (block_4) into a unified PharmacovigilanceReport.
    """
    # Step 1: Calculate drug washout clearance
    washout_result = calculate_drug_clearance_fastmcp(
        drug_name=drug_name,
        days_since_last_dose=days_since_last_dose,
        required_washout_days=required_washout_days,
    )

    # Step 2: Evaluate adverse events from clinical history
    ae_result = evaluate_adverse_event_safety(clinical_history) if clinical_history else {
        "matched_adverse_events": [],
        "ctcae_grade": None,
        "steroid_taper_detected": False,
        "borderline_safety_flag": False,
        "confidence": 0.95,
        "safety_status": "SAFE",
        "clinical_rationale": "No clinical history provided for adverse event assessment.",
    }

    # Combine confidence: take the minimum
    combined_confidence = min(
        washout_result.get("confidence", 0.95),
        ae_result.get("confidence", 0.95),
    )

    return {
        "patient_id": "UNKNOWN",
        "trial_id": "NCT-AEGIS-001",
        "drug_name": drug_name,
        "prior_therapy": washout_result.get("canonical_drug", drug_name),
        "days_since_last_dose": days_since_last_dose,
        "required_washout_days": washout_result.get("required_washout_days", 28),
        "washout_status": washout_result.get("overall_status", "WASHOUT_SATISFIED"),
        "washout_satisfied": washout_result.get("washout_satisfied", True),
        "washout_period_satisfied": washout_result.get("washout_period_satisfied", True),
        "washout_deficit_days": washout_result.get("washout_deficit_days", 0),
        "confidence": round(combined_confidence, 2),
        "borderline_safety_flag": ae_result.get("borderline_safety_flag", False),
        "ctcae_adverse_events": ae_result.get("matched_adverse_events", []),
        "identified_contraindications": [],
        "clinical_summary": washout_result.get("clinical_rationale", ""),
        "details": ae_result.get("clinical_rationale", ""),
    }
