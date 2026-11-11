#!/usr/bin/env python3
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

"""Interactive CISO Red-Team Scoreboard for Aegis TrialShield.

Executes all 5 autograded checkpoint scripts (Tasks 1-5), calculates the
candidate's cumulative grading score, and visualizes progress alongside the
CISO Statutory Liability Meter (HIPAA $1.9M + GINA $300K exposure).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

MAX_STATUTORY_LIABILITY_USD: int = 2_200_000
MAX_LAB_SCORE: int = 100

TASK_DEFINITIONS: list[dict[str, Any]] = [
    {
        "task": 1,
        "name": "HIPAA Safe Harbor & GINA Title II Interceptor",
        "script": "scripts/verify_task_1.py",
        "max_points": 15,
        "statutory_risk": "HIPAA Direct PHI / GINA Discrimination",
    },
    {
        "task": 2,
        "name": "FastMCP Washout Engine & FHIR Lab Normalizer",
        "script": "scripts/verify_task_2.py",
        "max_points": 20,
        "statutory_risk": "Clinical Trial Washout Protocol Violation",
    },
    {
        "task": 3,
        "name": "Deterministic Synthesis & Mandatory HITL Gate",
        "script": "scripts/verify_task_3.py",
        "max_points": 25,
        "statutory_risk": "Unsupervised Autonomous Enrollment Liability",
    },
    {
        "task": 4,
        "name": "ADK Sub-Agent Decoupling & Typed Contracts",
        "script": "scripts/verify_task_4.py",
        "max_points": 20,
        "statutory_risk": "Monolithic Blast Radius & Prompt Injection",
    },
    {
        "task": 5,
        "name": "Least Privilege IAM & OIDC Token Enforcement",
        "script": "scripts/verify_task_5.py",
        "max_points": 20,
        "statutory_risk": "Over-Permissioned God-Mode Service Account",
    },
]

# ANSI escape codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
DIM = "\033[2m"


def calculate_statutory_liability(total_score: int, max_score: int = MAX_LAB_SCORE) -> int:
    """Calculate remaining statutory liability exposure in USD.

    Exposure scales down proportionally as security controls pass verification:
    - 0 / 100 pts -> $2,200,000 (Maximum HIPAA $1.9M + GINA $300K exposure)
    - 100 / 100 pts -> $0 (Full production clearance approved)
    """
    if total_score >= max_score:
        return 0
    if total_score <= 0:
        return MAX_STATUTORY_LIABILITY_USD
    fraction_unmitigated = 1.0 - (total_score / float(max_score))
    return int(MAX_STATUTORY_LIABILITY_USD * fraction_unmitigated)


def get_status_description(total_score: int, max_score: int = MAX_LAB_SCORE) -> str:
    """Generate status description based on current score."""
    liability = calculate_statutory_liability(total_score, max_score)
    if total_score >= max_score:
        return "$0 Statutory Exposure (CISO PRODUCTION LAUNCH APPROVED)"
    if total_score <= 0:
        return (
            "$2,200,000 Statutory Exposure "
            "(HIPAA $1.9M + GINA $300K — STOP-WORK ORDER ACTIVE)"
        )
    return (
        f"${liability:,} Statutory Exposure "
        f"(STOP-WORK ORDER ACTIVE — {max_score - total_score} pts deficit)"
    )


def run_single_verification(task_def: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Execute a single task verification script and parse points."""
    script_path = repo_root / task_def["script"]
    max_pts = task_def["max_points"]
    task_num = task_def["task"]

    if not script_path.exists():
        return {
            "task": task_num,
            "name": task_def["name"],
            "score": 0,
            "max_points": max_pts,
            "passed": False,
            "error": f"Script {task_def['script']} not found",
        }

    cmd = [sys.executable, str(script_path)]
    result = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=False)

    score = 0
    # Match pattern: 'Task X Total Score: Y/Z points'
    score_match = re.search(
        rf"Task\s+{task_num}\s+Total\s+Score:\s*(\d+)/(\d+)",
        result.stdout,
    )
    if score_match:
        score = int(score_match.group(1))
    elif result.returncode == 0:
        score = max_pts
    else:
        score = 0

    return {
        "task": task_num,
        "name": task_def["name"],
        "score": score,
        "max_points": max_pts,
        "passed": score == max_pts,
        "returncode": result.returncode,
    }


def render_bar(score: int, max_pts: int, width: int = 12) -> str:
    """Render a text progress bar."""
    if max_pts <= 0:
        return "░" * width
    filled = int((score / float(max_pts)) * width)
    filled = max(0, min(width, filled))
    empty = width - filled
    return ("█" * filled) + ("░" * empty)


def run_scoreboard(json_output: bool = False) -> int:
    """Execute all verification scripts and render the scoreboard."""
    repo_root = Path(__file__).resolve().parent.parent

    task_results: list[dict[str, Any]] = []
    total_score = 0

    for task_def in TASK_DEFINITIONS:
        res = run_single_verification(task_def, repo_root)
        task_results.append(res)
        total_score += res["score"]

    liability_usd = calculate_statutory_liability(total_score, MAX_LAB_SCORE)
    status_str = get_status_description(total_score, MAX_LAB_SCORE)

    if json_output:
        payload = {
            "total_score": total_score,
            "max_score": MAX_LAB_SCORE,
            "liability_usd": liability_usd,
            "status": status_str,
            "tasks": task_results,
        }
        print(json.dumps(payload, indent=2))
        return 0 if total_score == MAX_LAB_SCORE else 1

    # ANSI Terminal Dashboard Rendering
    width = 76
    print()
    print(f"{CYAN}{BOLD}╔{'═' * (width - 2)}╗{RESET}")
    title = "🛡️  AEGIS TRIALSHIELD: CISO RED-TEAM SCOREBOARD"
    padding = (width - 2 - len(title) + 1) // 2
    print(f"{CYAN}{BOLD}║{' ' * padding}{title}{' ' * (width - 2 - padding - len(title) + 1)}║{RESET}")
    print(f"{CYAN}{BOLD}╠{'═' * (width - 2)}╣{RESET}")

    for r in task_results:
        t_num = r["task"]
        t_name = r["name"]
        t_score = r["score"]
        t_max = r["max_points"]
        bar = render_bar(t_score, t_max, 10)

        if r["passed"]:
            status_tag = f"{GREEN}{BOLD}PASS{RESET}"
            bar_colored = f"{GREEN}[{bar}]{RESET}"
            pts_str = f"{GREEN}{t_score:>2}/{t_max:>2} pts{RESET}"
        else:
            status_tag = f"{RED}{BOLD}FAIL{RESET}"
            bar_colored = f"{RED}[{bar}]{RESET}"
            pts_str = f"{RED}{t_score:>2}/{t_max:>2} pts{RESET}"

        # Truncate or pad name
        name_display = (t_name[:40] + "..") if len(t_name) > 42 else t_name
        line_content = f"  Task {t_num}: {name_display:<42} {bar_colored} {pts_str}  {status_tag}"
        print(f"{CYAN}{BOLD}║{RESET}{line_content:<83}{CYAN}{BOLD}║{RESET}")

    print(f"{CYAN}{BOLD}╠{'═' * (width - 2)}╣{RESET}")

    total_bar = render_bar(total_score, MAX_LAB_SCORE, 18)
    if total_score == MAX_LAB_SCORE:
        total_colored = f"{GREEN}{BOLD}[{total_bar}] {total_score:>3}/{MAX_LAB_SCORE} points (100% COMPLETE){RESET}"
    else:
        total_colored = f"{YELLOW}{BOLD}[{total_bar}] {total_score:>3}/{MAX_LAB_SCORE} points ({total_score}%){RESET}"

    tot_line = f"  TOTAL MESH SCORE:  {total_colored}"
    print(f"{CYAN}{BOLD}║{RESET}{tot_line:<90}{CYAN}{BOLD}║{RESET}")
    print(f"{CYAN}{BOLD}╠{'═' * (width - 2)}╣{RESET}")

    # Statutory Liability Meter
    meter_header = f"  {BOLD}CISO STATUTORY LIABILITY METER:{RESET}"
    print(f"{CYAN}{BOLD}║{RESET}{meter_header:<84}{CYAN}{BOLD}║{RESET}")

    if total_score == MAX_LAB_SCORE:
        liability_display = f"  {GREEN}{BOLD}✅ $0 Statutory Exposure (CISO PRODUCTION LAUNCH APPROVED){RESET}"
    elif total_score == 0:
        liability_display = (
            f"  {RED}{BOLD}🛑 $2,200,000 Statutory Exposure "
            f"(HIPAA $1.9M + GINA $300K — STOP-WORK ORDER ACTIVE){RESET}"
        )
    else:
        liability_display = (
            f"  {YELLOW}{BOLD}⚠️  ${liability_usd:,} Statutory Exposure "
            f"(REMEDIATION IN PROGRESS — STOP-WORK ORDER ACTIVE){RESET}"
        )

    print(f"{CYAN}{BOLD}║{RESET}{liability_display:<93}{CYAN}{BOLD}║{RESET}")
    print(f"{CYAN}{BOLD}╚{'═' * (width - 2)}╝{RESET}")
    print()

    return 0 if total_score == MAX_LAB_SCORE else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aegis TrialShield CISO Red-Team Scoreboard",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output scoreboard results as JSON for automated grading",
    )
    args = parser.parse_args()
    sys.exit(run_scoreboard(json_output=args.json))


if __name__ == "__main__":
    main()
