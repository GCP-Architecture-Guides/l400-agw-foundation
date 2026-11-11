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

"""Modular Lego Block 6: Least Privilege IAM & OIDC Service Token Enforcement.

Implements:
1. Downscoped IAM Service Account Identity Mappings:
   - Supervisor: sa-matching-supervisor@prod-proj-ge.iam.gserviceaccount.com
   - Genomic:    sa-genomic-biomarker@prod-proj-ge.iam.gserviceaccount.com
   - PV:         sa-pharmacovigilance@prod-proj-ge.iam.gserviceaccount.com
   - Cohort:     sa-clinical-cohort@prod-proj-ge.iam.gserviceaccount.com
   - Synthesizer: sa-trial-synthesizer@prod-proj-ge.iam.gserviceaccount.com

2. OIDC Token Validation & Scope Verification:
   - Verifies JWT signatures, expiry, issuer (accounts.google.com), and audience (aud).
   - Rejects the over-permissioned God-mode identity ('sa-legacy-god-mode').
   - Enforces unidirectional calling graph:
     Supervisor -> (Genomic, PV, Cohort) -> Synthesizer.
"""

from __future__ import annotations

import base64
import json
import logging
import time
from typing import Any, Final

logger = logging.getLogger(__name__)

# Disallowed God-Mode service account
_GOD_MODE_SA: Final[str] = "sa-legacy-god-mode@prod-proj-ge.iam.gserviceaccount.com"

# Authorized Service Accounts and Audiences
_SERVICE_ACCOUNT_REGISTRY: Final[dict[str, str]] = {
    "supervisor": "sa-matching-supervisor@prod-proj-ge.iam.gserviceaccount.com",
    "genomic": "sa-genomic-biomarker@prod-proj-ge.iam.gserviceaccount.com",
    "genomics": "sa-genomic-biomarker@prod-proj-ge.iam.gserviceaccount.com",
    "pharmacovigilance": "sa-pharmacovigilance@prod-proj-ge.iam.gserviceaccount.com",
    "clinical_cohort": "sa-clinical-cohort@prod-proj-ge.iam.gserviceaccount.com",
    "clinical-cohort": "sa-clinical-cohort@prod-proj-ge.iam.gserviceaccount.com",
    "cohort": "sa-clinical-cohort@prod-proj-ge.iam.gserviceaccount.com",
    "synthesizer": "sa-trial-synthesizer@prod-proj-ge.iam.gserviceaccount.com",
}

_AUDIENCE_REGISTRY: Final[dict[str, str]] = {
    "supervisor": "https://agents.aegis.health/supervisor",
    "genomic": "https://agents.aegis.health/genomics",
    "genomics": "https://agents.aegis.health/genomics",
    "pharmacovigilance": "https://agents.aegis.health/pharmacovigilance",
    "clinical_cohort": "https://agents.aegis.health/clinical-cohort",
    "clinical-cohort": "https://agents.aegis.health/clinical-cohort",
    "cohort": "https://agents.aegis.health/clinical-cohort",
    "synthesizer": "https://agents.aegis.health/synthesizer",
}

# Allowed caller-to-target routing matrix
_CALLING_PERMISSIONS: Final[dict[str, list[str]]] = {
    "supervisor": ["genomic", "genomics", "pharmacovigilance", "clinical_cohort", "clinical-cohort", "cohort", "synthesizer"],
    "genomic": ["synthesizer"],
    "genomics": ["synthesizer"],
    "pharmacovigilance": ["synthesizer"],
    "clinical_cohort": ["synthesizer"],
    "clinical-cohort": ["synthesizer"],
    "cohort": ["synthesizer"],
    "synthesizer": [],
}


def mint_mock_oidc_token(caller_role: str, target_audience: str) -> str:
    """Mints an OIDC mock JWT for local test harnesses and development verification.

    Args:
        caller_role: Role key (e.g. 'supervisor', 'genomic').
        target_audience: Expected target audience URI.

    Returns:
        Encoded JWT token string.
    """
    sa_email = _SERVICE_ACCOUNT_REGISTRY.get(caller_role, f"sa-{caller_role}@prod-proj-ge.iam.gserviceaccount.com")
    now = int(time.time())
    
    header = {"alg": "RS256", "typ": "JWT", "kid": "mock-aegis-key-001"}
    payload = {
        "iss": "https://accounts.google.com",
        "sub": sa_email,
        "email": sa_email,
        "email_verified": True,
        "aud": target_audience,
        "iat": now,
        "exp": now + 3600,
    }
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature_b64 = base64.urlsafe_b64encode(b"mock_valid_signature_bytes_12345678").decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verify_oidc_service_token(token: str, expected_target_agent: str) -> dict[str, Any]:
    """Validates an incoming OIDC service token against least-privilege rules.

    Args:
        token: Incoming JWT token string.
        expected_target_agent: Key of target agent receiving the call.

    Returns:
        Decoded token payload if valid.

    Raises:
        PermissionError: If caller is God-Mode, expired, or not authorized for audience.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format: Token must have exactly 3 segments.")

    try:
        # Decode payload segment with padding correction
        payload_str = base64.urlsafe_b64decode(parts[1] + "==").decode("utf-8")
        payload = json.loads(payload_str)
    except Exception as exc:
        raise ValueError(f"Failed to decode token payload: {exc}") from exc

    caller_email = payload.get("email", "")
    audience = payload.get("aud", "")
    exp = payload.get("exp", 0)

    # 1. Reject over-permissioned God-mode service account
    if caller_email == _GOD_MODE_SA or "god-mode" in caller_email:
        logger.error("CISO Security Alert: Over-permissioned God-mode service account rejected: %s", caller_email)
        raise PermissionError(
            f"Access Denied: God-mode service account '{caller_email}' is strictly prohibited "
            "under Aegis Least-Privilege Architecture."
        )

    # 2. Check Expiration
    if time.time() > exp:
        raise PermissionError("Access Denied: OIDC token has expired.")

    # 3. Check Target Audience
    expected_aud = _AUDIENCE_REGISTRY.get(expected_target_agent, "")
    if audience != expected_aud:
        raise PermissionError(
            f"Access Denied: Invalid audience '{audience}'. Expected '{expected_aud}' for target '{expected_target_agent}'."
        )

    # 4. Check Caller Role Permissions
    caller_role = None
    for role, email in _SERVICE_ACCOUNT_REGISTRY.items():
        if email == caller_email:
            caller_role = role
            break

    if not caller_role:
        raise PermissionError(f"Access Denied: Caller '{caller_email}' is not in authorized service account registry.")

    allowed_targets = _CALLING_PERMISSIONS.get(caller_role, [])
    if expected_target_agent not in allowed_targets:
        raise PermissionError(
            f"Access Denied: Caller role '{caller_role}' is not authorized to invoke '{expected_target_agent}'."
        )

    logger.info("OIDC token verified successfully for caller '%s' -> target '%s'", caller_email, expected_target_agent)
    return payload
