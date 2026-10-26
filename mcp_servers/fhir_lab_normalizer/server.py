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

"""FastMCP Server for FHIR R4 Laboratory Normalization & ECOG Scoring."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP
from lego_blocks.block_3_fhir_lab_normalizer import (
    normalize_fhir_renal_labs,
    extract_ecog_status,
)

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
    """Standardizes laboratory creatinine observations."""
    return normalize_fhir_renal_labs(
        lab_type="serum_creatinine",
        raw_value=raw_value,
        raw_unit=raw_unit,
        unparseable_labs=unparseable_labs,
    )


@mcp_server.tool(
    name="mcp_extract_ecog_score",
    description="Extracts ASCO/ECOG functional score (0-5) from clinician notes without falsy-zero bugs.",
)
def mcp_extract_ecog_score(clinical_notes: str) -> dict[str, Any]:
    """Scores ECOG performance status from free-text notes."""
    return extract_ecog_status(clinical_notes)


if __name__ == "__main__":
    mcp_server.run()
