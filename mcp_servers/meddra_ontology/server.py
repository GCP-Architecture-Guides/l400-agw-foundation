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

"""FastMCP Server for MedDRA Adverse Event & Pharmacovigilance Washout Calculations.

TASK 2 CHALLENGE:
Expose deterministic pharmacology washout calculation and adverse event
lookup as FastMCP tools for sub-agents to invoke.
Use `lego_blocks/block_2_fastmcp_washout.py` and `lego_blocks/block_4_meddra_adverse_events.py`!
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp_server = FastMCP(
    name="aegis-pharmacovigilance-mcp",
)


@mcp_server.tool(
    name="mcp_calculate_drug_clearance",
    description="Deterministically calculates drug washout periods (e.g. 14d for Tagrisso, 28d for Keytruda) and deficit days.",
)
def mcp_calculate_drug_clearance(
    drug_name: str,
    days_since_last_dose: int,
    required_washout_days: int | None = None,
) -> dict[str, Any]:
    """Calculates whether a prior therapy has cleared the required washout interval.

    TODO (Task 2): Use calculate_drug_clearance_fastmcp from
    lego_blocks.block_2_fastmcp_washout to implement this tool.
    """
    raise NotImplementedError(
        "TODO (Task 2): Implement mcp_calculate_drug_clearance in "
        "mcp_servers/meddra_ontology/server.py using lego_blocks/block_2_fastmcp_washout.py"
    )


@mcp_server.tool(
    name="mcp_evaluate_adverse_events",
    description="Maps adverse event terms to MedDRA v26 ontology and checks for CTCAE grade / borderline safety flags.",
)
def mcp_evaluate_adverse_events(clinical_text: str) -> dict[str, Any]:
    """Evaluates clinician notes for immune-related adverse events and steroid tapers.

    TODO (Task 2): Use evaluate_adverse_event_safety from
    lego_blocks.block_4_meddra_adverse_events to implement this tool.
    """
    raise NotImplementedError(
        "TODO (Task 2): Implement mcp_evaluate_adverse_events in "
        "mcp_servers/meddra_ontology/server.py using lego_blocks/block_4_meddra_adverse_events.py"
    )


if __name__ == "__main__":
    mcp_server.run()
