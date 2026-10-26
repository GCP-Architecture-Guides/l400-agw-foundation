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

"""TrialShield POC Agent — Entrypoint for ADK Runner & Reasoning Engine.

Exposes the legacy monolithic root agent for deployment to Vertex AI Agent Runtime
and registration with Gemini Enterprise UI.
"""

from __future__ import annotations

import logging

from google.adk.apps import App

from legacy_mega_agent.poc_mega_agent import poc_agent

logger = logging.getLogger(__name__)

root_agent = poc_agent

app = App(
    root_agent=root_agent,
    name="TrialShield_POC_Agent",
)
