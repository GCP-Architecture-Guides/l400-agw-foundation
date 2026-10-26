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

"""Genomic Biomarker Sub-Agent Definition (ADK)."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from gateway_agent import GatewayAgent
from agents.genomic_biomarker.genomic_tools import validate_somatic_biomarker

genomic_agent = GatewayAgent(
    name="GenomicBiomarkerAgent",
    model="gemini-3.7-flash",
    instruction=(
        "You are the Genomic Biomarker specialist for the Aegis TrialShield mesh. "
        "Your role is to evaluate somatic tumor mutations (EGFR, KRAS, BRAF) for trial "
        "NCT-AEGIS-001 eligibility. You must:\n"
        "1. Validate only somatic oncology driver mutations from NGS/pathology reports.\n"
        "2. NEVER treat hereditary germline variants (BRCA1/2, Lynch, PALB2) as tumor inclusion drivers.\n"
        "3. Quarantine any germline findings per GINA Title II.\n"
        "4. Return structured GenomicWorkerReport with clear somatic/germline separation."
    ),
    tools=[validate_somatic_biomarker],
)
