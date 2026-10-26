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

"""Autograded Checkpoint for Task 5 (20 Points).

Validates:
1. Rejection of over-permissioned God-mode service account ('sa-legacy-god-mode').
2. Downscoped IAM OIDC token minting for each specialized role.
3. Strict audience validation (https://agents.aegis.health/<agent>).
4. Unidirectional calling graph enforcement (Supervisor -> Workers -> Synthesizer).
"""

import sys
from lego_blocks.block_6_oidc_auth_guard import mint_mock_oidc_token


def run_checks() -> int:
    score = 0
    total = 20
    print("=" * 70)
    print("🧪 Verifying Task 5: Least Privilege IAM & OIDC Token Enforcement (20 pts)")
    print("=" * 70)

    try:
        from agents.trial_matching_supervisor.routing_tools import verify_mesh_caller_authorization
    except Exception as exc:
        print(f"  ❌ [0/20 pts] Failed to import verify_mesh_caller_authorization: {exc}")
        print("     TODO (Task 5): Implement verify_mesh_caller_authorization in agents/trial_matching_supervisor/routing_tools.py using lego_blocks/block_6_oidc_auth_guard.py")
        print("-" * 70)
        print(f"Task 5 Total Score: 0/{total} points")
        print("=" * 70)
        return 1

    # Check 1: Reject God-Mode Service Account (5 pts)
    try:
        god_mode_token = mint_mock_oidc_token("god-mode", "https://agents.aegis.health/pharmacovigilance")
        god_rejected = False
        try:
            verify_mesh_caller_authorization(god_mode_token, "pharmacovigilance")
        except PermissionError as exc:
            if "god-mode" in str(exc).lower() or "strictly prohibited" in str(exc).lower():
                god_rejected = True

        if god_rejected:
            print("  ✅ [5/5 pts] Over-permissioned God-Mode service account ('sa-legacy-god-mode') strictly rejected.")
            score += 5
        else:
            print("  ❌ [0/5 pts] God-mode rejection failed.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error executing God-mode rejection check: {exc}")

    # Check 2: Valid Supervisor -> Pharmacovigilance Call (5 pts)
    try:
        pv_token = mint_mock_oidc_token("supervisor", "https://agents.aegis.health/pharmacovigilance")
        payload = verify_mesh_caller_authorization(pv_token, "pharmacovigilance")
        if payload.get("email") == "sa-matching-supervisor@prod-proj-ge.iam.gserviceaccount.com":
            print("  ✅ [5/5 pts] Downscoped supervisor token authorized for Pharmacovigilance Agent.")
            score += 5
        else:
            print("  ❌ [0/5 pts] Supervisor token validation failed.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error executing supervisor token check: {exc}")

    # Check 3: Audience Mismatch Rejection (5 pts)
    try:
        genomic_token = mint_mock_oidc_token("genomics", "https://agents.aegis.health/genomics")
        audience_rejected = False
        try:
            verify_mesh_caller_authorization(genomic_token, "pharmacovigilance")
        except PermissionError as exc:
            if "audience" in str(exc).lower():
                audience_rejected = True

        if audience_rejected:
            print("  ✅ [5/5 pts] Audience mismatch rejected (genomic token cannot invoke pharmacovigilance).")
            score += 5
        else:
            print("  ❌ [0/5 pts] Audience mismatch validation failed.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error executing audience validation check: {exc}")

    # Check 4: Unidirectional Calling Graph (5 pts)
    try:
        synth_token = mint_mock_oidc_token("synthesizer", "https://agents.aegis.health/clinical-cohort")
        reverse_call_rejected = False
        try:
            verify_mesh_caller_authorization(synth_token, "clinical-cohort")
        except PermissionError as exc:
            if "not authorized" in str(exc).lower() or "unauthorized" in str(exc).lower():
                reverse_call_rejected = True

        if reverse_call_rejected:
            print("  ✅ [5/5 pts] Calling graph enforced: Synthesizer leaf cannot call upstream workers.")
            score += 5
        else:
            print("  ❌ [0/5 pts] Calling graph enforcement failed.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error executing calling graph check: {exc}")

    print("-" * 70)
    print(f"Task 5 Total Score: {score}/{total} points")
    print("=" * 70)
    return 0 if score == total else 1


if __name__ == "__main__":
    sys.exit(run_checks())
