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

"""FastMCP Server for FHIR R4 Laboratory Normalization & ECOG Scoring.

TASK 2 CHALLENGE:
Expose deterministic FHIR UCUM laboratory conversions and ECOG
performance status scoring as FastMCP micro-tools.
Use `lego_blocks/block_3_fhir_lab_normalizer.py` as your reference implementation!
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp_server = FastMCP(
    name="aegis-clinical-cohort-mcp",
)


@mcp_server.tool(
    name="mcp_normalize_renal_labs",
    description="Normalizes serum creatinine measurements to FHIR R4 standard units (umol/L) and flags legacy unparseable units (mg%).",
)
def mcp_normalize_renal_labs(
    raw_value: float,
    raw_unit: str = "mg/dL",
    unparseable_labs: bool = False,
) -> dict[str, Any]:
    """Standardizes laboratory creatinine observations.

    TODO (Task 2): Use normalize_fhir_renal_labs from
    lego_blocks.block_3_fhir_lab_normalizer to implement this tool.
    """
    raise NotImplementedError(
        "TODO (Task 2): Implement mcp_normalize_renal_labs in "
        "mcp_servers/fhir_lab_normalizer/server.py using lego_blocks/block_3_fhir_lab_normalizer.py"
    )


@mcp_server.tool(
    name="mcp_extract_ecog_score",
    description="Extracts ASCO/ECOG functional score (0-5) from clinician notes without falsy-zero bugs.",
)
def mcp_extract_ecog_score(clinical_notes: str) -> dict[str, Any]:
    """Scores ECOG performance status from free-text notes.

    TODO (Task 2): Use extract_ecog_status from
    lego_blocks.block_3_fhir_lab_normalizer to implement this tool.
    """
    raise NotImplementedError(
        "TODO (Task 2): Implement mcp_extract_ecog_score in "
        "mcp_servers/fhir_lab_normalizer/server.py using lego_blocks/block_3_fhir_lab_normalizer.py"
    )


if __name__ == "__main__":
    mcp_server.run()
