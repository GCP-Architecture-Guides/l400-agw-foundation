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

"""Synthesis tools for Trial Eligibility Synthesizer.

TASK 3: Deterministic boolean gating and mandatory HITL gate triggers.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from lego_blocks.block_5_hitl_synthesizer import synthesize_trial_verdict

logger = logging.getLogger(__name__)


def _parse_report(report_input: Any) -> dict[str, Any]:
    """Parse a report from JSON string or dict."""
    if isinstance(report_input, str):
        try:
            return json.loads(report_input)
        except (json.JSONDecodeError, TypeError):
            return {}
    if isinstance(report_input, dict):
        return report_input
    return {}


def evaluate_trial_eligibility(
    genomic_report_json: Any,
    pv_report_json: Any,
    cohort_report_json: Any,
) -> dict[str, Any]:
    """Combines domain worker reports into an audited deterministic trial verdict.

    Uses the 2-gate synthesis engine from block_5:
    - Gate 1 (FIRST): HITL triggers (low confidence, unparseable labs, borderline safety)
    - Gate 2 (SECOND): Boolean criteria (genomic + washout + ECOG + cohort)
    """
    genomic_report = _parse_report(genomic_report_json)
    pv_report = _parse_report(pv_report_json)
    cohort_report = _parse_report(cohort_report_json)

    verdict = synthesize_trial_verdict(
        genomic_report=genomic_report,
        pv_report=pv_report,
        cohort_report=cohort_report,
    )

    return verdict.model_dump()
