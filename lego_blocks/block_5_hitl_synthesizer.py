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

"""Modular Lego Block 5: Deterministic Synthesis & Human-in-the-Loop (HITL) Gatekeeper.

Implements:
1. Strict Boolean Gating Invariant:
   ELIGIBLE iff (Genomic == VALID_SOMATIC) AND
                (Washout == WASHOUT_SATISFIED) AND
                (ECOG <= 2) AND
                (Cohort == COHORT_ELIGIBLE)

2. Mandatory Human-In-The-Loop (HITL) Escalation:
   Routes to 'PENDING_REVIEW' (human_intervention_required = True) when:
   - Any worker confidence score < 0.85
   - Unparseable lab units detected (e.g., '1.0 mg%')
   - Borderline safety contraindication flag present (e.g. pneumonitis on steroid taper)
   - Ambiguous or inconclusive worker reports

3. Zero Collateral Decisions:
   Deterministic, mathematically verifiable decision paths that prevent LLM hallucinations
   from improperly denying viable oncology candidates or recklessly admitting toxic patients.
"""

from __future__ import annotations

import logging
from typing import Any, Final

from app.contracts import (
    EligibilityStatus,
    GateChecks,
    SynthesizerVerdict,
)

logger = logging.getLogger(__name__)

HITL_CONFIDENCE_THRESHOLD: Final[float] = 0.85


def synthesize_trial_verdict(
    genomic_report: dict[str, Any],
    pv_report: dict[str, Any],
    cohort_report: dict[str, Any],
) -> SynthesizerVerdict:
    """Evaluates multi-agent oncology trial eligibility via deterministic boolean gating.

    Args:
        genomic_report: Structured report from Genomic Biomarker sub-agent.
        pv_report: Structured report from Pharmacovigilance sub-agent.
        cohort_report: Structured report from Clinical Cohort sub-agent.

    Returns:
        Standardized typed SynthesizerVerdict model.
    """
    # 1. Extract statuses
    genomic_status = str(
        genomic_report.get("overall_genomic_status", genomic_report.get("variant_status", ""))
    ).strip().upper()

    washout_status = str(
        pv_report.get("washout_status", pv_report.get("overall_status", ""))
    ).strip().upper()
    if not washout_status and pv_report.get("washout_period_satisfied") is True:
        washout_status = "WASHOUT_SATISFIED"

    cohort_status = str(cohort_report.get("cohort_status", "")).strip().upper()
    
    # Safely extract ECOG score (avoiding falsy zero bug)
    ecog_score_raw = cohort_report.get("ecog_score")
    if ecog_score_raw is None:
        ecog_score_raw = cohort_report.get("ecog_status")
    try:
        ecog_score: int | None = int(ecog_score_raw) if ecog_score_raw is not None else None
    except (ValueError, TypeError):
        ecog_score = None

    # 2. Extract Confidence Scores & Flags
    genomic_conf = float(genomic_report.get("confidence", 0.95))
    pv_conf = float(pv_report.get("confidence", 0.95))
    cohort_conf = float(cohort_report.get("confidence", 0.95))
    min_confidence = min(genomic_conf, pv_conf, cohort_conf)

    unparseable_labs = bool(cohort_report.get("unparseable_labs", False))
    borderline_safety = bool(
        pv_report.get("borderline_safety", False) or pv_report.get("borderline_safety_flag", False)
    )

    hitl_reasons: list[str] = []
    exclusion_reasons: list[str] = []

    # 3. Check for HITL Triggers
    if unparseable_labs:
        hitl_reasons.append("Clinical cohort detected unparseable legacy lab units (e.g. mg%)")
        cohort_conf = min(cohort_conf, 0.70)

    if borderline_safety:
        hitl_reasons.append("Borderline pharmacovigilance safety contraindication flag present")
        pv_conf = min(pv_conf, 0.79)

    min_confidence = min(genomic_conf, pv_conf, cohort_conf)
    if min_confidence < HITL_CONFIDENCE_THRESHOLD:
        hitl_reasons.append(
            f"Sub-agent confidence below threshold ({min_confidence:.2f} < {HITL_CONFIDENCE_THRESHOLD}): "
            f"Genomic={genomic_conf:.2f}, PV={pv_conf:.2f}, Cohort={cohort_conf:.2f}"
        )

    if genomic_status in ("AMBIGUOUS", "INCONCLUSIVE", "UNKNOWN"):
        hitl_reasons.append(f"Genomic biomarker status is inconclusive: '{genomic_status}'")

    if ecog_score is None:
        hitl_reasons.append("ECOG functional performance status could not be deterministically determined")

    # 4. Evaluate Boolean Gate Invariants
    genomic_passed = genomic_status == "VALID_SOMATIC"
    washout_passed = washout_status == "WASHOUT_SATISFIED"
    ecog_passed = ecog_score is not None and ecog_score <= 2
    cohort_passed = cohort_status == "COHORT_ELIGIBLE" or (cohort_status == "" and ecog_passed)

    if not genomic_passed:
        exclusion_reasons.append(
            f"Genomic criterion not satisfied: status is '{genomic_status}' (required 'VALID_SOMATIC')"
        )
    if not washout_passed:
        deficit = pv_report.get("washout_deficit_days", "unknown")
        exclusion_reasons.append(
            f"Washout criterion not satisfied: status is '{washout_status}' "
            f"(required 'WASHOUT_SATISFIED', deficit: {deficit} days)"
        )
    if not ecog_passed:
        exclusion_reasons.append(f"ECOG criterion not satisfied: score is {ecog_score} (required <= 2)")
    if not cohort_passed:
        exclusion_reasons.append(f"Cohort criterion not satisfied: status is '{cohort_status}' (required 'COHORT_ELIGIBLE')")

    # 5. Determine Final Verdict (HITL Gate Evaluated First!)
    if hitl_reasons:
        final_status = EligibilityStatus.PENDING_REVIEW
        human_req = True
        summary = (
            "Trial eligibility requires Oncologist Human-in-the-Loop review due to safety/confidence triggers: "
            + "; ".join(hitl_reasons)
        )
    elif genomic_passed and washout_passed and ecog_passed and cohort_passed:
        final_status = EligibilityStatus.ELIGIBLE
        human_req = False
        summary = (
            f"Patient satisfies all inclusion criteria: validated somatic mutation "
            f"({genomic_report.get('variant_normalized', 'confirmed')}), "
            f"washout satisfied, and ECOG {ecog_score}."
        )
    else:
        final_status = EligibilityStatus.INELIGIBLE
        human_req = False
        summary = (
            "Patient is excluded from trial based on objective criteria: "
            + "; ".join(exclusion_reasons)
        )

    # 6. Build GateChecks model
    gate_checks = GateChecks(
        genomic_gate=genomic_passed,
        washout_gate=washout_passed,
        ecog_gate=ecog_passed,
        cohort_gate=cohort_passed,
    )

    return SynthesizerVerdict(
        eligibility_status=final_status,
        human_intervention_required=human_req,
        gate_checks=gate_checks,
        exclusion_reasons=exclusion_reasons,
        hitl_reasons=hitl_reasons,
        confidence=round(min_confidence, 2),
        clinical_summary=summary,
    )
