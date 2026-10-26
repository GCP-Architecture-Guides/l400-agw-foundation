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

"""Modular Lego Block 2: FastMCP Pharmacological Washout Engine.

Deconstructs monolithic regex parsing into an isolated, deterministic
FastMCP tool for oncology washout calculations.

Resolves:
- Monolithic Washout Parsing Failure (e.g. PT-901 Tagrisso/osimertinib 21d vs 14d)
- Checkpoint inhibitors (pembrolizumab/Keytruda 28d, nivolumab/Opdivo 28d)
- Targeted kinase inhibitors (osimertinib/Tagrisso 14d, dabrafenib 14d)
- Chemotherapy (docetaxel 14d, paclitaxel 14d, cisplatin 14d)
"""

from __future__ import annotations

import re
from typing import Any, Final
from fastmcp import FastMCP

# Initialize FastMCP Server for Washout Calculator
washout_mcp_server = FastMCP(
    name="aegis-washout-mcp",
)

# Canonical Drug Washout Knowledge Base
_DRUG_WASHOUT_DAYS: Final[dict[str, int]] = {
    # Checkpoint Inhibitors (PD-1 / PD-L1 / CTLA-4)
    "pembrolizumab": 28,
    "keytruda": 28,
    "nivolumab": 28,
    "opdivo": 28,
    "atezolizumab": 28,
    "durvalumab": 28,
    "ipilimumab": 42,
    # Targeted Kinase Inhibitors (EGFR / BRAF / KRAS)
    "osimertinib": 14,
    "tagrisso": 14,
    "erlotinib": 14,
    "gefitinib": 14,
    "dabrafenib": 14,
    "tafinlar": 14,
    "trametinib": 14,
    "sotorasib": 14,
    "adagrasib": 14,
    # Chemotherapy
    "docetaxel": 14,
    "taxotere": 14,
    "paclitaxel": 14,
    "carboplatin": 14,
    "cisplatin": 14,
    "oxaliplatin": 14,
    "gemcitabine": 14,
}

_DRUG_ALIAS_MAP: Final[dict[str, str]] = {
    "keytruda": "pembrolizumab",
    "opdivo": "nivolumab",
    "tagrisso": "osimertinib",
    "tafinlar": "dabrafenib",
    "taxotere": "docetaxel",
}


def resolve_canonical_drug(drug_name: str) -> str:
    """Normalizes trade names and colloquial terms to canonical generic drug names."""
    clean = drug_name.strip().lower()
    return _DRUG_ALIAS_MAP.get(clean, clean)


@washout_mcp_server.tool(
    name="calculate_washout_clearance",
    description="Calculates pharmacological washout satisfaction and deficit days.",
)
def calculate_washout_clearance(
    drug_name: str,
    days_since_last_dose: int | None = None,
    required_washout_days: int | None = None,
    days_elapsed: int | None = None,
) -> dict[str, Any]:
    """Calculates clearance satisfaction for a prior therapy.

    Args:
        drug_name: Generic or brand name of prior medication.
        days_since_last_dose: Days elapsed since last dose.
        required_washout_days: Protocol required washout window (optional).
        days_elapsed: Synonym for days_since_last_dose.

    Returns:
        Structured evaluation of washout satisfaction.
    """
    days = days_since_last_dose if days_since_last_dose is not None else (days_elapsed or 0)
    canonical = resolve_canonical_drug(drug_name)
    standard_req = _DRUG_WASHOUT_DAYS.get(canonical, 28)
    protocol_req = required_washout_days if required_washout_days is not None else standard_req

    is_satisfied = days >= protocol_req
    deficit = max(0, protocol_req - days)
    overall_status = "WASHOUT_SATISFIED" if is_satisfied else "WASHOUT_DEFICIT"
    rationale = (
        f"Prior therapy {drug_name} ({canonical}): {days} days elapsed vs {protocol_req} days required. "
        f"Status: {overall_status} (Deficit: {deficit} days)."
    )

    return {
        "mcp_server": "aegis-washout-mcp",
        "drug_input": drug_name,
        "canonical_drug": canonical,
        "days_elapsed": days,
        "days_since_last_dose": days,
        "required_washout_days": protocol_req,
        "washout_satisfied": is_satisfied,
        "washout_period_satisfied": is_satisfied,
        "overall_status": overall_status,
        "deficit_days": deficit,
        "washout_deficit_days": deficit,
        "confidence": 0.98,
        "clinical_rationale": rationale,
    }


# Convenience alias for module consumers
calculate_drug_clearance_fastmcp = calculate_washout_clearance


def parse_washout_from_text(text: str) -> dict[str, Any]:
    """Robust clinical NLP extraction of drug names, elapsed days, and protocol requirements."""
    # Pattern 1: e.g. "finished her last dose of Tagrisso (osimertinib) 21 days ago, and the trial requires a 14-day washout"
    tagrisso_match = re.search(
        r"(?:last\s+dose\s+of\s+|dose\s+of\s+|therapy\s+|prior\s+)?([A-Za-z]+(?:\s*\([A-Za-z]+\))?)\s*(?:completed|discontinued|ended|finished)?\s*(\d+)\s*days\s*ago.*?requires\s*(?:a\s*)?(\d+)[-\s]*day\s*washout",
        text,
        re.IGNORECASE,
    )
    if tagrisso_match:
        drug_raw = tagrisso_match.group(1).split("(")[0].strip()
        elapsed = int(tagrisso_match.group(2))
        req = int(tagrisso_match.group(3))
        return calculate_washout_clearance(drug_raw, elapsed, req)

    # Pattern 2: e.g. "Last Pembrolizumab dose was 35 days ago (required washout: 28 days)"
    standard_match = re.search(
        r"(?:prior|last)?\s*([A-Za-z]+(?:\s*\([A-Za-z]+\))?)\s*(?:dose|therapy|infusion)?\s*(?:was|completed|discontinued|ended)?\s*(\d+)\s*days\s*ago.*?(?:required\s*washout[:\s]*(\d+)\s*days?)?",
        text,
        re.IGNORECASE,
    )
    if standard_match:
        drug_raw = standard_match.group(1).split("(")[0].strip()
        elapsed = int(standard_match.group(2))
        req = int(standard_match.group(3)) if standard_match.group(3) else None
        return calculate_washout_clearance(drug_raw, elapsed, req)

    # Fallback default
    return {
        "mcp_server": "aegis-washout-mcp",
        "drug_input": "unknown",
        "canonical_drug": "unknown",
        "days_elapsed": 0,
        "required_washout_days": 28,
        "washout_satisfied": False,
        "deficit_days": 28,
        "confidence": 0.50,
    }
