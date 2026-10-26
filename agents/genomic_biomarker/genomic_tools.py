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

"""Genomic Biomarker tools for somatic oncology driver validation."""

from __future__ import annotations

import logging
import re
from typing import Any

from lego_blocks.block_1_hipaa_gina_rules import quarantine_gina_germline_data

logger = logging.getLogger(__name__)

# Actionable somatic oncology driver mutations for NCT-AEGIS-001
_SOMATIC_DRIVERS: dict[str, list[str]] = {
    "EGFR": ["L858R", "Exon 19 del", "T790M", "C797S", "Exon 20 ins"],
    "KRAS": ["G12C", "G12D", "G12V", "G13D"],
    "BRAF": ["V600E", "V600K"],
    "ALK": ["EML4-ALK", "fusion"],
    "ROS1": ["fusion"],
    "RET": ["fusion"],
    "MET": ["Exon 14 skipping", "amplification"],
    "HER2": ["amplification", "Exon 20 ins"],
    "NTRK": ["fusion"],
}


def validate_somatic_biomarker(
    variant_text: str,
    reported_confidence: float = 0.95,
) -> dict[str, Any]:
    """Validates somatic tumor NGS alterations against trial NCT-AEGIS-001 criteria.

    Preserves somatic drivers (EGFR, KRAS, BRAF) while quarantining germline markers.
    """
    # First quarantine any germline markers from the variant text
    cleaned_text, quarantined_markers, has_germline = quarantine_gina_germline_data(variant_text)

    # Search for actionable somatic drivers
    found_gene = None
    found_variant = None
    is_actionable = False

    for gene, variants in _SOMATIC_DRIVERS.items():
        if re.search(rf"\b{gene}\b", cleaned_text, re.IGNORECASE):
            found_gene = gene
            for var in variants:
                if re.search(re.escape(var), cleaned_text, re.IGNORECASE):
                    found_variant = f"{gene} {var}"
                    is_actionable = True
                    break
            if found_gene and not found_variant:
                # Gene mentioned but no specific variant matched
                found_variant = f"{gene} (variant unspecified)"
            break

    # Determine genomic status
    if is_actionable and found_gene:
        overall_status = "VALID_SOMATIC"
        interpretation = f"Actionable somatic {found_variant} detected. Eligible for NCT-AEGIS-001."
    elif found_gene:
        overall_status = "INCONCLUSIVE"
        interpretation = f"{found_gene} detected but no actionable variant matched."
    elif has_germline and not found_gene:
        # Only germline found, no somatic — wild type tumor
        overall_status = "NO_ACTIONABLE_SOMATIC"
        interpretation = "No actionable somatic driver detected. Germline markers quarantined per GINA Title II."
    else:
        overall_status = "NO_ACTIONABLE_SOMATIC"
        interpretation = "No actionable somatic oncology driver mutations detected in submitted specimen."

    return {
        "patient_id": "UNKNOWN",
        "trial_id": "NCT-AEGIS-001",
        "overall_genomic_status": overall_status,
        "variant_status": overall_status,
        "gene": found_gene or "",
        "somatic_variant": found_variant or "",
        "variant_normalized": found_variant or "",
        "is_actionable": is_actionable,
        "confidence": reported_confidence,
        "gina_title_ii_flag": has_germline,
        "germline_quarantined": has_germline,
        "redacted_germline_markers": quarantined_markers,
        "clinical_interpretation": interpretation,
        "details": interpretation,
    }
