#!/usr/bin/env python3
"""
Cryptographic Verifier for `assessment_report_<goal_id>.md` (For LLM Assessor & Grading Backend)

Verifies that:
  1. The assessment report file contains both the Canonical Assessment JSON block
     and the Google-signed RS256 OIDC JWT (`id_token`).
  2. Re-serializing the Canonical Assessment JSON block (`sort_keys=True, separators=(',', ':')`)
     produces the exact `sha256` digest claimed in the Google-signed JWT's `aud` parameter.
  3. The JWT's `RS256` signature and `kid` match Google's active OIDC signing certificates
     (`https://www.googleapis.com/oauth2/v3/certs` & `https://oauth2.googleapis.com/tokeninfo`),
     confirming it was minted by Google Cloud IAM Credentials API (`iss: https://accounts.google.com`)
     for a service account in the student's GCP project.
  4. The `project`, `principal`, `student`, and `score` inside the signed JWT `aud` claim match
     the canonical JSON payload (preventing a student from modifying their name, project ID, or score).
"""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import ssl
import sys
from typing import Any, Dict, Tuple
import urllib.error
import urllib.parse
import urllib.request


def _build_ssl_context() -> ssl.SSLContext:
    cafile = os.environ.get("SSL_CERT_FILE", "")
    if not cafile or not Path(cafile).is_file():
        if Path("/etc/ssl/cert.pem").is_file():
            cafile = "/etc/ssl/cert.pem"
        else:
            try:
                import certifi  # type: ignore
                cafile = certifi.where()
            except Exception:
                cafile = ""
    if cafile:
        return ssl.create_default_context(cafile=cafile)
    return ssl.create_default_context()


_SSL_CTX = _build_ssl_context()


def _http_json(url: str) -> Tuple[int, Any]:
    req = urllib.request.Request(url=url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace") if err.fp else "{}"
        try:
            return err.code, json.loads(raw)
        except Exception:
            return err.code, {"error": raw}
    except Exception as exc:
        return 0, {"error": str(exc)}


def _decode_jwt_parts(jwt_token: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    parts = jwt_token.strip().split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format (expected 3 dot-separated parts).")

    def _b64(seg: str) -> Dict[str, Any]:
        padded = seg + "=" * (-len(seg) % 4)
        return json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))

    return _b64(parts[0]), _b64(parts[1])


def verify_markdown_report(md_path: Path, expected_student: str = "", expected_project: str = "") -> Dict[str, Any]:
    text = md_path.read_text(encoding="utf-8")

    json_match = re.search(
        r"<!-- BEGIN_CANONICAL_ASSESSMENT_JSON -->\s*```json\s*(.*?)\s*```\s*<!-- END_CANONICAL_ASSESSMENT_JSON -->",
        text,
        re.DOTALL,
    )
    if not json_match:
        return {"valid": False, "reason": "Missing CANONICAL_ASSESSMENT_JSON block in Markdown file."}

    jwt_match = re.search(
        r"<!-- BEGIN_GOOGLE_OIDC_JWT -->\s*```text\s*(.*?)\s*```\s*<!-- END_GOOGLE_OIDC_JWT -->",
        text,
        re.DOTALL,
    )
    if not jwt_match:
        return {"valid": False, "reason": "Missing GOOGLE_OIDC_JWT block in Markdown file."}

    raw_json_str = json_match.group(1).strip()
    jwt_token = jwt_match.group(1).strip()

    try:
        payload_obj = json.loads(raw_json_str)
    except Exception as exc:
        return {"valid": False, "reason": f"Invalid JSON in canonical block: {exc}"}

    # 1. Recompute canonical SHA-256
    canonical_bytes = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    recomputed_sha256 = hashlib.sha256(canonical_bytes).hexdigest()

    # 2. Decode JWT header & payload
    try:
        jwt_header, jwt_payload = _decode_jwt_parts(jwt_token)
    except Exception as exc:
        return {"valid": False, "reason": f"Malformed JWT: {exc}"}

    # 3. Verify JWT against Google OIDC JWKS & tokeninfo endpoint
    st_certs, certs_data = _http_json("https://www.googleapis.com/oauth2/v3/certs")
    google_kids = {k.get("kid") for k in certs_data.get("keys", [])} if isinstance(certs_data, dict) else set()
    kid = jwt_header.get("kid", "")
    kid_in_google_jwks = kid in google_kids

    st_ti, ti_data = _http_json(
        f"https://oauth2.googleapis.com/tokeninfo?id_token={urllib.parse.quote(jwt_token)}"
    )
    google_sig_verified = st_ti == 200 and isinstance(ti_data, dict) and ti_data.get("iss") == "https://accounts.google.com"

    # 4. Parse signed `aud` claim parameters
    aud_str = str(jwt_payload.get("aud", ""))
    parsed_aud = urllib.parse.urlparse(aud_str)
    aud_params = dict(urllib.parse.parse_qsl(parsed_aud.query))

    signed_sha256 = aud_params.get("sha256", "")
    signed_project = aud_params.get("project", "")
    signed_principal = aud_params.get("principal", "")
    signed_student = aud_params.get("student", "")
    signed_lab = aud_params.get("lab", "")
    signed_goal = aud_params.get("goal", "") or (aud_params.get("lab", "") if not signed_lab else "")
    signed_signer = aud_params.get("signer", "")
    signed_nonce = aud_params.get("nonce", "")
    signed_score = aud_params.get("score", "")

    payload_project = str(payload_obj.get("project", {}).get("project_id", ""))
    payload_principal = str(payload_obj.get("student_identity", {}).get("authenticated_principal_email", ""))
    payload_student = str(payload_obj.get("student_identity", {}).get("student_id", ""))
    meta_obj = payload_obj.get("metadata", {})
    payload_lab = str(meta_obj.get("lab_id", ""))
    payload_goal = str(meta_obj.get("goal_id", "") or (meta_obj.get("lab_id", "") if not payload_lab else ""))
    payload_nonce = str(meta_obj.get("submission_id", ""))
    payload_score = (
        f"{payload_obj.get('summary', {}).get('earned_points')}/"
        f"{payload_obj.get('summary', {}).get('max_points')}"
    )
    jwt_email = str(jwt_payload.get("email", ""))
    expected_sa_suffix = f"@{payload_project}.iam.gserviceaccount.com"
    signer_matches_project = jwt_email.endswith(expected_sa_suffix) and (
        not signed_signer or jwt_email == signed_signer
    )

    checks = {
        "sha256_matches_signed_jwt": recomputed_sha256 == signed_sha256,
        "google_jwks_kid_recognized": kid_in_google_jwks,
        "google_oidc_signature_verified": google_sig_verified,
        "jwt_issuer_is_google": jwt_payload.get("iss") == "https://accounts.google.com",
        "jwt_signer_matches_project_sa": signer_matches_project,
        "project_id_matches_jwt": payload_project == signed_project,
        "principal_matches_jwt": payload_principal == signed_principal,
        "student_id_matches_jwt": payload_student == signed_student,
        "score_matches_jwt": payload_score == signed_score,
    }
    if signed_lab and payload_lab:
        checks["lab_id_matches_jwt"] = payload_lab == signed_lab
    if signed_goal or payload_goal:
        checks["goal_id_matches_jwt"] = payload_goal == signed_goal
    if signed_nonce or payload_nonce:
        checks["submission_id_matches_jwt"] = payload_nonce == signed_nonce
    if expected_student:
        checks["expected_student_matches"] = expected_student in (signed_student, signed_principal)
    if expected_project:
        checks["expected_project_matches"] = expected_project == signed_project

    all_valid = all(checks.values())
    return {
        "valid": all_valid,
        "recomputed_sha256": recomputed_sha256,
        "signed_sha256": signed_sha256,
        "project_id": signed_project,
        "authenticated_principal": signed_principal,
        "student_id": signed_student,
        "lab_id": signed_lab or payload_lab,
        "goal_id": signed_goal or payload_goal,
        "submission_id": signed_nonce or payload_nonce,
        "score": signed_score,
        "jwt_signer_email": jwt_email,
        "jwt_kid": kid,
        "verification_checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify cryptographic signature and integrity of assessment_report.md")
    parser.add_argument("report_path", help="Path to assessment_report.md")
    parser.add_argument("--expected-student", default="", help="Optional expected student email/ID")
    parser.add_argument("--expected-project", default="", help="Optional expected GCP project ID")
    args = parser.parse_args()

    result = verify_markdown_report(
        Path(args.report_path).resolve(),
        expected_student=args.expected_student,
        expected_project=args.expected_project,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    sys.exit(main())
