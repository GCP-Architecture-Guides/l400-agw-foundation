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

"""Autograded Checkpoint for Task 2 (20 Points).

Validates:
1. FastMCP deterministic pharmacology washout calculations (Tagrisso, Keytruda).
2. FHIR R4 SI lab unit conversions (serum creatinine mg/dL -> umol/L).
3. Legacy unit handling ('mg%') and unparseable lab flagging.
4. ASCO/ECOG Performance Status extraction with falsy-zero fix (ECOG 0).
"""

import sys


def run_checks() -> int:
    score = 0
    total = 20
    print("=" * 70)
    print("🧪 Verifying Task 2: FastMCP Washout Engine & FHIR Lab Normalizer (20 pts)")
    print("=" * 70)

    try:
        from mcp_servers.meddra_ontology.server import mcp_calculate_drug_clearance
        from mcp_servers.fhir_lab_normalizer.server import (
            mcp_extract_ecog_score,
            mcp_normalize_renal_labs,
        )
    except Exception as exc:
        print(f"  ❌ [0/20 pts] Failed to import FastMCP server tools: {exc}")
        print("     TODO (Task 2): Implement tools in mcp_servers/ using lego_blocks/block_2_fastmcp_washout.py and lego_blocks/block_3_fhir_lab_normalizer.py")
        print("-" * 70)
        print(f"Task 2 Total Score: 0/{total} points")
        print("=" * 70)
        return 1

    # Check 1: FastMCP Washout Satisfied (Tagrisso 21d vs 14d) (4 pts)
    try:
        washout_tagrisso = mcp_calculate_drug_clearance(
            drug_name="Tagrisso (osimertinib)",
            days_since_last_dose=21,
            required_washout_days=14,
        )
        if (
            washout_tagrisso.get("washout_period_satisfied") is True
            and washout_tagrisso.get("overall_status") == "WASHOUT_SATISFIED"
            and washout_tagrisso.get("washout_deficit_days") == 0
        ):
            print("  ✅ [4/4 pts] Tagrisso 21d clearance correctly verified (WASHOUT_SATISFIED).")
            score += 4
        else:
            print("  ❌ [0/4 pts] Tagrisso clearance calculation failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing Tagrisso clearance tool: {exc}")

    # Check 2: FastMCP Washout Deficit (Keytruda 15d vs 28d) (4 pts)
    try:
        washout_keytruda = mcp_calculate_drug_clearance(
            drug_name="Keytruda (pembrolizumab)",
            days_since_last_dose=15,
            required_washout_days=28,
        )
        if (
            washout_keytruda.get("washout_period_satisfied") is False
            and washout_keytruda.get("overall_status") == "WASHOUT_DEFICIT"
            and washout_keytruda.get("washout_deficit_days") == 13
        ):
            print("  ✅ [4/4 pts] Keytruda 15d deficit correctly computed (13 days deficit).")
            score += 4
        else:
            print("  ❌ [0/4 pts] Keytruda deficit calculation failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing Keytruda clearance tool: {exc}")

    # Check 3: FHIR R4 Unit Conversion (4 pts)
    try:
        fhir_norm = mcp_normalize_renal_labs(raw_value=0.85, raw_unit="mg/dL")
        fhir_high = mcp_normalize_renal_labs(raw_value=2.4, raw_unit="mg/dL")
        if (
            abs(fhir_norm.get("normalized_value", 0.0) - 75.16) < 0.1
            and fhir_norm.get("normalized_unit") == "umol/L"
            and fhir_norm.get("renal_status") == "ACCEPTABLE"
            and fhir_high.get("renal_status") == "ELEVATED"
        ):
            print("  ✅ [4/4 pts] FHIR R4 lab conversions verified (0.85 mg/dL -> 75.16 umol/L, 2.4 mg/dL -> ELEVATED).")
            score += 4
        else:
            print("  ❌ [0/4 pts] FHIR lab normalization failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing FHIR normalization tool: {exc}")

    # Check 4: Unparseable Lab Detection ('mg%') (4 pts)
    try:
        fhir_legacy = mcp_normalize_renal_labs(raw_value=1.0, raw_unit="mg%")
        if (
            fhir_legacy.get("unparseable_labs") is True
            and fhir_legacy.get("confidence", 1.0) < 0.85
        ):
            print("  ✅ [4/4 pts] Legacy '1.0 mg%' unit correctly detected, lowering confidence for HITL escalation.")
            score += 4
        else:
            print("  ❌ [0/4 pts] Unparseable legacy unit detection failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing legacy unit check: {exc}")

    # Check 5: Falsy-Zero Safe ECOG 0 (4 pts)
    try:
        ecog_zero = mcp_extract_ecog_score("Patient is fully active and asymptomatic with an ECOG performance status of 0.")
        if (
            ecog_zero.get("ecog_score") == 0
            and ecog_zero.get("ambulatory_status") == "FULLY_ACTIVE"
            and ecog_zero.get("confidence", 0.0) >= 0.85
        ):
            print("  ✅ [4/4 pts] ECOG 0 correctly recognized as FULLY_ACTIVE (falsy-zero bug eliminated).")
            score += 4
        else:
            print("  ❌ [0/4 pts] ECOG 0 classification failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing ECOG tool: {exc}")

    print("-" * 70)
    print(f"Task 2 Total Score: {score}/{total} points")
    print("=" * 70)
    return 0 if score == total else 1


if __name__ == "__main__":
    sys.exit(run_checks())
