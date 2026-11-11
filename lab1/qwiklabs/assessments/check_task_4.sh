#!/usr/bin/env bash
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

set -uo pipefail

TASK_NUM=4
TASK_NAME="ADK Sub-Agent Decoupling & Typed Contracts"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPO_ROOT}"

echo "======================================================================"
echo "🎯 Qwiklabs Assessment: Checkpoint ${TASK_NUM} (${TASK_NAME})"
echo "======================================================================"

set +e
uv run python "scripts/verify_task_${TASK_NUM}.py"
EXIT_CODE=$?
set -e

echo ""
if [ "${EXIT_CODE}" -eq 0 ]; then
    echo "======================================================================"
    echo "✅ ASSESSMENT PASSED: Task ${TASK_NUM} (${TASK_NAME}) verified with full points!"
    echo "======================================================================"
else
    echo "======================================================================"
    echo "❌ ASSESSMENT INCOMPLETE: Task ${TASK_NUM} did not meet all grading criteria."
    echo "💡 Run 'make hint TASK=${TASK_NUM} LEVEL=1' for architectural guidance."
    echo "======================================================================"
fi

exit "${EXIT_CODE}"
