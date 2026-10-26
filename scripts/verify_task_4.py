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

"""Autograded Checkpoint for Task 4 (20 Points).

Validates:
1. ADK Agent definitions for all 5 decoupled sub-agents.
2. ADK agent naming conventions, model configuration (gemini-3.7-flash), and attached tools.
3. Strongly typed Pydantic contracts (ClinicalIntakeEnvelope, GenomicWorkerReport,
   PharmacovigilanceReport, ClinicalCohortReport, SynthesizerVerdict).
4. Cross-agent serialization and data boundary isolation.
"""

import sys


def run_checks() -> int:
    score = 0
    total = 20
    print("=" * 70)
    print("🧪 Verifying Task 4: ADK Sub-Agent Decoupling & Typed Contracts (20 pts)")
    print("=" * 70)

    try:
        from agents.clinical_cohort.cohort_agent import cohort_agent
        from agents.genomic_biomarker.biomarker_agent import genomic_agent
        from agents.pharmacovigilance.pv_agent import pv_agent
        from agents.trial_eligibility_synthesizer.synthesizer_agent import synthesizer_agent
        from agents.trial_matching_supervisor.agent import root_agent
    except Exception as exc:
        print(f"  ❌ [0/20 pts] Failed to import sub-agents: {exc}")
        print("     TODO (Task 4): Instantiate all 5 ADK sub-agents in agents/*/ using model 'gemini-3.7-flash'")
        print("-" * 70)
        print(f"Task 4 Total Score: 0/{total} points")
        print("=" * 70)
        return 1

    agents = [root_agent, genomic_agent, pv_agent, cohort_agent, synthesizer_agent]
    if any(a is None for a in agents):
        print("  ❌ [0/5 pts] One or more sub-agents are None (unimplemented).")
        print("  ❌ [0/5 pts] Missing tool bindings on stubbed sub-agents.")
        print("  ❌ [0/5 pts] Sub-agent contracts cannot be bound to stubbed instances.")
        print("  ❌ [0/5 pts] Synthesizer sub-agent not instantiated.")
        print("     TODO (Task 4): Complete agent definitions in agents/*/agent.py")
        print("-" * 70)
        print(f"Task 4 Total Score: 0/{total} points")
        print("=" * 70)
        return 1

    # Check 1: All 5 Sub-Agents Instantiated with Model gemini-3.7-flash (5 pts)
    try:
        agent_names = [getattr(a, "name", None) for a in agents]
        all_flash = all(getattr(a, "model", None) == "gemini-3.7-flash" for a in agents)
        expected_names = [
            "TrialMatchingSupervisor",
            "GenomicBiomarkerAgent",
            "PharmacovigilanceAgent",
            "ClinicalCohortAgent",
            "TrialEligibilitySynthesizer",
        ]
        if agent_names == expected_names and all_flash:
            print("  ✅ [5/5 pts] All 5 ADK sub-agents instantiated with model 'gemini-3.7-flash' and proper names.")
            score += 5
        else:
            print(f"  ❌ [0/5 pts] Agent configuration mismatch. Found: {agent_names}")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error checking agent names and models: {exc}")

    # Check 2: Each Agent Has Domain Tools Bound (5 pts)
    try:
        tools_ok = (
            len(getattr(root_agent, "tools", [])) >= 1
            and len(getattr(genomic_agent, "tools", [])) >= 1
            and len(getattr(pv_agent, "tools", [])) >= 1
            and len(getattr(cohort_agent, "tools", [])) >= 1
            and len(getattr(synthesizer_agent, "tools", [])) >= 1
        )
        if tools_ok:
            print("  ✅ [5/5 pts] Each decoupled sub-agent has specialized domain tools bound to its instance.")
            score += 5
        else:
            print("  ❌ [0/5 pts] Missing tool bindings on one or more sub-agents.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error checking agent tools: {exc}")

    # Check 3: Pydantic Domain Contracts Serialization (5 pts)
    try:
        from app.contracts import (
            ClinicalCohortReport,
            ClinicalIntakeEnvelope,
            GenomicStatus,
            GenomicWorkerReport,
            PharmacovigilanceReport,
        )

        envelope = ClinicalIntakeEnvelope(
            patient_id="PT-701",
            trial_id="NCT-AEGIS-001",
            sanitized_clinical_notes="De-identified notes",
            pii_redacted=True,
            gina_quarantined=True,
            quarantined_germline_markers=["BRCA1"],
        )
        genomic_rep = GenomicWorkerReport(
            variant_status=GenomicStatus.VALID_SOMATIC,
            gene="EGFR",
            variant_normalized="p.Leu858Arg",
            hgvs_cdna="NM_005228.5:c.2573T>G",
            hgvs_protein="p.Leu858Arg",
            confidence=0.98,
            germline_quarantined=True,
            clinical_interpretation="Actionable",
        )
        pv_rep = PharmacovigilanceReport(
            drug_name="Keytruda",
            days_since_last_dose=35,
            required_washout_days=28,
            washout_status="WASHOUT_SATISFIED",
            washout_period_satisfied=True,
            confidence=0.95,
            clinical_summary="Washout cleared",
        )
        cohort_rep = ClinicalCohortReport(
            ecog_score=1,
            ambulatory_status="AMBULATORY",
            renal_status="ACCEPTABLE",
            cohort_status="COHORT_ELIGIBLE",
            confidence=0.95,
            clinical_summary="Cohort eligible",
        )
        if (
            envelope.patient_id == "PT-701"
            and genomic_rep.variant_status == GenomicStatus.VALID_SOMATIC
            and pv_rep.washout_period_satisfied is True
            and cohort_rep.ecog_score == 1
        ):
            print("  ✅ [5/5 pts] Domain worker Pydantic contracts validated and serializable.")
            score += 5
        else:
            print("  ❌ [0/5 pts] Pydantic contracts validation failed.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error checking domain contracts: {exc}")

    # Check 4: SynthesizerVerdict Contract & GateChecks (5 pts)
    try:
        from app.contracts import EligibilityStatus, GateChecks, SynthesizerVerdict

        verdict = SynthesizerVerdict(
            eligibility_status=EligibilityStatus.ELIGIBLE,
            human_intervention_required=False,
            gate_checks=GateChecks(genomic_gate=True, washout_gate=True, ecog_gate=True, cohort_gate=True),
            exclusion_reasons=[],
            hitl_reasons=[],
            confidence=0.96,
            clinical_summary="All gates passed",
        )
        v_dict = verdict.model_dump()
        if (
            v_dict["eligibility_status"] == "ELIGIBLE"
            and v_dict["human_intervention_required"] is False
            and v_dict["gate_checks"]["genomic_gate"] is True
        ):
            print("  ✅ [5/5 pts] SynthesizerVerdict model matches strict specification.")
            score += 5
        else:
            print("  ❌ [0/5 pts] SynthesizerVerdict model validation failed.")
    except Exception as exc:
        print(f"  ❌ [0/5 pts] Error checking SynthesizerVerdict model: {exc}")

    print("-" * 70)
    print(f"Task 4 Total Score: {score}/{total} points")
    print("=" * 70)
    return 0 if score == total else 1


if __name__ == "__main__":
    sys.exit(run_checks())
