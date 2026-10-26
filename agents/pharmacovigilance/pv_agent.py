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

"""Pharmacovigilance Sub-Agent Definition (ADK)."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from gateway_agent import GatewayAgent
from agents.pharmacovigilance.pv_tools import evaluate_patient_pharmacovigilance

pv_agent = GatewayAgent(
    name="PharmacovigilanceAgent",
    model="gemini-3.7-flash",
    instruction=(
        "You are the Pharmacovigilance specialist for the Aegis TrialShield mesh. "
        "Your role is to evaluate drug washout clearance and adverse event safety:\n"
        "1. Use deterministic FastMCP calculations for drug washout periods (not AI guessing).\n"
        "2. Map adverse events to MedDRA v26 ontology with CTCAE v5.0 grading.\n"
        "3. Flag borderline safety contraindications (Grade 2+ irAEs, steroid tapers) "
        "for mandatory HITL oncologist review.\n"
        "4. Return structured PharmacovigilanceReport with exact deficit days."
    ),
    tools=[evaluate_patient_pharmacovigilance],
)
