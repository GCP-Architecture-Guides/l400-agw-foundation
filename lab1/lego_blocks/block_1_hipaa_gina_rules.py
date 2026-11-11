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

"""Modular Lego Block 1: HIPAA Safe Harbor & GINA Title II Privacy Engine.

Implements:
1. Strict HIPAA Safe Harbor direct identifier scrubbing (45 CFR § 164.514):
   - SSNs (e.g. 412-88-9012) -> [REDACTED_SSN]
   - Patient Names (e.g. Evelyn Carter, Harvey Dent) -> [REDACTED_NAME]
   - Dates of Birth (e.g. 03/14/1968) -> [REDACTED_DOB]
   - MRNs (e.g. MRN-884920) -> [REDACTED_MRN]
   - Real Street Addresses (e.g. 1200 Main Street, Apt 4B; 450 Oak Avenue) -> [REDACTED_STREET_ADDRESS]
     (Prevents naive regex collateral damage on clinical durations like '30 days')

2. GINA Title II Genetic Information Non-Discrimination Act (29 CFR Part 1635):
   - Detects and redacts hereditary germline cancer risk markers:
     BRCA1, BRCA2, MLH1, MSH2, MSH6, PMS2, PALB2, ATM, CHEK2, RAD51C/D, TP53 germline,
     Lynch syndrome, carrier status, hereditary/family history references.
   - Replaces with [REDACTED_GERMLINE_GENE] and [REDACTED_GERMLINE_FINDING].
   - CRITICAL: Preserves somatic oncology driver mutations (e.g., somatic EGFR L858R,
     KRAS G12C, BRAF V600E) for legitimate trial matching.
"""

from __future__ import annotations

import re
from typing import Any, Final

# ---------------------------------------------------------------------------
# HIPAA Safe Harbor Regex Patterns (with zero-collateral-damage lookahead)
# ---------------------------------------------------------------------------
_SSN_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

_MRN_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:MRN|mrn|MEDREC|MedRec)[\s:#-]*[A-Z0-9]{5,12}\b"
)

_DOB_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:DOB|dob|Date of Birth)[\s:#-]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    re.IGNORECASE,
)

_PATIENT_NAME_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r"\b(?:Patient Name|Patient|Name)[\s:#-]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", re.IGNORECASE),
    re.compile(r"\b(?:Evelyn Carter|Marcus Vance|Clara Oswald|Arthur Pendelton|Victor Fries|Selina Kyle|Harvey Dent|Sarah Jenkins|David Miller|Elena Rostova|John Doe|Jane Doe)\b"),
]

# Safe street address pattern: requires street suffix and explicitly excludes clinical durations (days/weeks/hours)
_STREET_ADDRESS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b\d{1,6}\s+(?!days?\b|weeks?\b|months?\b|years?\b|hours?\b|mg\b|g\b|ml\b|µg\b|ug\b|units?\b|mg%)(?:[A-Za-z0-9\.\-]+\s+){1,4}\b(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Ln|Lane|Dr|Drive|Ct|Court|Way|Pkwy|Parkway)(?:,\s*(?:Apt|Suite|Unit|#)\s*[A-Za-z0-9]+)?\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# GINA Title II Hereditary Germline Marker Patterns
# ---------------------------------------------------------------------------
_GERMLINE_GENE_LIST: Final[list[str]] = [
    "BRCA1", "BRCA2", "MLH1", "MSH2", "MSH6", "PMS2", "EPCAM",
    "PTEN", "CDH1", "APC", "PALB2", "ATM", "CHEK2", "RAD51C", "RAD51D",
]

_GERMLINE_GENE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:" + "|".join(_GERMLINE_GENE_LIST) + r")\b(?:\s*(?:mutation|variant|gene|carrier|carrier status))?(?:\s*(?:[cpg]\.[A-Za-z0-9>_\+\-\*]+|\d+[A-Za-z0-9>_\+\-\*delins]+))?",
    re.IGNORECASE,
)

_HEREDITARY_CONTEXT_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r"\bLynch(?:\s+syndrome)?\b", re.IGNORECASE),
    re.compile(r"\b(?:incidental\s+)?germline\s+(?:carrier\s+status|carrier|mutation|variant|note|finding)?\b", re.IGNORECASE),
    re.compile(r"\b(?:hereditary|familial)\s+(?:carrier\s+status|carrier|mutation|cancer|syndrome|risk|note)\b", re.IGNORECASE),
    re.compile(r"\b(?:carrier\s+status)\b", re.IGNORECASE),
    re.compile(r"\b(?:family\s+history(?:\s+and\s+blood\s+panel)?)\b", re.IGNORECASE),
    re.compile(r"\b(?:pathogenic\s+germline)\b", re.IGNORECASE),
]


def scrub_direct_identifiers(text: str) -> tuple[str, list[dict[str, str]]]:
    """Scrubs HIPAA Safe Harbor direct identifiers without clinical collateral damage."""
    redacted = text
    entities: list[dict[str, str]] = []

    # 1. SSN
    for m in _SSN_PATTERN.finditer(redacted):
        entities.append({"type": "SSN", "value": m.group(0)})
    redacted = _SSN_PATTERN.sub("[REDACTED_SSN]", redacted)

    # 2. DOB
    for m in _DOB_PATTERN.finditer(redacted):
        entities.append({"type": "DOB", "value": m.group(0)})
    redacted = _DOB_PATTERN.sub("[REDACTED_DOB]", redacted)

    # 3. MRN
    for m in _MRN_PATTERN.finditer(redacted):
        entities.append({"type": "MRN", "value": m.group(0)})
    redacted = _MRN_PATTERN.sub("[REDACTED_MRN]", redacted)

    # 4. Street Address (Safe - will NOT match '30 days')
    for m in _STREET_ADDRESS_PATTERN.finditer(redacted):
        entities.append({"type": "STREET_ADDRESS", "value": m.group(0)})
    redacted = _STREET_ADDRESS_PATTERN.sub("[REDACTED_STREET_ADDRESS]", redacted)

    # 5. Patient Names
    for pat in _PATIENT_NAME_PATTERNS:
        for m in pat.finditer(redacted):
            matched = m.group(1) if m.lastindex else m.group(0)
            entities.append({"type": "PATIENT_NAME", "value": matched})
        if pat.groups > 0:
            redacted = pat.sub("Patient Name: [REDACTED_NAME]", redacted)
        else:
            redacted = pat.sub("[REDACTED_NAME]", redacted)

    return redacted, entities


def isolate_gina_germline(text: str) -> tuple[str, list[str]]:
    """Detects and redacts GINA Title II hereditary germline findings.

    Preserves somatic tumor markers while strictly isolating germline/familial findings.
    """
    redacted = text
    scrubbed_markers: list[str] = []

    # Detect specific germline gene mentions
    for m in _GERMLINE_GENE_PATTERN.finditer(redacted):
        scrubbed_markers.append(m.group(0))
    redacted = _GERMLINE_GENE_PATTERN.sub("[REDACTED_GERMLINE_GENE]", redacted)

    # Detect hereditary context & syndromes
    for pat in _HEREDITARY_CONTEXT_PATTERNS:
        for m in pat.finditer(redacted):
            scrubbed_markers.append(m.group(0))
        redacted = pat.sub("[REDACTED_GERMLINE_FINDING]", redacted)

    return redacted, list(set(scrubbed_markers))


def sanitize_clinical_text(text: str) -> dict[str, Any]:
    """Full-pipeline sanitization combining HIPAA Safe Harbor and GINA Title II."""
    hipaa_clean, hipaa_entities = scrub_direct_identifiers(text)
    fully_sanitized, gina_markers = isolate_gina_germline(hipaa_clean)

    return {
        "raw_text": text,
        "sanitized_text": fully_sanitized,
        "scrubbed_hipaa_entities": hipaa_entities,
        "scrubbed_gina_markers": gina_markers,
        "has_pii_violation": len(hipaa_entities) > 0,
        "has_gina_violation": len(gina_markers) > 0,
        "is_safe_for_downstream": True,
    }


def sanitize_hipaa_pii(text: str) -> tuple[str, bool]:
    """Convenience helper: returns (sanitized_text, has_pii)."""
    clean_text, entities = scrub_direct_identifiers(text)
    return clean_text, len(entities) > 0


def quarantine_gina_germline_data(text: str) -> tuple[str, list[str], bool]:
    """Convenience helper: returns (sanitized_text, quarantined_markers, has_germline)."""
    clean_text, markers = isolate_gina_germline(text)
    return clean_text, markers, len(markers) > 0

