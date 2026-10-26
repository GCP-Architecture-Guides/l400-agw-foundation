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

"""Trial Eligibility Synthesizer Agent Package.

Specialized synthesis sub-agent responsible for:
1. Deterministic boolean gating invariant:
   Eligible iff (Genomic == VALID_SOMATIC) AND (Washout == WASHOUT_SATISFIED) AND (ECOG <= 2) AND (Cohort == COHORT_ELIGIBLE).
2. Mandatory Human-In-The-Loop (HITL) gate triggers:
   Triggered on confidence < 0.85, unparseable lab units, or borderline safety flags.
3. Generating auditable clinical screening reports and Firestore logs.
"""

from .synthesizer_agent import synthesizer_agent

__all__ = ["synthesizer_agent"]
