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

"""Autograded Checkpoint for Task 1 (15 Points).

Validates:
1. HIPAA Safe Harbor direct identifier scrubbing via supervisor intake interceptor.
2. Zero collateral damage on clinical durations ('30 days' is NOT scrubbed).
3. GINA Title II germline quarantine (BRCA1/2, Lynch, PALB2).
4. Preservation of somatic oncology driver mutations (EGFR, KRAS, BRAF).
"""

import sys


def run_checks() -> int:
    score = 0
    total = 15
    print("=" * 70)
    print("🧪 Verifying Task 1: HIPAA Safe Harbor & GINA Title II Interceptor (15 pts)")
    print("=" * 70)

    try:
        from agents.trial_matching_supervisor.routing_tools import intercept_and_deidentify_intake
    except Exception as exc:
        print(f"  ❌ [0/15 pts] Failed to import intercept_and_deidentify_intake: {exc}")
        print("     TODO (Task 1): Implement agents/trial_matching_supervisor/routing_tools.py using lego_blocks/block_1_hipaa_gina_rules.py")
        print("-" * 70)
        print(f"Task 1 Total Score: 0/{total} points")
        print("=" * 70)
        return 1

    # Check 1: PII Redaction (SSN, MRN, Name, DOB) (4 pts)
    try:
        raw_pt701 = (
            "Patient Name: Evelyn Carter, SSN: 412-88-9012, MRN: MRN-884920, DOB: 03/14/1968. "
            "Evaluated for NCT-AEGIS-001."
        )
        res_701 = intercept_and_deidentify_intake("PT-701", raw_pt701)
        envelope_701 = res_701.get("envelope", {})
        sanitized_701 = envelope_701.get("sanitized_clinical_notes", "")
        pii_found = envelope_701.get("pii_redacted", False)
        if (
            "412-88-9012" not in sanitized_701
            and "Evelyn Carter" not in sanitized_701
            and "MRN-884920" not in sanitized_701
            and "03/14/1968" not in sanitized_701
            and "[REDACTED_SSN]" in sanitized_701
            and "[REDACTED_NAME]" in sanitized_701
            and pii_found
        ):
            print("  ✅ [4/4 pts] HIPAA Direct Identifiers (SSN, Name, MRN, DOB) sanitized successfully.")
            score += 4
        else:
            print("  ❌ [0/4 pts] Failed to sanitize HIPAA Direct Identifiers in intake interceptor.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing intake interceptor on PT-701: {exc}")

    # Check 2: Zero Collateral Damage on Durations ('30 days') (4 pts)
    try:
        raw_duration = (
            "Patient Clara Oswald had last Pembrolizumab dose 30 days ago (required washout: 28 days). "
            "Living at 1200 Main Street, Apt 4B."
        )
        res_dur = intercept_and_deidentify_intake("PT-703", raw_duration)
        sanitized_dur = res_dur.get("envelope", {}).get("sanitized_clinical_notes", "")
        if "30 days" in sanitized_dur and "28 days" in sanitized_dur and "[REDACTED_STREET_ADDRESS]" in sanitized_dur:
            print("  ✅ [4/4 pts] Real street address scrubbed without damaging clinical durations ('30 days').")
            score += 4
        else:
            print("  ❌ [0/4 pts] Collateral damage detected or address not scrubbed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing duration check: {exc}")

    # Check 3: GINA Title II Germline Quarantine (4 pts)
    try:
        raw_gina = (
            "Tumor biopsy shows somatic EGFR L858R. Peripheral blood indicates incidental germline BRCA1 carrier "
            "and hereditary Lynch syndrome (MLH1/MSH2 carrier)."
        )
        res_gina = intercept_and_deidentify_intake("PT-701", raw_gina)
        envelope_gina = res_gina.get("envelope", {})
        somatic_only = res_gina.get("somatic_notes_for_genomics", "")
        markers = envelope_gina.get("quarantined_germline_markers", [])
        gina_flag = envelope_gina.get("gina_quarantined", False)
        if (
            gina_flag
            and "BRCA1" not in somatic_only
            and "Lynch syndrome" not in somatic_only
            and "MLH1" not in somatic_only
            and "EGFR L858R" in somatic_only
            and any("BRCA1" in m for m in markers)
        ):
            print("  ✅ [4/4 pts] GINA Title II germline risk markers quarantined while preserving somatic EGFR driver.")
            score += 4
        else:
            print("  ❌ [0/4 pts] GINA germline quarantine failed.")
    except Exception as exc:
        print(f"  ❌ [0/4 pts] Error executing GINA quarantine check: {exc}")

    # Check 4: Multiple Somatic Drivers Preserved (3 pts)
    try:
        raw_somatics = "Variants detected: somatic KRAS G12C and somatic BRAF V600E alongside germline PALB2."
        res_somatics = intercept_and_deidentify_intake("PT-702", raw_somatics)
        somatic_clean = res_somatics.get("somatic_notes_for_genomics", "")
        if "KRAS G12C" in somatic_clean and "BRAF V600E" in somatic_clean and "PALB2" not in somatic_clean:
            print("  ✅ [3/3 pts] Somatic oncology driver variants (KRAS G12C, BRAF V600E) safely preserved.")
            score += 3
        else:
            print("  ❌ [0/3 pts] Somatic oncology preservation failed.")
    except Exception as exc:
        print(f"  ❌ [0/3 pts] Error executing somatic driver preservation check: {exc}")

    print("-" * 70)
    print(f"Task 1 Total Score: {score}/{total} points")
    print("=" * 70)
    return 0 if score == total else 1


if __name__ == "__main__":
    sys.exit(run_checks())
