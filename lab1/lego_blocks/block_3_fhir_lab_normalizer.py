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

"""Modular Lego Block 3: FHIR R4 Lab Normalizer & ECOG Performance Status Engine.

Implements:
1. Deterministic FHIR R4 / UCUM unit conversion for laboratory observations:
   - Serum Creatinine: mg/dL -> umol/L (conversion factor 88.42)
   - Protocol boundary threshold: Creatinine <= 1.50 mg/dL (132.63 umol/L)
   - Explicit detection and flagging of legacy non-standard units (e.g., 'mg%')
     triggering unparseable_labs=True and lowering confidence to 0.70 for HITL escalation.

2. ASCO / ECOG Performance Status Classifier:
   - Evaluates performance status on standard 0-5 scale.
   - CRITICAL BUG FIX: Fixes the Python falsy-zero bug ('if not ecog_score:').
     Score 0 ('fully active') is a valid integer and must be treated as optimal fitness!
"""

from __future__ import annotations

import logging
import re
from typing import Any, Final

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FHIR R4 UCUM Unit Conversion Factors
# ---------------------------------------------------------------------------
_FHIR_LAB_CONVERSION: Final[dict[str, dict[str, tuple[str, str, float]]]] = {
    "serum_creatinine": {
        "mg/dl": ("umol/L", "http://unitsofmeasure.org", 88.42),
        "mg/100ml": ("umol/L", "http://unitsofmeasure.org", 88.42),
        "umol/l": ("umol/L", "http://unitsofmeasure.org", 1.0),
        "µmol/l": ("umol/L", "http://unitsofmeasure.org", 1.0),
        "micromol/l": ("umol/L", "http://unitsofmeasure.org", 1.0),
    },
    "creatinine": {
        "mg/dl": ("umol/L", "http://unitsofmeasure.org", 88.42),
        "mg/100ml": ("umol/L", "http://unitsofmeasure.org", 88.42),
        "umol/l": ("umol/L", "http://unitsofmeasure.org", 1.0),
    },
    "hemoglobin": {
        "g/dl": ("g/L", "http://unitsofmeasure.org", 10.0),
        "g/l": ("g/L", "http://unitsofmeasure.org", 1.0),
    },
    "platelet_count": {
        "10*3/ul": ("10*9/L", "http://unitsofmeasure.org", 1.0),
        "k/ul": ("10*9/L", "http://unitsofmeasure.org", 1.0),
        "10*9/l": ("10*9/L", "http://unitsofmeasure.org", 1.0),
    },
}

_ACCEPTABLE_MAX_CREATININE_UMOL_L: Final[float] = 132.63  # 1.50 mg/dL * 88.42


def normalize_fhir_renal_labs(
    lab_type: str,
    raw_value: float,
    raw_unit: str,
    unparseable_labs: bool = False,
) -> dict[str, Any]:
    """Converts clinical laboratory observation to standard FHIR R4 SI units.

    Args:
        lab_type: Laboratory assay identifier (e.g. 'serum_creatinine').
        raw_value: Raw numeric value reported by laboratory.
        raw_unit: Source unit string (e.g. 'mg/dL', 'mg%').
        unparseable_labs: Upstream flag for unparseable legacy notation.

    Returns:
        Structured normalization dictionary with renal acceptability assessment.
    """
    clean_lab = lab_type.lower().strip().replace(" ", "_").replace("-", "_")
    unit_lower = raw_unit.strip().lower()

    # Detect legacy non-UCUM units (such as 'mg%' seen in legacy lab systems)
    if unparseable_labs or "mg%" in unit_lower or "unparseable" in unit_lower or "%" in unit_lower:
        logger.warning("Unparseable legacy lab unit detected: %s %s", raw_value, raw_unit)
        return {
            "lab_type": lab_type,
            "raw_value": raw_value,
            "raw_unit": raw_unit,
            "normalized_value": raw_value,
            "normalized_unit": raw_unit,
            "fhir_system": "http://unitsofmeasure.org",
            "conversion_applied": False,
            "conversion_status": "UNPARSEABLE_UNIT",
            "unparseable_unit": True,
            "unparseable_labs": True,
            "status": "UNPARSEABLE_UNIT",
            "confidence": 0.70,
            "renal_status": "NOT_ASSESSED",
            "clinical_note": (
                f"Lab '{lab_type}' contains non-UCUM legacy or unparseable unit '{raw_unit}'. "
                "Triggering Human-in-the-Loop (HITL) oncologist escalation."
            ),
        }

    conversions = _FHIR_LAB_CONVERSION.get(clean_lab, {})
    if unit_lower in conversions:
        norm_unit, system, factor = conversions[unit_lower]
        normalized_value = round(raw_value * factor, 2)

        # Assess renal status for creatinine
        renal_status = "NOT_ASSESSED"
        if "creatinine" in clean_lab:
            if normalized_value <= _ACCEPTABLE_MAX_CREATININE_UMOL_L:
                renal_status = "ACCEPTABLE"
            else:
                renal_status = "ELEVATED"

        return {
            "lab_type": lab_type,
            "raw_value": raw_value,
            "raw_unit": raw_unit,
            "normalized_value": normalized_value,
            "normalized_unit": norm_unit,
            "fhir_system": system,
            "conversion_applied": True,
            "conversion_status": "CONVERTED",
            "unparseable_unit": False,
            "unparseable_labs": False,
            "status": "NORMALIZED",
            "confidence": 0.98,
            "renal_status": renal_status,
            "clinical_note": f"Normalized {raw_value} {raw_unit} -> {normalized_value} {norm_unit} ({renal_status}).",
        }

    # Unsupported or unknown lab/unit
    return {
        "lab_type": lab_type,
        "raw_value": raw_value,
        "raw_unit": raw_unit,
        "normalized_value": raw_value,
        "normalized_unit": raw_unit,
        "fhir_system": "http://unitsofmeasure.org",
        "conversion_applied": False,
        "conversion_status": "UNSUPPORTED_UNIT",
        "unparseable_unit": True,
        "unparseable_labs": True,
        "status": "UNSUPPORTED_UNIT",
        "confidence": 0.75,
        "renal_status": "NOT_ASSESSED",
        "clinical_note": f"Unit '{raw_unit}' for lab '{lab_type}' is unsupported.",
    }


# ---------------------------------------------------------------------------
# ECOG Performance Status Extraction (Safe Falsy-Zero Implementation)
# ---------------------------------------------------------------------------
_ECOG_NUMERIC_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:ECOG|ecog|performance status|PS)\s*(?:is|score|status|of|:)?\s*([0-5])\b",
    re.IGNORECASE,
)

_ECOG_KEYWORDS: Final[list[tuple[int, list[str]]]] = [
    (4, [r"completely disabled", r"bedridden", r"no self[\s-]?care"]),
    (3, [r"limited self[\s-]?care", r"confined to (?:bed|chair) (?:>|more than) 50%"]),
    (2, [r"ambulatory >50%", r"capable of all self[\s-]?care but unable to work"]),
    (1, [r"restricted in physically strenuous activity", r"light or sedentary work", r"ambulatory"]),
    (0, [r"fully active", r"able to carry on all pre-disease", r"no restrictions", r"optimal fitness"]),
]


def extract_ecog_status(clinical_notes: str) -> dict[str, Any]:
    """Extracts ECOG performance status (0-5) from clinician notes without falsy-zero bugs.

    Args:
        clinical_notes: Free-form physician notes or trial intake text.

    Returns:
        Structured ECOG evaluation dictionary.
    """
    if not clinical_notes or not clinical_notes.strip():
        return {
            "ecog_score": 1,
            "ambulatory_status": "DEFAULT_FALLBACK",
            "confidence": 0.60,
            "clinical_note": "No notes provided; defaulted to ECOG 1.",
        }

    # 1. Search for explicit numeric score (e.g. "ECOG 0", "ECOG score: 1")
    match = _ECOG_NUMERIC_PATTERN.search(clinical_notes)
    if match:
        score = int(match.group(1))
        # Note: In Python, score=0 is falsy, so we NEVER do 'if not score:'!
        status_labels = {
            0: "FULLY_ACTIVE",
            1: "AMBULATORY",
            2: "AMBULATORY_SELF_CARE",
            3: "LIMITED_SELF_CARE",
            4: "COMPLETELY_DISABLED",
            5: "DECEASED",
        }
        return {
            "ecog_score": score,
            "ambulatory_status": status_labels.get(score, "UNKNOWN"),
            "confidence": 0.99,
            "eligible_for_trial": score <= 2,
            "clinical_note": f"Explicit numeric ECOG {score} extracted ({status_labels.get(score, 'UNKNOWN')}).",
        }

    # 2. Keyword fallback matching
    for score, patterns in _ECOG_KEYWORDS:
        for pat in patterns:
            if re.search(pat, clinical_notes, re.IGNORECASE):
                status_labels = {
                    0: "FULLY_ACTIVE",
                    1: "AMBULATORY",
                    2: "AMBULATORY_SELF_CARE",
                    3: "LIMITED_SELF_CARE",
                    4: "COMPLETELY_DISABLED",
                    5: "DECEASED",
                }
                return {
                    "ecog_score": score,
                    "ambulatory_status": status_labels.get(score, "UNKNOWN"),
                    "confidence": 0.90,
                    "eligible_for_trial": score <= 2,
                    "clinical_note": f"Matched clinical descriptor '{pat}' -> ECOG {score}.",
                }

    # Default fallback
    return {
        "ecog_score": 1,
        "ambulatory_status": "AMBULATORY",
        "confidence": 0.70,
        "eligible_for_trial": True,
        "clinical_note": "Defaulted to ECOG 1 from general clinical notes.",
    }
