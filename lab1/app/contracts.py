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

"""Standardized Pydantic Data Contracts for Aegis TrialShield Multi-Agent Mesh.

These typed schemas establish strict boundary contracts between:
1. Clinical Intake / Safe Harbor Redaction Layer (ClinicalIntakeEnvelope)
2. Genomic Biomarker Specialist (GenomicWorkerReport)
3. Pharmacovigilance & Washout Specialist (PharmacovigilanceReport)
4. Clinical Cohort & Lab Normalization Specialist (ClinicalCohortReport)
5. Deterministic Synthesis & HITL Gatekeeper (SynthesizerVerdict)

Enforces:
- Strict field typing and data validation
- GINA Title II isolation invariants
- Audit-compliant serialization for FDA 21 CFR Part 312
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class EligibilityStatus(str, Enum):
    """Clinical trial eligibility decision states."""
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    PENDING_REVIEW = "PENDING_REVIEW"


class GenomicStatus(str, Enum):
    """Genomic biomarker qualification status."""
    VALID_SOMATIC = "VALID_SOMATIC"
    INELIGIBLE_MUTATION = "INELIGIBLE_MUTATION"
    NO_ACTIONABLE_SOMATIC = "NO_ACTIONABLE_SOMATIC"
    INCONCLUSIVE = "INCONCLUSIVE"


class ClinicalIntakeEnvelope(BaseModel):
    """Standardized envelope for incoming patient screening requests."""
    model_config = ConfigDict(extra="ignore")

    patient_id: str = Field(default="UNKNOWN", description="Unique de-identified patient tracking ID")
    trial_id: str = Field(default="NCT-AEGIS-001", description="Clinical trial protocol ID")
    raw_text: str = Field(default="", description="Raw clinical text submitted by intake clinician")
    sanitized_text: str = Field(default="", description="Sanitized text with PII and GINA germline markers redacted")
    sanitized_clinical_notes: str = Field(default="", description="Alias for sanitized_text")
    scrubbed_entities: list[dict[str, str]] = Field(default_factory=list, description="Audit trail of scrubbed identifiers")
    has_pii_violation: bool = Field(default=False, description="True if direct identifiers were detected in raw text")
    pii_redacted: bool = Field(default=False, description="True if PII was redacted")
    has_gina_violation: bool = Field(default=False, description="True if hereditary germline markers were detected")
    gina_quarantined: bool = Field(default=False, description="True if GINA germline markers were quarantined")
    quarantined_germline_markers: list[str] = Field(default_factory=list, description="Quarantined germline markers")


class GenomicWorkerReport(BaseModel):
    """Structured report returned by GenomicBiomarkerAgent."""
    model_config = ConfigDict(extra="ignore")

    patient_id: str = Field(default="UNKNOWN", description="Patient ID")
    trial_id: str = Field(default="NCT-AEGIS-001", description="Clinical trial protocol ID")
    status: GenomicStatus = Field(default=GenomicStatus.VALID_SOMATIC, description="Genomic biomarker qualification status")
    variant_status: GenomicStatus = Field(default=GenomicStatus.VALID_SOMATIC, description="Alias for status")
    gene: str = Field(default="", description="Gene symbol (e.g. EGFR, KRAS, BRAF)")
    somatic_variant: str = Field(default="", description="Validated somatic tumor mutation")
    variant_normalized: str = Field(default="", description="Normalized variant notation")
    hgvs_nomenclature: str = Field(default="", description="Canonical HGVS nomenclature")
    hgvs_cdna: str = Field(default="", description="HGVS cDNA")
    hgvs_protein: str = Field(default="", description="HGVS protein")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Genomic assay confidence score")
    gina_title_ii_flag: bool = Field(default=False, description="True if germline carrier findings were scrubbed")
    germline_quarantined: bool = Field(default=False, description="True if germline markers quarantined")
    redacted_germline_markers: list[str] = Field(default_factory=list, description="List of detected germline markers")
    is_actionable: bool = Field(default=False, description="True if somatic variant matches trial inclusion criteria")
    clinical_interpretation: str = Field(default="", description="Genomic clinical interpretation")
    details: str = Field(default="", description="Clinical genomic interpretation narrative")


class PharmacovigilanceReport(BaseModel):
    """Structured report returned by PharmacovigilanceAgent."""
    model_config = ConfigDict(extra="ignore")

    patient_id: str = Field(default="UNKNOWN", description="Patient ID")
    trial_id: str = Field(default="NCT-AEGIS-001", description="Clinical trial protocol ID")
    drug_name: str = Field(default="", description="Name of medication")
    prior_therapy: str = Field(default="", description="Name of most recent prior systemic therapy")
    days_since_last_dose: int = Field(default=0, description="Days elapsed since discontinuation of prior therapy")
    required_washout_days: int = Field(default=28, description="Mandatory trial protocol washout period in days")
    washout_status: str = Field(default="WASHOUT_SATISFIED", description="Washout status label")
    washout_satisfied: bool = Field(default=True, description="True if days_since_last_dose >= required_washout_days")
    washout_period_satisfied: bool = Field(default=True, description="Alias for washout_satisfied")
    washout_deficit_days: int = Field(default=0, description="Days remaining until washout completion if unsatisfied")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Pharmacovigilance parsing confidence score")
    borderline_safety_flag: bool = Field(default=False, description="True if resolving grade 2 toxicity or active taper")
    ctcae_adverse_events: list[dict[str, Any]] = Field(default_factory=list, description="Structured MedDRA/CTCAE findings")
    identified_contraindications: list[str] = Field(default_factory=list, description="Contraindications")
    clinical_summary: str = Field(default="", description="PV clinical summary")
    details: str = Field(default="", description="Pharmacovigilance clinical assessment narrative")


class ClinicalCohortReport(BaseModel):
    """Structured report returned by ClinicalCohortAgent."""
    model_config = ConfigDict(extra="ignore")

    patient_id: str = Field(default="UNKNOWN", description="Patient ID")
    trial_id: str = Field(default="NCT-AEGIS-001", description="Clinical trial protocol ID")
    cohort_status: str = Field(default="COHORT_ELIGIBLE", description="Cohort status")
    cohort_eligible: bool = Field(default=True, description="True if ECOG <= 2 and labs meet protocol criteria")
    ecog_score: int | None = Field(default=1, ge=0, le=5, description="ECOG score (0 to 5, zero-safe)")
    ambulatory_status: str = Field(default="AMBULATORY", description="Ambulatory status")
    ecog_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="ECOG scoring confidence")
    renal_status: str = Field(default="ACCEPTABLE", description="Renal acceptability")
    normalized_serum_creatinine: float | None = Field(default=None, description="Normalized creatinine")
    normalized_unit: str | None = Field(default=None, description="Normalized unit")
    creatinine_mg_dl: float | None = Field(default=None, description="Normalized serum creatinine in mg/dL")
    unparseable_labs: bool = Field(default=False, description="True if non-standard/legacy units could not be converted")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Overall clinical cohort confidence score")
    lab_normalizations: dict[str, Any] = Field(default_factory=dict, description="Detailed normalized lab measurements")
    clinical_summary: str = Field(default="", description="Cohort clinical summary")
    details: str = Field(default="", description="Clinical cohort fitness narrative")


class GateChecks(BaseModel):
    """Deterministic boolean invariant gates for trial eligibility."""
    model_config = ConfigDict(extra="ignore")

    genomic_eligible: bool = Field(default=False, description="Genomic biomarker matches protocol")
    genomic_gate: bool = Field(default=False, description="Alias for genomic_eligible")
    washout_satisfied: bool = Field(default=False, description="Pharmacological washout period satisfied")
    washout_gate: bool = Field(default=False, description="Alias for washout_satisfied")
    ecog_eligible: bool = Field(default=False, description="ECOG performance status <= 2 (zero-safe)")
    ecog_gate: bool = Field(default=False, description="Alias for ecog_eligible")
    cohort_eligible: bool = Field(default=False, description="Laboratory and physiological criteria met")
    cohort_gate: bool = Field(default=False, description="Alias for cohort_eligible")

    def all_passed(self) -> bool:
        """Evaluates whether all 4 gating invariants are satisfied."""
        g = self.genomic_eligible or self.genomic_gate
        w = self.washout_satisfied or self.washout_gate
        e = self.ecog_eligible or self.ecog_gate
        c = self.cohort_eligible or self.cohort_gate
        return bool(g and w and e and c)


class SynthesizerVerdict(BaseModel):
    """Deterministic final verdict synthesized from domain specialist reports."""
    model_config = ConfigDict(extra="ignore")

    patient_id: str = Field(default="UNKNOWN", description="Patient ID")
    trial_id: str = Field(default="NCT-AEGIS-001", description="Clinical trial protocol ID")
    eligibility_status: EligibilityStatus = Field(..., description="Final decision: ELIGIBLE, INELIGIBLE, or PENDING_REVIEW")
    human_intervention_required: bool = Field(..., description="Mandatory HITL escalation gatekeeper")
    gate_checks: GateChecks = Field(default_factory=GateChecks, description="Individual sub-gate evaluation results")
    exclusion_reasons: list[str] = Field(default_factory=list, description="Clinical exclusion reasons if INELIGIBLE")
    hitl_reasons: list[str] = Field(default_factory=list, description="Specific triggers requiring Oncologist review")
    confidence: float = Field(default=1.0, description="Overall synthesized confidence score")
    min_confidence: float = Field(default=1.0, description="Lowest confidence score across all domain specialists")
    clinical_summary: str = Field(default="", description="Comprehensive synthesized clinical summary")
    audit_event_id: str = Field(default="", description="Unique Firestore/audit log tracking hash")

