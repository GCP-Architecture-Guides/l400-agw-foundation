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

"""Routing and perimeter interceptor tools for Trial Matching Supervisor.

TASK 1 CHALLENGE:
Learners implement the HIPAA De-Identification & GINA Title II Isolation Interceptor.
Use `lego_blocks/block_1_hipaa_gina_rules.py` as your reference implementation!

TASK 5 CHALLENGE:
Learners enforce downscoped IAM OIDC service token validation and calling permissions.
Use `lego_blocks/block_6_oidc_auth_guard.py` as your reference implementation!
"""

from __future__ import annotations

import logging
from typing import Any

from app.contracts import ClinicalIntakeEnvelope

logger = logging.getLogger(__name__)


def intercept_and_deidentify_intake(
    patient_id: str,
    raw_clinical_notes: str,
    trial_id: str = "NCT-AEGIS-001",
) -> dict[str, Any]:
    """Intercepts raw intake text at the security perimeter.

    Sanitizes HIPAA Safe Harbor direct identifiers and quarantines GINA Title II
    hereditary risk markers before distributing work to domain sub-agents.

    TODO (Task 1): Connect this function to `sanitize_hipaa_pii` and
    `quarantine_gina_germline_data` from `lego_blocks.block_1_hipaa_gina_rules`.
    """
    raise NotImplementedError(
        "TODO (Task 1): Implement intercept_and_deidentify_intake in "
        "agents/trial_matching_supervisor/routing_tools.py using "
        "lego_blocks/block_1_hipaa_gina_rules.py"
    )


def verify_mesh_caller_authorization(
    token: str,
    expected_target: str,
) -> dict[str, Any]:
    """Validates downscoped IAM OIDC service token and caller permissions.

    TODO (Task 5): Connect this function to `verify_oidc_service_token`
    from `lego_blocks.block_6_oidc_auth_guard`.
    """
    raise NotImplementedError(
        "TODO (Task 5): Implement verify_mesh_caller_authorization in "
        "agents/trial_matching_supervisor/routing_tools.py using "
        "lego_blocks/block_6_oidc_auth_guard.py"
    )
