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

"""FastMCP Server for MedDRA Adverse Event & Pharmacovigilance Washout Calculations."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP
from lego_blocks.block_2_fastmcp_washout import calculate_drug_clearance_fastmcp
from lego_blocks.block_4_meddra_adverse_events import evaluate_adverse_event_safety

logger = logging.getLogger(__name__)

mcp_server = FastMCP(
    name="aegis-pharmacovigilance-mcp",
)


@mcp_server.tool(
    name="mcp_calculate_drug_clearance",
    description="Deterministically calculates drug washout periods and deficit days.",
)
def mcp_calculate_drug_clearance(
    drug_name: str,
    days_since_last_dose: int,
    required_washout_days: int | None = None,
) -> dict[str, Any]:
    """Calculates whether a prior therapy has cleared the required washout interval."""
    return calculate_drug_clearance_fastmcp(
        drug_name=drug_name,
        days_since_last_dose=days_since_last_dose,
        required_washout_days=required_washout_days,
    )


@mcp_server.tool(
    name="mcp_evaluate_adverse_events",
    description="Maps adverse event terms to MedDRA v26 ontology and checks for CTCAE grade / borderline safety flags.",
)
def mcp_evaluate_adverse_events(clinical_text: str) -> dict[str, Any]:
    """Evaluates clinician notes for immune-related adverse events and steroid tapers."""
    return evaluate_adverse_event_safety(clinical_text)


if __name__ == "__main__":
    mcp_server.run()
