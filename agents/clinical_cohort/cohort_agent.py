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

"""Clinical Cohort Sub-Agent Definition (ADK)."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from gateway_agent import GatewayAgent
from agents.clinical_cohort.cohort_tools import evaluate_clinical_cohort

cohort_agent = GatewayAgent(
    name="ClinicalCohortAgent",
    model="gemini-3.7-flash",
    instruction=(
        "You are the Clinical Cohort specialist for the Aegis TrialShield mesh. "
        "Your role is to evaluate patient functional performance and laboratory fitness:\n"
        "1. Extract ECOG performance status (0-5) without the Python falsy-zero bug. "
        "ECOG 0 means FULLY ACTIVE — it is a valid, optimal score!\n"
        "2. Normalize laboratory measurements into FHIR R4 standard units (mg/dL -> umol/L).\n"
        "3. Flag legacy non-standard units (e.g., mg%) as unparseable for HITL escalation.\n"
        "4. Return structured ClinicalCohortReport with renal status assessment."
    ),
    tools=[evaluate_clinical_cohort],
)
