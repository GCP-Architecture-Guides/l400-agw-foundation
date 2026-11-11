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

"""Trial Matching Supervisor Agent Definition (ADK).

TASK 4 CHALLENGE:
Decouple the monolithic mega agent into 5 specialized ADK sub-agents.
This agent acts as the root coordinator that handles intake, sanitization,
and fans out work to specialized domain sub-agents.
"""

from __future__ import annotations

# TODO (Task 4): Import Agent from google.adk.agents and instantiate root_agent
# using model="gemini-3.7-flash", proper supervisor instructions, and binding
# `intercept_and_deidentify_intake` from .routing_tools.
root_agent = None
