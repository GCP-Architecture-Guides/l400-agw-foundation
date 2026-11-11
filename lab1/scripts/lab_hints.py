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

"""2-Tier Progressive Hint CLI for Aegis TrialShield Lab.

Provides two tiers of guidance for Tasks 1-5:
- LEVEL=1 (Architectural Nudge): Explains the security/clinical trap and points
  to the reference lego_blocks/ file.
- LEVEL=2 (AGY Prompting Strategy): Provides a structured prompt checklist for
  directing Antigravity (AGY) without revealing raw copy-paste solution code.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

# ANSI styling
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RED = "\033[91m"

HINTS_DB: dict[int, dict[str, Any]] = {
    1: {
        "title": "Task 1: HIPAA Safe Harbor & GINA Title II Pre-Model Interceptor",
        "lego_file": "lego_blocks/block_1_hipaa_gina_rules.py",
        "level_1": {
            "tier_name": "Level 1: Architectural Nudge",
            "content": (
                "🎯 CLINICAL & SECURITY TRAPS TO WATCH OUT FOR:\n\n"
                "1. Street Address vs. Washout Duration Collision:\n"
                "   Naive street address regexes matching '\\d+\\s+[A-Za-z]+' will aggressively\n"
                "   redact clinical durations like '30 days' or '14 days' as street names.\n"
                "   Use negative lookaheads or token exclusions (e.g., '(?!\\b(days|weeks|months)\\b)')\n"
                "   so clinical timelines required for pharmacovigilance are preserved.\n\n"
                "2. GINA Title II Germline Quarantine vs. Somatic Drivers:\n"
                "   Under GINA Title II, hereditary germline mutations (e.g., BRCA1, BRCA2, Lynch, PALB2)\n"
                "   MUST be quarantined into an isolated compliance audit trail before downstream\n"
                "   agent routing. However, somatic oncology driver variants (e.g., EGFR L858R, KRAS G12C,\n"
                "   BRAF V600E) MUST remain intact in the sanitized payload for trial matching!\n\n"
                "📂 REFERENCE IMPLEMENTATION TO INSPECT:\n"
                "   lego_blocks/block_1_hipaa_gina_rules.py"
            ),
        },
        "level_2": {
            "tier_name": "Level 2: AGY Prompting Strategy",
            "content": (
                "🤖 ANTIGRAVITY (AGY) PROMPTING CHECKLIST FOR TASK 1:\n\n"
                "When prompting AGY to build `intercept_and_deidentify_intake`, specify these constraints:\n\n"
                "  [ ] Pre-Model Deterministic Interceptor: Instruct AGY that de-identification must\n"
                "      execute entirely deterministic regex/rule passes before any LLM inference call.\n"
                "  [ ] HIPAA Safe Harbor Direct Identifiers: Mandate regex redaction for SSNs,\n"
                "      MRNs, names, phone numbers, and dates of birth (DOBs), replacing with typed tokens\n"
                "      like '[REDACTED_SSN]', '[REDACTED_MRN]', etc.\n"
                "  [ ] Duration Collision Safeguard: Explicitly instruct AGY: 'Do NOT redact clinical\n"
                "      duration phrases such as \"30 days\", \"14 days\", or \"6 weeks\" when scrubbing addresses.'\n"
                "  [ ] Genetic Segregation Contract: Require the returned envelope to have two distinct fields:\n"
                "      - `sanitized_clinical_notes`: Clean clinical narrative for downstream agent mesh.\n"
                "      - `somatic_notes_for_genomics`: Filtered notes preserving somatic oncology drivers.\n"
                "      - `quarantined_germline_markers`: List of segregated hereditary markers (BRCA1/2, PALB2).\n"
                "  [ ] Check against imports: Ensure the tool imports seamlessly into\n"
                "      `agents/trial_matching_supervisor/routing_tools.py`."
            ),
        },
    },
    2: {
        "title": "Task 2: FastMCP Washout Engine & FHIR Lab Normalizer",
        "lego_file": "lego_blocks/block_2_fastmcp_washout.py",
        "secondary_lego_file": "lego_blocks/block_3_fhir_lab_normalizer.py",
        "level_1": {
            "tier_name": "Level 1: Architectural Nudge",
            "content": (
                "🎯 CLINICAL & SECURITY TRAPS TO WATCH OUT FOR:\n\n"
                "1. ECOG 0 Falsy-Zero Trap:\n"
                "   In Python, `if not ecog_score:` evaluates to True when `ecog_score == 0`!\n"
                "   An ECOG score of 0 denotes a patient who is 'FULLY_ACTIVE' and asymptomatic.\n"
                "   Treating 0 as falsy leads to treating the healthiest trial candidates as missing data.\n"
                "   Always check `if ecog_score is None:` explicitly.\n\n"
                "2. Legacy Lab Unit Trap ('1.0 mg%'):\n"
                "   Historic and community oncology EHRs often log creatinine in 'mg%' instead of 'mg/dL'.\n"
                "   If the parser encounters legacy or unparseable units, it must NOT crash or guess blindly;\n"
                "   it must flag lower confidence (< 0.85) to force human-in-the-loop (HITL) review.\n\n"
                "3. Washout Boundary Logic (Tagrisso 21d >= 14d Washout):\n"
                "   Pharmacovigilance requires calculating elapsed days since last medication intake.\n"
                "   Verify `days_since_last_dose >= required_washout_days` (e.g. Tagrisso 21d >= 14d -> satisfied;\n"
                "   Keytruda 15d < 28d -> deficit 13 days).\n\n"
                "📂 REFERENCE IMPLEMENTATIONS TO INSPECT:\n"
                "   lego_blocks/block_2_fastmcp_washout.py (MedDRA Drug Washout Engine)\n"
                "   lego_blocks/block_3_fhir_lab_normalizer.py (FHIR R4 Lab & ECOG Normalizer)"
            ),
        },
        "level_2": {
            "tier_name": "Level 2: AGY Prompting Strategy",
            "content": (
                "🤖 ANTIGRAVITY (AGY) PROMPTING CHECKLIST FOR TASK 2:\n\n"
                "When prompting AGY to build the FastMCP server tools, specify these constraints:\n\n"
                "  [ ] FastMCP Tool Architecture: Instruct AGY to implement `@mcp.tool` decorators in\n"
                "      `mcp_servers/meddra_ontology/server.py` and `mcp_servers/fhir_lab_normalizer/server.py`.\n"
                "  [ ] Explicit None Checking for ECOG: Instruct AGY: 'ECOG performance status 0 is valid\n"
                "      and indicates FULLY_ACTIVE; do NOT use `if not score` because 0 is falsy in Python.'\n"
                "  [ ] FHIR R4 Unit Conversion: Creatinine conversion factor: 1 mg/dL = 88.42 umol/L.\n"
                "      Threshold: serum creatinine <= 1.5 mg/dL (132.6 umol/L) is ACCEPTABLE; > 1.5 is ELEVATED.\n"
                "  [ ] Legacy Unit Handling: If a unit like 'mg%' is encountered, mark unparseable flag\n"
                "      and set confidence to 0.70 to trigger physician escalation in Task 3.\n"
                "  [ ] Return Typed Dictionaries: Ensure functions return dicts with keys matching\n"
                "      `lego_blocks/block_2_fastmcp_washout.py` and `lego_blocks/block_3_fhir_lab_normalizer.py`."
            ),
        },
    },
    3: {
        "title": "Task 3: Deterministic Synthesis & Mandatory HITL Gate",
        "lego_file": "lego_blocks/block_5_hitl_synthesizer.py",
        "level_1": {
            "tier_name": "Level 1: Architectural Nudge",
            "content": (
                "🎯 CLINICAL & SECURITY TRAPS TO WATCH OUT FOR:\n\n"
                "1. Mandatory Stage-1 HITL Gate Precedence:\n"
                "   In high-risk medical AI, HITL safety gates take absolute precedence over boolean criteria.\n"
                "   Before checking whether genomic, washout, and cohort criteria are met, the synthesizer\n"
                "   MUST evaluate Stage-1 safety flags:\n"
                "   - Borderline safety flags (e.g. pneumonitis on prednisone taper in PT-707)\n"
                "   - Low worker confidence (< 0.85 threshold)\n"
                "   - Unparseable lab units ('mg%')\n"
                "   If any safety condition trips, immediately return `PENDING_REVIEW` with\n"
                "   `human_intervention_required=True`, irrespective of boolean gate passes!\n\n"
                "2. GINA Germline vs Somatic Confusion (PT-704 Wild-Type):\n"
                "   If a patient has wild-type somatic oncology drivers, but has a quarantined germline BRCA2\n"
                "   variant, the patient is INELIGIBLE (driver not present) and does NOT require HITL review.\n"
                "   Do not confuse germline markers with somatic inclusion criteria.\n\n"
                "📂 REFERENCE IMPLEMENTATION TO INSPECT:\n"
                "   lego_blocks/block_5_hitl_synthesizer.py"
            ),
        },
        "level_2": {
            "tier_name": "Level 2: AGY Prompting Strategy",
            "content": (
                "🤖 ANTIGRAVITY (AGY) PROMPTING CHECKLIST FOR TASK 3:\n\n"
                "When prompting AGY to build `evaluate_trial_eligibility`, specify these constraints:\n\n"
                "  [ ] 2-Stage Pipeline Pattern: Prompt AGY: 'Structure `evaluate_trial_eligibility` into two\n"
                "      clear sequential stages: Stage 1 (HITL Safety Gate Evaluation) and Stage 2\n"
                "      (Deterministic Criteria Synthesis).'\n"
                "  [ ] Stage 1 Precedence: If `borderline_safety_flag` is True, or if any worker confidence is\n"
                "      below 0.85, or if unparseable units exist, set `eligibility_status = \"PENDING_REVIEW\"`,\n"
                "      `human_intervention_required = True`, and return immediately.\n"
                "  [ ] Stage 2 Boolean Verdict: If Stage 1 passes, verify all criteria:\n"
                "      - genomic_gate: variant_status in ('VALID_SOMATIC', 'ACTIONABLE')\n"
                "      - washout_gate: washout_period_satisfied is True\n"
                "      - ecog_gate: ecog_score in (0, 1)\n"
                "      - cohort_gate: cohort_status == 'COHORT_ELIGIBLE'\n"
                "      Set ELIGIBLE if all True; INELIGIBLE otherwise; `human_intervention_required = False`.\n"
                "  [ ] Bind to Synthesizer: Ensure function is exposed in\n"
                "      `agents/trial_eligibility_synthesizer/synthesis_tools.py`."
            ),
        },
    },
    4: {
        "title": "Task 4: ADK Sub-Agent Decoupling & Typed Contracts",
        "lego_file": "lego_blocks/block_4_meddra_adverse_events.py",
        "secondary_lego_file": "app/contracts.py",
        "level_1": {
            "tier_name": "Level 1: Architectural Nudge",
            "content": (
                "🎯 CLINICAL & SECURITY TRAPS TO WATCH OUT FOR:\n\n"
                "1. Decoupling the 5 ADK Agents on gemini-3.7-flash:\n"
                "   The monolithic mega-agent compressed all domains into a single prompt. Task 4 requires\n"
                "   decoupling into 5 distinct Google ADK `Agent` instances, all configured with model\n"
                "   `gemini-3.7-flash`:\n"
                "   - `TrialMatchingSupervisor` (Supervisor agent)\n"
                "   - `GenomicBiomarkerAgent` (Specialist worker)\n"
                "   - `PharmacovigilanceAgent` (Specialist worker)\n"
                "   - `ClinicalCohortAgent` (Specialist worker)\n"
                "   - `TrialEligibilitySynthesizer` (Synthesis worker)\n\n"
                "2. Domain Tool Isolation:\n"
                "   Do NOT give every tool to every agent! Bind only domain-specific tools to each agent instance\n"
                "   (e.g. PV tools to PV agent, FHIR tools to Cohort agent, synthesis tools to Synthesizer).\n\n"
                "3. Pydantic Contract Serialization:\n"
                "   Validate strict typed contracts between agents using Pydantic models from `app/contracts.py`:\n"
                "   `DeidentifiedEnvelope`, `GenomicWorkerReport`, `PharmacovigilanceReport`,\n"
                "   `ClinicalCohortReport`, and `SynthesizerVerdict`.\n\n"
                "📂 REFERENCE CONTRACTS TO INSPECT:\n"
                "   app/contracts.py\n"
                "   lego_blocks/block_4_meddra_adverse_events.py"
            ),
        },
        "level_2": {
            "tier_name": "Level 2: AGY Prompting Strategy",
            "content": (
                "🤖 ANTIGRAVITY (AGY) PROMPTING CHECKLIST FOR TASK 4:\n\n"
                "When prompting AGY to build the 5 decoupled sub-agents, specify these constraints:\n\n"
                "  [ ] ADK Agent Class: Use `from google.adk.agents import Agent` (or ADK standard agent factory).\n"
                "  [ ] Model Selection: Enforce `model=\"gemini-3.7-flash\"` on all 5 agent definitions.\n"
                "  [ ] Dedicated Agent Files:\n"
                "      - `agents/trial_matching_supervisor/agent.py` -> `root_agent`\n"
                "      - `agents/genomic_biomarker/biomarker_agent.py` -> `genomic_agent`\n"
                "      - `agents/pharmacovigilance/pv_agent.py` -> `pv_agent`\n"
                "      - `agents/clinical_cohort/cohort_agent.py` -> `cohort_agent`\n"
                "      - `agents/trial_eligibility_synthesizer/synthesizer_agent.py` -> `synthesizer_agent`\n"
                "  [ ] Tool Binding: Ensure each agent's `tools` parameter lists only its domain tools.\n"
                "  [ ] Strict Pydantic Types: Verify that output payloads match models in `app/contracts.py`\n"
                "      with proper enums (`GenomicStatus`, `EligibilityStatus`)."
            ),
        },
    },
    5: {
        "title": "Task 5: Least Privilege IAM & OIDC Token Enforcement",
        "lego_file": "lego_blocks/block_6_oidc_auth_guard.py",
        "level_1": {
            "tier_name": "Level 1: Architectural Nudge",
            "content": (
                "🎯 CLINICAL & SECURITY TRAPS TO WATCH OUT FOR:\n\n"
                "1. Rejecting the God-Mode Service Account ('sa-legacy-god-mode'):\n"
                "   The legacy monolithic agent operated under `sa-legacy-god-mode` with unrestricted cloud\n"
                "   permissions. The multi-agent mesh security gateway must explicitly inspect incoming\n"
                "   identity assertions and immediately reject any token carrying `sa-legacy-god-mode` with a\n"
                "   `PermissionError`.\n\n"
                "2. Audience Validation (Target Service Claim):\n"
                "   OIDC tokens minted for one specialist agent (e.g. `https://agents.aegis.health/genomics`)\n"
                "   must NOT be accepted by another service (e.g. `pharmacovigilance`). Enforce strict audience\n"
                "   (`aud`) validation on every inter-agent RPC.\n\n"
                "3. Unidirectional Calling Graph:\n"
                "   The architecture enforces a strict DAG: Supervisor -> Domain Workers -> Synthesizer.\n"
                "   The Synthesizer is a leaf synthesis agent; it is strictly forbidden from calling upstream\n"
                "   domain workers or peer services.\n\n"
                "📂 REFERENCE IMPLEMENTATION TO INSPECT:\n"
                "   lego_blocks/block_6_oidc_auth_guard.py"
            ),
        },
        "level_2": {
            "tier_name": "Level 2: AGY Prompting Strategy",
            "content": (
                "🤖 ANTIGRAVITY (AGY) PROMPTING CHECKLIST FOR TASK 5:\n\n"
                "When prompting AGY to build `verify_mesh_caller_authorization`, specify these constraints:\n\n"
                "  [ ] God-Mode Rejection: Prompt AGY: 'Inspect caller email from JWT claims; if\n"
                "      \"sa-legacy-god-mode\" is present, raise `PermissionError(\"God-mode service account\n"
                "      is strictly prohibited in multi-agent mesh.\")`.'\n"
                "  [ ] Audience Claim Matching: Verify that token `aud` claim matches the registered service\n"
                "      audience URI (`https://agents.aegis.health/<target_service>`). Raise `PermissionError`\n"
                "      on mismatch.\n"
                "  [ ] Graph Permission Matrix: Check caller against `_CALLING_PERMISSIONS` matrix:\n"
                "      Supervisor can invoke workers; workers can invoke Synthesizer; Synthesizer cannot\n"
                "      invoke upstream workers.\n"
                "  [ ] Expose in Supervisor Routing: Ensure `verify_mesh_caller_authorization` is exported in\n"
                "      `agents/trial_matching_supervisor/routing_tools.py`."
            ),
        },
    },
}


def print_hint(task_id: int, level: int) -> int:
    """Print the requested hint."""
    if task_id not in HINTS_DB:
        print(f"{RED}{BOLD}Error: Invalid task {task_id}. Must be between 1 and 5.{RESET}")
        return 1

    if level not in (1, 2):
        print(f"{RED}{BOLD}Error: Invalid level {level}. Must be 1 or 2.{RESET}")
        return 1

    hint_entry = HINTS_DB[task_id]
    level_key = f"level_{level}"
    level_info = hint_entry[level_key]

    width = 76
    print()
    print(f"{CYAN}{BOLD}╔{'═' * (width - 2)}╗{RESET}")
    print(f"{CYAN}{BOLD}║  💡 AEGIS TRIALSHIELD LAB HINT SYSTEM{' ' * (width - 41)}║{RESET}")
    print(f"{CYAN}{BOLD}╠{'═' * (width - 2)}╣{RESET}")
    title = hint_entry["title"]
    print(f"{CYAN}{BOLD}║{RESET}  {YELLOW}{BOLD}{title}{RESET}")
    tier_name = level_info["tier_name"]
    print(f"{CYAN}{BOLD}║{RESET}  {GREEN}{BOLD}{tier_name}{RESET}")
    print(f"{CYAN}{BOLD}╠{'═' * (width - 2)}╣{RESET}")
    print()

    print(level_info["content"])
    print()
    print(f"{CYAN}{BOLD}╚{'═' * (width - 2)}╝{RESET}")
    print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aegis TrialShield 2-Tier Progressive Hint CLI",
    )
    parser.add_argument(
        "positional_args",
        nargs="*",
        help="Optional positional TASK and LEVEL (e.g. '1 1')",
    )
    parser.add_argument(
        "-t", "--task",
        type=int,
        default=None,
        help="Lab Task number (1-5)",
    )
    parser.add_argument(
        "-l", "--level",
        type=int,
        default=None,
        help="Hint Level: 1 = Architectural Nudge, 2 = AGY Prompting Strategy",
    )
    args = parser.parse_args()

    task = args.task
    level = args.level

    # Handle positional arguments if provided
    if args.positional_args:
        if len(args.positional_args) >= 1 and task is None:
            try:
                task = int(args.positional_args[0])
            except ValueError:
                print(f"{RED}{BOLD}Error: TASK must be an integer (1-5).{RESET}")
                sys.exit(1)
        if len(args.positional_args) >= 2 and level is None:
            try:
                level = int(args.positional_args[1])
            except ValueError:
                print(f"{RED}{BOLD}Error: LEVEL must be an integer (1-2).{RESET}")
                sys.exit(1)

    # Defaults
    if task is None:
        task = 1
    if level is None:
        level = 1

    sys.exit(print_hint(task, level))


if __name__ == "__main__":
    main()
