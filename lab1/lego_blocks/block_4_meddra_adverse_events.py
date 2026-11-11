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

"""Modular Lego Block 4: MedDRA Adverse Event & Pharmacovigilance Safety Guard.

Implements:
1. MedDRA v26 Preferred Term (PT) and System Organ Class (SOC) mapping:
   - Maps clinical terms (e.g., 'immune-mediated pneumonitis', 'colitis', 'nephritis')
     to standardized MedDRA ontology codes.
2. NCI Common Terminology Criteria for Adverse Events (CTCAE v5.0) grading:
   - Detects adverse event severity (Grade 1 through Grade 4).
3. Borderline Safety & Active irAE Detection:
   - Detects active or resolving Grade 2+ immune-related adverse events (irAEs)
     and ongoing corticosteroid tapers (e.g., prednisone taper).
   - Generates 'borderline_safety_flag = True' and drops confidence to 0.79,
     ensuring deterministic escalation to Human-In-The-Loop (HITL) oncologist review!
"""

from __future__ import annotations

import logging
import re
from typing import Any, Final

logger = logging.getLogger(__name__)

# MedDRA Ontology Reference
_MEDDRA_AE_ONTOLOGY: Final[dict[str, dict[str, Any]]] = {
    "pneumonitis": {
        "preferred_term": "Pneumonitis",
        "soc": "Respiratory, thoracic and mediastinal disorders",
        "meddra_code": 10035742,
        "is_immune_mediated": True,
        "monitoring_required": True,
    },
    "immune-mediated pneumonitis": {
        "preferred_term": "Immune-mediated pneumonitis",
        "soc": "Respiratory, thoracic and mediastinal disorders",
        "meddra_code": 10078832,
        "is_immune_mediated": True,
        "monitoring_required": True,
    },
    "colitis": {
        "preferred_term": "Colitis",
        "soc": "Gastrointestinal disorders",
        "meddra_code": 10009887,
        "is_immune_mediated": True,
        "monitoring_required": True,
    },
    "hepatitis": {
        "preferred_term": "Hepatitis",
        "soc": "Hepatobiliary disorders",
        "meddra_code": 10019717,
        "is_immune_mediated": True,
        "monitoring_required": True,
    },
    "nephritis": {
        "preferred_term": "Nephritis",
        "soc": "Renal and urinary disorders",
        "meddra_code": 10029155,
        "is_immune_mediated": True,
        "monitoring_required": True,
    },
    "myocarditis": {
        "preferred_term": "Myocarditis",
        "soc": "Cardiac disorders",
        "meddra_code": 10028606,
        "is_immune_mediated": True,
        "monitoring_required": True,
    },
}


def evaluate_adverse_event_safety(clinical_text: str) -> dict[str, Any]:
    """Analyzes clinician notes for adverse events, CTCAE grading, and safety flags.

    Args:
        clinical_text: Physician examination notes or adverse event documentation.

    Returns:
        Structured safety assessment with borderline flags and confidence ratings.
    """
    text_lower = clinical_text.lower()

    # 1. Detect steroid taper or ongoing immunosuppressive therapy
    steroid_taper_detected = bool(
        re.search(r"\b(?:steroid|prednisone|dexamethasone|methylprednisolone)\s+taper\b", text_lower)
        or "on prednisone taper" in text_lower
        or "on steroid taper" in text_lower
    )

    # 2. Detect CTCAE Grade
    grade_match = re.search(r"\bgrade\s*([1-4])\b", text_lower)
    ctcae_grade = int(grade_match.group(1)) if grade_match else None

    # 3. Match MedDRA terms
    matched_events: list[dict[str, Any]] = []
    is_irAE = False

    for term, meta in _MEDDRA_AE_ONTOLOGY.items():
        if term in text_lower:
            matched_events.append({
                "raw_term": term,
                "preferred_term": meta["preferred_term"],
                "soc": meta["soc"],
                "meddra_code": meta["meddra_code"],
                "is_immune_mediated": meta["is_immune_mediated"],
            })
            if meta["is_immune_mediated"]:
                is_irAE = True

    # 4. Determine Borderline Safety Flag and Confidence
    # Grade 2+ immune adverse events or active steroid tapers require oncologist oversight
    borderline_safety_flag = False
    confidence = 0.95
    safety_status = "SAFE"
    rationale = "No active high-grade toxicities or immunosuppressive tapers identified."

    if (ctcae_grade is not None and ctcae_grade >= 2 and is_irAE) or (is_irAE and steroid_taper_detected):
        borderline_safety_flag = True
        confidence = 0.79  # Intentionally < 0.85 to trigger HITL gatekeeper!
        safety_status = "BORDERLINE_SAFETY_REVIEW"
        rationale = (
            f"Active/resolving immune-related adverse event detected (Grade {ctcae_grade or 'unspecified'}) "
            f"with steroid taper status: {steroid_taper_detected}. Requires oncologist HITL evaluation."
        )
    elif ctcae_grade is not None and ctcae_grade >= 3:
        borderline_safety_flag = True
        confidence = 0.70
        safety_status = "UNSAFE_HIGH_GRADE_TOXICITY"
        rationale = f"Severe Grade {ctcae_grade} toxicity detected. Patient safety risk."
    elif matched_events:
        safety_status = "MONITORING_REQUIRED"
        rationale = f"Grade {ctcae_grade or 1} event detected. Routine monitoring recommended."

    return {
        "matched_adverse_events": matched_events,
        "ctcae_grade": ctcae_grade,
        "steroid_taper_detected": steroid_taper_detected,
        "borderline_safety_flag": borderline_safety_flag,
        "confidence": confidence,
        "safety_status": safety_status,
        "clinical_rationale": rationale,
    }
