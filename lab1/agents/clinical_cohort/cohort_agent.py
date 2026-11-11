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

"""Clinical Cohort Sub-Agent Definition (ADK).

TASK 4 CHALLENGE:
Decouple clinical performance status and FHIR laboratory evaluation into a dedicated sub-agent.
Accurately preserves ECOG 0 as fully active and flags legacy lab units for HITL review.
"""

from __future__ import annotations

# TODO (Task 4): Import Agent from google.adk.agents and instantiate cohort_agent
# using model="gemini-3.7-flash", proper cohort instructions, and binding
# `evaluate_clinical_cohort` from .cohort_tools.
cohort_agent = None
