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

"""Clinical Cohort Agent Package.

Specialized domain sub-agent responsible for:
1. Extracting ASCO/ECOG functional performance status (0-5) from unstructured clinician notes.
2. Normalizing laboratory values to FHIR R4 standard SI units (UCUM).
3. Flagging legacy unparseable lab units (e.g., mg%) to trigger Human-in-the-Loop review.
"""

from .cohort_agent import cohort_agent

__all__ = ["cohort_agent"]
