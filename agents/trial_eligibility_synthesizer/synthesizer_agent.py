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

"""Trial Eligibility Synthesizer Sub-Agent Definition (ADK).

TASK 4 CHALLENGE:
Decouple synthesis and HITL escalation into a dedicated sub-agent.
Prevents stochastic LLM reasoning from bypassing required clinical safety gates.
"""

from __future__ import annotations

# TODO (Task 4): Import Agent from google.adk.agents and instantiate synthesizer_agent
# using model="gemini-3.7-flash", proper synthesizer instructions, and binding
# `evaluate_trial_eligibility` from .synthesis_tools.
synthesizer_agent = None
