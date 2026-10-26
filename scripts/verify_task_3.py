#!/usr/bin/env python3
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

"""Autograded Checkpoint for Task 3 (25 Points).

Validates:
1. Boolean Gating Invariant: (Genomic == VALID_SOMATIC) AND (Washout == WASHOUT_SATISFIED)
                             AND (ECOG <= 2) AND (Cohort == COHORT_ELIGIBLE).
2. Deterministic Denial on objective criteria failures (washout deficit).
3. Mandatory HITL on low assay confidence (< 0.85).
4. Mandatory HITL on unparseable lab units (1.0 mg%).
5. Mandatory HITL on borderline safety flags (Grade 2 pneumonitis on steroid taper).
6. GINA germline vs. somatic separation (PT-704 Wild-Type correctly marked INELIGIBLE).
"""

import sys


def run_checks() -> int:
    score = 0
    total = 25
    print("=" * 70)
    print("🧪 Verifying Task 3: Deterministic Synthesis & Mandatory HITL Gate (25 pts)")
    print("=" * 70)

    try:
        from agents.trial_eligibility_synthesizer.synthesis_tools import evaluate_trial_eligibility
    except Exception as exc:
        print(f"  ❌ [0/25 pts] Failed to import evaluate_trial_eligibility: {exc}")
        print("     TODO (Task 3): Implement agents/trial_eligibility_synthesizer/synthesis_tools.py using lego_blocks/block_5_hitl_synthesizer.py")
        print("-" * 70)
        print(f"Task 3 Total Score: 0/{total} points")
        print("=" * 70)
        return 1

    # Check 1: Perfect Candidate -> ELIGIBLE (4 pts)
    try:
        v_eligible = evaluate_trial_eligibility(
            genomic_report_json={"overall_genomic_status": "VALID_SOMATIC", "confidence": 0.98, "variant_normalized": "EGFR L858R"},
            pv_report_json={"washout_status": "WASHOUT_SATISFIED", "washout_period_satisfied": True, "confidence": 0.95},
            cohort_report_json={"cohort_status": "COHORT_ELIGIBLE", "ecog_score": 1, "confidence": 0.95, "unparseable_labs": False},
        )
        if (
            v_eligible.get("eligibility_status") == "ELIGIBLE"
            and v_eligible.get("human_intervention_required") is False
        ):
            print("  ✅ [4/4 pts] Perfect candidate synthesized as ELIGIBLE with human_intervention_required=False.")
            score += 4
        else:
            print("  ❌ [0/4 pts] Perfect candidate synthesis failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error during perfect candidate synthesis: {exc}")

    # Check 2: Objective Failure -> INELIGIBLE (4 pts)
    try:
        v_ineligible = evaluate_trial_eligibility(
            genomic_report_json={"overall_genomic_status": "VALID_SOMATIC", "confidence": 0.98},
            pv_report_json={"washout_status": "WASHOUT_DEFICIT", "washout_period_satisfied": False, "washout_deficit_days": 16, "confidence": 0.95},
            cohort_report_json={"cohort_status": "COHORT_ELIGIBLE", "ecog_score": 1, "confidence": 0.95},
        )
        if (
            v_ineligible.get("eligibility_status") == "INELIGIBLE"
            and v_ineligible.get("human_intervention_required") is False
        ):
            print("  ✅ [4/4 pts] Washout deficit correctly synthesized as INELIGIBLE without unnecessary HITL.")
            score += 4
        else:
            print("  ❌ [0/4 pts] Objective failure synthesis failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error during objective failure synthesis: {exc}")

    # Check 3: Low Genomic Confidence (< 0.85) -> PENDING_REVIEW (4 pts)
    try:
        v_low_conf = evaluate_trial_eligibility(
            genomic_report_json={"overall_genomic_status": "VALID_SOMATIC", "confidence": 0.72},
            pv_report_json={"washout_status": "WASHOUT_SATISFIED", "washout_period_satisfied": True, "confidence": 0.95},
            cohort_report_json={"cohort_status": "COHORT_ELIGIBLE", "ecog_score": 1, "confidence": 0.95},
        )
        if (
            v_low_conf.get("eligibility_status") == "PENDING_REVIEW"
            and v_low_conf.get("human_intervention_required") is True
        ):
            print("  ✅ [4/4 pts] Low genomic confidence (0.72 < 0.85) triggered mandatory PENDING_REVIEW (HITL).")
            score += 4
        else:
            print("  ❌ [0/4 pts] Low confidence HITL trigger failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error during low confidence synthesis: {exc}")

    # Check 4: Unparseable Lab Units ('mg%') -> PENDING_REVIEW (4 pts)
    try:
        v_unparseable = evaluate_trial_eligibility(
            genomic_report_json={"overall_genomic_status": "VALID_SOMATIC", "confidence": 0.98},
            pv_report_json={"washout_status": "WASHOUT_SATISFIED", "washout_period_satisfied": True, "confidence": 0.95},
            cohort_report_json={"cohort_status": "INCONCLUSIVE", "ecog_score": 1, "confidence": 0.70, "unparseable_labs": True},
        )
        if (
            v_unparseable.get("eligibility_status") == "PENDING_REVIEW"
            and v_unparseable.get("human_intervention_required") is True
        ):
            print("  ✅ [4/4 pts] Unparseable lab units ('mg%') triggered mandatory PENDING_REVIEW (HITL).")
            score += 4
        else:
            print("  ❌ [0/4 pts] Unparseable lab units HITL trigger failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error during unparseable lab synthesis: {exc}")

    # Check 5: Borderline Safety Flag -> PENDING_REVIEW (5 pts)
    try:
        v_pt707 = evaluate_trial_eligibility(
            genomic_report_json={"overall_genomic_status": "VALID_SOMATIC", "confidence": 0.97},
            pv_report_json={
                "washout_status": "WASHOUT_SATISFIED",
                "washout_period_satisfied": True,
                "confidence": 0.79,
                "borderline_safety_flag": True,
                "active_adverse_events": ["Grade 2 immune-mediated pneumonitis on prednisone taper"],
            },
            cohort_report_json={"cohort_status": "COHORT_ELIGIBLE", "ecog_score": 1, "confidence": 0.95},
        )
        if (
            v_pt707.get("eligibility_status") == "PENDING_REVIEW"
            and v_pt707.get("human_intervention_required") is True
        ):
            print("  ✅ [5/5 pts] Borderline pneumonitis safety flag triggered mandatory PENDING_REVIEW (remedies PT-707!).")
            score += 5
        else:
            print("  ❌ [0/5 pts] Borderline safety flag HITL trigger failed.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error during borderline safety flag synthesis: {exc}")

    # Check 6: GINA vs Somatic Confusion -> INELIGIBLE (4 pts)
    try:
        v_pt704 = evaluate_trial_eligibility(
            genomic_report_json={
                "overall_genomic_status": "WILD_TYPE",
                "variant_status": "WILD_TYPE",
                "confidence": 0.99,
                "germline_quarantined": True,
                "quarantined_germline_markers": ["BRCA2"],
            },
            pv_report_json={"washout_status": "WASHOUT_SATISFIED", "washout_period_satisfied": True, "confidence": 0.95},
            cohort_report_json={"cohort_status": "COHORT_ELIGIBLE", "ecog_score": 0, "confidence": 0.95},
        )
        if (
            v_pt704.get("eligibility_status") == "INELIGIBLE"
            and v_pt704.get("human_intervention_required") is False
        ):
            print("  ✅ [4/4 pts] PT-704 Wild-Type correctly synthesized as INELIGIBLE (germline BRCA2 not confused).")
            score += 4
        else:
            print("  ❌ [0/4 pts] PT-704 Wild-Type synthesis failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error during PT-704 synthesis: {exc}")

    print("-" * 70)
    print(f"Task 3 Total Score: {score}/{total} points")
    print("=" * 70)
    return 0 if score == total else 1


if __name__ == "__main__":
    sys.exit(run_checks())
