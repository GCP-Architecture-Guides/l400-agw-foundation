# CEPF128-L400: Deconstruct the Monolithic Mega Agent & Architect a Secure Healthcare Multi-Agent Mesh

[![Lab Tier: L400 Expert](https://img.shields.io/badge/Lab_Tier-L400_Expert-red.svg)](https://cloud.google.com)
[![Google ADK](https://img.shields.io/badge/Framework-Google_ADK-blue.svg)](https://github.com/google/agent-development-kit)
[![Model: Gemini 3.7 Flash](https://img.shields.io/badge/Model-Gemini_3.7_Flash-4285F4.svg)](https://cloud.google.com/vertex-ai)
[![Compliance: HIPAA Safe Harbor & GINA Title II](https://img.shields.io/badge/Compliance-HIPAA_%7C_GINA-green.svg)](https://hhs.gov)
[![Autograder: 100/100 Pts](https://img.shields.io/badge/Autograder-100%2F100_Pts-brightgreen.svg)](Makefile)

---

## 1. What You Will Learn in This 2-Hour Lab

Welcome! In this hands-on lab, you will act as a Lead Cloud Security Architect tasked with remediating a high-risk AI healthcare application that failed its security audit. You do **NOT** need any medical background, biology training, or healthcare expertise—all medical formulas and rules are pre-built for you in ready-to-use Python helper modules ("Lego blocks").

By the end of this lab, you will know how to:
- **Deconstruct an Unsafe "Mega Agent":** Break down an all-powerful, single-prompt AI agent into 5 specialized micro-agents with clear, isolated boundaries and typed contracts using the **Google Agent Development Kit (ADK)** (Google's framework for building modular AI agents).
- **Sanitize Sensitive Patient Data at the Perimeter:** Intercept and scrub direct identifiers (Names, Social Security Numbers [SSNs], Medical Record Numbers [MRNs], and Dates of Birth) under **HIPAA** (US patient privacy law protecting personal identifiers) before any AI sees them, while fixing naive regex patterns so treatment durations like `"30 days"` are never corrupted.
- **Quarantine Protected Family Genetics:** Implement cryptographic isolation under **GINA (Genetic Information Nondiscrimination Act)** (US law that makes it illegal to use a person's inherited family DNA when making eligibility or employment decisions) to quarantine inherited family DNA (*Germline Variants*, like `BRCA1/2` or `PALB2`) into a private audit vault while safely passing tumor mutations (*Somatic Variants*, like `EGFR` or `KRAS`) to clinical screeners.
- **Stop AI Math Guesswork with FastMCP Tools:** Replace unreliable **AI guesswork in free text** with deterministic Python calculators via **FastMCP (Model Context Protocol)** (a standard way to connect AI agents to exact Python calculator tools so the AI doesn't guess math in free text) for drug cooldown timers and standardized kidney lab numbers.
- **Install a Two-Gate Human Safety Circuit-Breaker:** Eliminate dangerous binary Approve/Deny decisions by creating a mandatory **Human-in-the-Loop (HITL / `PENDING_REVIEW`)** safety gate that pauses the AI and routes cases to human doctors whenever confidence drops below 85% (`0.85`), lab units are unreadable (`mg%`), or active drug side effects are flagged.
- **Enforce Least-Privilege IAM & OIDC Bearer Tokens:** Revoke an over-permissioned God-mode service account (`sa-legacy-god-mode`) and enforce fine-grained **OIDC (OpenID Connect) Bearer Tokens** (cryptographic ID badges that prove which Service Account is calling a microservice) to secure agent-to-agent communication and reject off-topic prompt attacks.

---

## 2. The Business Case (Why the CISO Stopped the Launch)

To automate patient screening for an experimental lung cancer clinical trial (**`NCT-AEGIS-001`**), an engineering team took a risky shortcut: they deployed a single **"Monolithic Mega Agent"** (`TrialShield POC Agent`). 

They bundled everything—patient intake, genetic matching, medication safety checks, kidney lab reviews, and final trial eligibility decisions—into one massive prompt. Worse, they ran this mega agent under an all-powerful Google Cloud service account (`sa-legacy-god-mode`) with unrestricted administrative access across the entire project.

During red-team penetration testing, the Chief Information Security Officer (CISO) discovered critical security, legal, and patient safety flaws and issued an immediate **Stop-Work Order**, halting deployment due to severe enterprise risks:

1. **$1.9M+ HIPAA Privacy Liability:**
   - **HIPAA** (Health Insurance Portability and Accountability Act) is the US federal patient privacy law protecting personal identifiers like Names, Social Security Numbers (SSNs), Medical Record Numbers (MRNs), and Street Addresses.
   - The Mega Agent used a naive street-address regex that mistook medical durations like `"30 days"` for street names (corrupting clinical timelines to `[REDACTED_STREET_ADDRESS] ago`), while letting actual SSNs, MRNs, and patient names leak straight into plaintext outputs and audit logs. This triggers statutory penalties capped at **$1,900,000+ per year** under HHS OCR (Department of Health and Human Services Office for Civil Rights) Tier 4 willful neglect rules.
2. **$300,000 GINA Genetic Discrimination Liability:**
   - **GINA** (Genetic Information Nondiscrimination Act) is a US federal law that makes it illegal to use a person's inherited family DNA when making clinical eligibility or employment decisions.
   - The Mega Agent suffered a critical conceptual confusion: it failed to distinguish between a **Tumor Mutation (*Somatic Variant*, like `EGFR`, `KRAS`, `BRAF`)**, which is a DNA change found *only inside the cancer tumor* that the clinical trial *is* targeting, and **Inherited Family DNA (*Germline Variant*, like `BRCA1/2`, `MLH1`, `PALB2`)**, which is passed down from parents in normal blood and must be quarantined at the door as a protected secret. In patient `PT-704`, the agent used an inherited `BRCA2` mutation to approve an ineligible patient whose tumor lacked the required target! This unlawful commingling exposes the organization to **$300,000 per violation** under EEOC (Equal Employment Opportunity Commission) / ADA statutory damage limits.
3. **Clinical Safety Hazard from Binary Decisions (No Human Safety Net):**
   - The Mega Agent forced all decisions into a rigid binary output: `ELIGIBLE` or `INELIGIBLE`, hardcoding `human_intervention_required = False`.
   - When reviewing patient `PT-707`—who had active Grade 2 lung inflammation (pneumonitis) requiring steroid medication—the AI blindly approved the patient because a drug cooldown timer had passed, completely ignoring the dangerous active toxicity. In other cases (`PT-703`), it flatly denied viable candidates simply because a laboratory reported kidney numbers in an unfamiliar hospital unit format (`1.0 mg%`).
4. **Prompt Injection & Unbounded Blast Radius:**
   - Operating as an unconstrained God-mode account with zero domain boundaries, the agent cheerfully answered off-topic questions (like diabetes dosing and Boston weekend weather forecasts for `PT-905`), leaving the core clinical infrastructure wide open to prompt injection and mission drift.

> [!IMPORTANT]
> **Total Initial CISO Statutory Liability: $2,200,000 USD.** Your mission in this lab is to refactor this architecture and drive that liability down to **$0**!

---

## 3. Plain-English Glossary Table (No Medical Degree Needed!)

As a Cloud Security Architect or Software Engineer, use this translation matrix to map healthcare terms directly to familiar security and distributed systems concepts:

| Term in Lab | What It Means in Plain English | How to Think About It as a Security Architect |
| :--- | :--- | :--- |
| **HIPAA** | US patient privacy law protecting personal identifiers (Names, SSNs, MRNs, Dates of Birth, Street Addresses). | **Perimeter Data Loss Prevention (DLP):** Mandatory input sanitization that strips direct identifiers before data touches downstream models. |
| **GINA (Genetic Information Nondiscrimination Act)** | US federal law making it illegal to use inherited family DNA when making eligibility or employment decisions. | **Data Segregation & Quarantine:** Cryptographically isolate inherited family data into a separate compliance vault so evaluators cannot access it. |
| **Tumor Mutation (*Somatic Variant*, e.g., `EGFR`, `KRAS`, `BRAF`)** | DNA changes found *only inside the cancer tumor* that the clinical trial is designed to treat. | **Legitimate Screening Payload:** Authorized criteria attributes that must be verified against trial requirements. |
| **Inherited Family DNA (*Germline Variant*, e.g., `BRCA1/2`, `MLH1`, `PALB2`)** | Hereditary DNA changes passed down from parents, present in normal blood cells throughout life. | **Protected Secret / Toxic Data:** Restricted sensitive attributes that must be intercepted and quarantined at the door. |
| **Medication Safety & Drug Cooldown Timers (*Pharmacovigilance & Washout Period*)** | The minimum number of days a patient must wait after stopping an old medication (like *Keytruda* or *Tagrisso*) before starting a new trial drug to prevent toxic drug clashes. | **Time-Based Rate Limiting / Session Cooldown:** Temporal access policy requiring an elapsed time interval (`current_date - last_dose_date >= required_washout_days`). |
| **Daily Physical Activity Score (*ECOG Performance Status*, `0` to `5`)** | Standard activity score from `0` to `5`, where **`0` means 100% healthy and fully active**, `2` is the maximum allowed for the trial, and `3+` means too sick. | **Boundary Condition Validation Bug:** Watch out for the **Python Falsy-Zero Bug** (`if not ecog_score:`), which treats `0` as falsy `False` instead of valid integer `0` and wrongly rejects the healthiest patients! |
| **Standardizing Kidney Lab Units (*FHIR R4 & Serum Creatinine*)** | A blood test measuring kidney health (*serum creatinine*). Values must be converted from US units (`mg/dL`) to metric (`umol/L` by multiplying by `88.42`), checked against `<= 1.50 mg/dL`, and legacy units like `1.0 mg%` must be flagged. | **Input Schema Validation & Normalization:** Standardize payload units across microservices; trigger validation errors on malformed legacy units. |
| **ADK (Google Agent Development Kit)** | Google's framework for building modular, decoupled AI agents with structured tools and typed state management. | **Microservices Framework for Agents:** Enables modular separation of concerns instead of one bloated monolithic process. |
| **FastMCP (Model Context Protocol)** | An open protocol connecting AI agents to exact, deterministic Python calculator tools. | **Remote Procedure Call (RPC) for Tools:** Offloads critical math and data transforms to deterministic backend code instead of relying on AI guesswork in free text. |
| **HITL (Human-in-the-Loop / `PENDING_REVIEW`)** | A safety circuit-breaker that pauses the AI and routes the file to a human doctor whenever confidence is low (`< 85%`), lab units are unreadable, or active drug side effects exist. | **Circuit-Breaker / Manual Approval Gate:** CI/CD-style approval pipeline requiring human sign-off on high-risk or ambiguous requests. |
| **OIDC (OpenID Connect) Bearer Token** | Cryptographic JSON Web Token (JWT) proving which Service Account is calling a microservice. | **Mutual Authentication & Least Privilege:** Restricts service-to-service calls using cryptographic audience claims (`aud=https://agents.aegis.health/...`). |
| **AI Guesswork in Free Text (*formerly "Stochastic verification"* )** | Asking an LLM to calculate numbers, dates, or boolean rules inside its generative text response. | **Non-Deterministic Execution Risk:** Flawed pattern where identical inputs can yield conflicting outputs depending on model temperature. |
| **Exact Code Rules / Safety Gate (*formerly "Deterministic boolean gating invariant"* )** | Hardcoded, deterministic Python logic (`all_passed()`) that evaluates structured boolean flags. | **Hardened Policy Engine (PDP/PEP):** Guarantees zero hallucination in critical security and compliance decisions. |
| **Matching Tumor Mutation (*formerly "Biomarker concordance"* )** | Verifying that the patient's verified tumor mutation matches what the trial requires. | **Attribute Whitelist Matching:** Exact payload validation against authorized criteria. |
| **Off-Topic Questions (*formerly "Off-label pharmacology queries"* )** | Requests unrelated to trial eligibility (e.g., asking for diabetes medication dosages or weekend weather forecasts). | **Prompt Injection / Mission Drift:** Unauthorized out-of-scope requests that perimeter guardrails must reject. |

---

## 4. Side-by-Side Comparison Table

Here is how the broken monolithic prototype compares to the production-ready 5-agent mesh you will construct:

| Architecture Dimension | Broken Mega Agent (`TrialShield POC Agent`) | Target 5-Agent System (`TrialShield Production`) |
| :--- | :--- | :--- |
| **Agent Topology** | 1 Monolithic Agent handling intake, genetics, drug cooldowns, labs, and decisions in one prompt. | **5 Decoupled Agents:**<br>1. **Oncology Trial Coordinator** (`TrialMatchingSupervisor`)<br>2. **Tumor Genetics Reviewer** (`GenomicBiomarkerAgent`)<br>3. **Medication Safety Reviewer** (`PharmacovigilanceAgent`)<br>4. **Patient Health & Lab Reviewer** (`ClinicalCohortAgent`)<br>5. **Final Trial Decision Maker** (`TrialEligibilitySynthesizer`) |
| **Identity & IAM Access** | Over-permissioned God-mode service account (`sa-legacy-god-mode`) with full project access. | Least-privilege per-agent service accounts authenticated with audience-restricted **OIDC Bearer Tokens**. |
| **HIPAA Patient Privacy** | Naive street-address regex (`\b\d+\s+[A-Za-z]+\b`) that redacts `"30 days"` into `[REDACTED_STREET_ADDRESS]` while leaking SSNs, MRNs, and patient names. | Two-stage pre-model interceptor scrubbing all 18 HIPAA direct identifiers while safely preserving clinical treatment durations (`"30 days"`). |
| **GINA Genetic Quarantine** | Zero isolation; confuses inherited family DNA (`BRCA2`) with tumor targets, wrongly approving ineligible patient `PT-704`. | Cryptographic SHA-256 quarantine vault that isolates inherited family DNA (`BRCA1/2`, `PALB2`) while forwarding tumor mutations (`EGFR`, `KRAS`, `BRAF`). |
| **Calculations & Conversions** | **AI guesswork in free text:** attempts to calculate drug cooldown days and lab units inside LLM prose; fails on drug aliases (`PT-901`). | **FastMCP Calculator Tools:** deterministic Python functions calculating exact drug clearance half-lives and converting kidney lab units. |
| **Decision Logic & Determinism** | Stochastic text generation; outputs unstructured English explanations with unpredictable criteria evaluation. | **Exact code rules / Safety gate:** deterministic Python rule (`all_passed()`) evaluated over strongly-typed Pydantic data contracts. |
| **Human Safety Net (HITL)** | Binary only (`ELIGIBLE` / `INELIGIBLE`); hardcodes `human_intervention_required = False`, blindly enrolling toxic patients (`PT-707`). | **Mandatory `PENDING_REVIEW` Circuit-Breaker:** automatically escalates to a human doctor if confidence `< 85%`, lab units are unreadable, or active toxicities appear. |
| **Domain Scope & Guardrails** | Zero perimeter defense; happily dispenses diabetes drug dosing and Boston weather forecasts (`PT-905`). | Strict intake boundary guardrails; automatically generates audited refusal notices for out-of-scope requests. |

---

## 5. Visual Architecture Diagrams

### Diagram 1: The Broken Mega Agent (Vulnerable Architecture)

Notice the single God-mode account, the naive regex damaging clinical text, the confusion between family DNA and tumor mutations, the falsy-zero bug, and the absence of any human review safety net:

```mermaid
flowchart TD
    subgraph Client["Clinical Intake Portal"]
        Patient["Patient Record (PT-701 to PT-905)<br>Name, SSN, Family DNA, Tumor DNA, Labs"]
    end

    subgraph Monolith["Vulnerable Monolithic Agent (TrialShield POC Agent)"]
        direction TB
        GodMode["1. God-Mode Service Account<br>sa-legacy-god-mode@prod-proj-ge<br>(Unbounded Blast Radius)"]
        RegexDamage["2. '30 days' Street-Address Filter Bug<br>Redacts '30 days' to [REDACTED_STREET_ADDRESS]<br>Leaks SSNs, MRNs, and Patient Names"]
        GINAConfusion["3. Family DNA Mix-Up (GINA Breach)<br>Confuses Inherited BRCA2 with Tumor EGFR<br>Wrongly Approves Ineligible Patient PT-704"]
        FalsyZero["4. ECOG 0 Falsy-Zero Bug<br>'if not ecog_score:' treats 0 as False<br>Wrongly Rejects Healthiest Patients (PT-708)"]
        BinaryDecision["5. Binary Approve/Deny Only (No Human Review)<br>No PENDING_REVIEW Safety Net<br>Approves Active Lung Inflammation on PT-707"]
        OffTopic["6. Zero Scope Guardrails<br>Answers Off-Topic Prompts (Diabetes and Weather)"]
    end

    Patient -->|Raw Unsanitized Notes| Monolith
    Monolith -->|Critical Violations| AuditAlert["CISO Stop-Work Order & Regulatory Penalties:<br>HIPAA Privacy Violations: $1.9M+ Penalty Cap<br>GINA Genetic Discrimination: $300k Damage Cap<br>Total Initial Statutory Exposure: $2,200,000"]
```

---

### Diagram 2: Your Target 5-Agent System (Hardened Architecture)

Notice how the perimeter interceptor scrubs privacy data and quarantines family DNA before invoking the mesh. The coordinator delegates to 3 specialized domain reviewers powered by FastMCP calculator tools. Finally, the decision maker enforces a strict two-gate sequence: **Gate 1: Human Review Check (`PENDING_REVIEW`) FIRST**, followed by **Gate 2: Approve/Deny Check SECOND**:

```mermaid
flowchart TD
    subgraph Perimeter["Perimeter Security Interceptor (Task 1)"]
        RawIntake["Raw Patient Notes"] --> SafeHarbor["HIPAA Patient Privacy Sanitizer<br>Scrubs SSN, MRN, Name, Street Address<br>Preserves Treatment Durations ('30 days')"]
        SafeHarbor --> GINAQuarantine["GINA Family DNA Quarantine<br>Vaults Inherited BRCA1/2, MLH1, PALB2<br>Forwards Tumor Mutations: EGFR, KRAS, BRAF"]
        GINAQuarantine --> Envelope["ClinicalIntakeEnvelope<br>(Clean Pydantic Data Contract)"]
    end

    subgraph CoordinatorMesh["1. Oncology Trial Coordinator (Task 4 and 5)"]
        Envelope --> Coordinator["Oncology Trial Coordinator<br>(TrialMatchingSupervisor)<br>Authenticated via OIDC Bearer Token"]
        Coordinator --> ScopeCheck{"Off-Topic Query?<br>(e.g., Weather or Diabetes)"}
        ScopeCheck -->|Yes| Refusal["Audited Refusal Notice<br>(Rejects PT-905 Safely)"]
    end

    subgraph DomainReviewers["Specialized Domain Reviewers (Task 4 and 5)"]
        ScopeCheck -->|Tumor Genetics| GenomicAgent["2. Tumor Genetics Reviewer<br>(GenomicBiomarkerAgent)<br>Validates Tumor Mutations<br>Ignores Quarantined Family DNA"]
        ScopeCheck -->|Medication History| PVAgent["3. Medication Safety Reviewer<br>(PharmacovigilanceAgent)<br>Checks Drug Cooldown Timers<br>Flags Active Side Effects"]
        ScopeCheck -->|Labs and Health Score| CohortAgent["4. Patient Health & Lab Reviewer<br>(ClinicalCohortAgent)<br>Validates Physical Activity Score<br>Checks Kidney Lab Values"]
    end

    subgraph FastMCPTools["FastMCP Deterministic Calculators (Task 2)"]
        PVAgent <--> MCPWashout["FastMCP Medication Cooldown Calculator<br>Calculates Drug Half-Life Timelines<br>Flags Borderline Lung Inflammation"]
        CohortAgent <--> MCPFHIR["FastMCP Kidney Lab Normalizer<br>Converts mg/dL to umol/L<br>Detects Unreadable 'mg%' Units<br>Zero-Safe Physical Activity Parser"]
    end

    subgraph DecisionMaker["5. Final Trial Decision Maker (Task 3)"]
        GenomicAgent --> WorkerReports["Domain Worker Reports<br>(Genomics, Medication, Labs)"]
        PVAgent --> WorkerReports
        CohortAgent --> WorkerReports
        WorkerReports --> Synthesizer["Final Trial Decision Maker<br>(TrialEligibilitySynthesizer)"]
        
        Synthesizer --> Gate1{"GATE 1: Human Review Check FIRST<br>Confidence < 0.85?<br>Unreadable Lab Units ('mg%')?<br>Active Toxicity / Lung Inflammation?"}
        
        Gate1 -->|Flag Tripped| HumanReview["PENDING_REVIEW<br>(human_intervention_required = True)<br>Routes to Human Doctor"]
        Gate1 -->|All Clean| Gate2{"GATE 2: Approve / Deny SECOND<br>Exact Code Rules: all_passed()?<br>Tumor Mutation Match?<br>Drug Cooldown Met?<br>Activity Score <= 2 and Kidney Normal?"}
        
        Gate2 -->|All Pass| Approved["ELIGIBLE<br>(human_intervention_required = False)"]
        Gate2 -->|Objective Fail| Denied["INELIGIBLE<br>(human_intervention_required = False)"]
    end
```

---

## 6. Pre-Built "Lego Blocks" Toolkit (`lego_blocks/`)

**Do not worry about memorizing medical rules!** You do not need to memorize oncology clinical trial protocols, calculate pharmaceutical half-lives, or write complex biochemical formulas from scratch. 

All clinical logic, medical math, regular expressions, and security validation routines are already written and thoroughly tested for you in the [`lego_blocks/`](lego_blocks/) directory. Your job as a Cloud Security Architect is simply to wire these pre-built blocks into the appropriate agent and server files:

| Lego Block Module | File Path | What It Does in Plain English | Assigned Lab Task |
| :--- | :--- | :--- | :--- |
| **Block 1: HIPAA & GINA Rules** | [`lego_blocks/block_1_hipaa_gina_rules.py`](lego_blocks/block_1_hipaa_gina_rules.py) | **Privacy & Family DNA Shield:** Scrubs direct patient identifiers (SSNs, names, MRNs) while preserving treatment durations like `"30 days"`. Isolates inherited family DNA (`BRCA1/2`, `PALB2`) into a cryptographic SHA-256 quarantine vault while keeping tumor mutations (`EGFR`, `KRAS`, `BRAF`) in the active payload. | **Task 1** |
| **Block 2: FastMCP Washout Engine** | [`lego_blocks/block_2_fastmcp_washout.py`](lego_blocks/block_2_fastmcp_washout.py) | **Medication Cooldown Calculator:** Calculates exact clearance days for previous cancer medications (Tagrisso/osimertinib, Keytruda/pembrolizumab, Opdivo/nivolumab) against trial cooldown rules, eliminating AI arithmetic guesswork. | **Task 2** |
| **Block 3: FHIR Lab Normalizer** | [`lego_blocks/block_3_fhir_lab_normalizer.py`](lego_blocks/block_3_fhir_lab_normalizer.py) | **Kidney Lab & Activity Score Normalizer:** Standardizes kidney lab values (`mg/dL` to `umol/L`), flags corrupted legacy units (`1.0 mg%`) for human review, and fixes the Python falsy-zero bug so `ECOG 0` is recognized as fully healthy. | **Task 2** |
| **Block 4: MedDRA Adverse Events** | [`lego_blocks/block_4_meddra_adverse_events.py`](lego_blocks/block_4_meddra_adverse_events.py) | **Medication Side-Effect Classifier:** Maps patient side effects to standardized safety grades (CTCAE) and flags borderline dangers (like Grade 2 lung inflammation) for mandatory human doctor triage. | **Task 2 & Task 3** |
| **Block 5: HITL Synthesizer** | [`lego_blocks/block_5_hitl_synthesizer.py`](lego_blocks/block_5_hitl_synthesizer.py) | **Two-Gate Decision Engine & Human Safety Net:** Evaluates Gate 1 (Human Review check FIRST for low confidence `< 0.85`, unreadable lab units, or active toxicities -> `PENDING_REVIEW`) and Gate 2 (Approve/Deny check SECOND via exact code rules `all_passed()` -> `ELIGIBLE` / `INELIGIBLE`). | **Task 3** |
| **Block 6: OIDC Auth Guard** | [`lego_blocks/block_6_oidc_auth_guard.py`](lego_blocks/block_6_oidc_auth_guard.py) | **Least-Privilege IAM & Token Guard:** Validates cryptographic OIDC bearer tokens, blocks over-permissioned God-mode accounts (`sa-legacy-god-mode`), and enforces strict calling topology across the agent mesh. | **Task 5** |

---

## 7. Your 5 Lab Challenges (100 Points Total)

Work through each challenge sequentially. You can check your progress at any time with the autograder commands, or request progressive hints if you get stuck.

---

### Task 1: Pre-Model Perimeter Interception (HIPAA Safe Harbor & GINA Title II)
- **Points:** 15 points
- **What's Broken:** The monolithic agent lets raw patient names, SSNs, and family genetics flow straight into the AI prompt. Worse, its clumsy street regex redacts clinical timelines like `"30 days"` into `[REDACTED_STREET_ADDRESS] ago`, breaking drug safety checks downstream.
- **Your Goal with AGY:** 
  1. Open [`agents/trial_matching_supervisor/routing_tools.py`](agents/trial_matching_supervisor/routing_tools.py).
  2. Implement `intercept_and_deidentify_intake` by wiring in [`lego_blocks/block_1_hipaa_gina_rules.py`](lego_blocks/block_1_hipaa_gina_rules.py).
  3. Ensure all direct identifiers (SSN, MRN, Name, DOB) are redacted, clinical durations like `"30 days"` remain untouched, and inherited family DNA (`BRCA1/2`, `PALB2`) is segregated into the quarantine field of the [`ClinicalIntakeEnvelope`](app/contracts.py).
- **How to Check Your Score:** `make verify-task-1`
- **Need a Hint?** Run `make hint TASK=1 LEVEL=1` for an architectural nudge, or `make hint TASK=1 LEVEL=2` for a guided prompt checklist.

---

### Task 2: FastMCP Grounding Tools (Medication Cooldown & Lab Normalization)
- **Points:** 20 points
- **What's Broken:** The monolithic agent guesses drug cooldown days using free-text string matching, failing on brand-generic names like Tagrisso vs. osimertinib (`PT-901`). It also falls into Python's `if not ecog_score:` falsy-zero trap (`PT-708`) by rejecting the healthiest patients, and completely ignores corrupted legacy lab units like `1.0 mg%` (`PT-703`, `PT-903`).
- **Your Goal with AGY:**
  1. Open [`mcp_servers/meddra_ontology/server.py`](mcp_servers/meddra_ontology/server.py) and wire in `mcp_calculate_drug_clearance` using [`lego_blocks/block_2_fastmcp_washout.py`](lego_blocks/block_2_fastmcp_washout.py).
  2. Open [`mcp_servers/fhir_lab_normalizer/server.py`](mcp_servers/fhir_lab_normalizer/server.py) and wire in `mcp_normalize_renal_labs` and `mcp_extract_ecog_score` using [`lego_blocks/block_3_fhir_lab_normalizer.py`](lego_blocks/block_3_fhir_lab_normalizer.py).
  3. Ensure `ECOG 0` is safely parsed as fully active (`0`), kidney units are converted to metric (`umol/L`), and legacy `mg%` units trigger a lower confidence score for human triage.
- **How to Check Your Score:** `make verify-task-2`
- **Need a Hint?** Run `make hint TASK=2 LEVEL=1` or `make hint TASK=2 LEVEL=2`.

---

### Task 3: Deterministic Decision Synthesis & Mandatory Human-in-the-Loop Gate
- **Points:** 25 points
- **What's Broken:** The monolithic agent only knows binary `ELIGIBLE` or `INELIGIBLE` verdicts and hardcodes `human_intervention_required = False`. It recklessly approves patient `PT-707` despite active Grade 2 lung inflammation, and wrongly rejects patient `PT-703` whose biopsy confidence was simply borderline.
- **Your Goal with AGY:**
  1. Open [`agents/trial_eligibility_synthesizer/synthesis_tools.py`](agents/trial_eligibility_synthesizer/synthesis_tools.py).
  2. Implement `evaluate_trial_eligibility` using [`lego_blocks/block_5_hitl_synthesizer.py`](lego_blocks/block_5_hitl_synthesizer.py).
  3. Enforce the two-gate evaluation order:
     - **Gate 1 (Human Review Check FIRST):** If confidence `< 0.85`, unreadable lab units exist (`unparseable_labs=True`), or active side effects are flagged (`borderline_safety_flag=True`), return `PENDING_REVIEW` with `human_intervention_required = True`.
     - **Gate 2 (Approve/Deny Check SECOND):** If all Gate 1 checks pass clean, evaluate exact code rules (`all_passed()`). If all criteria pass, return `ELIGIBLE`; if any objective criteria fail, return `INELIGIBLE` (with `human_intervention_required = False`).
- **How to Check Your Score:** `make verify-task-3`
- **Need a Hint?** Run `make hint TASK=3 LEVEL=1` or `make hint TASK=3 LEVEL=2`.

---

### Task 4: Decouple into 5 ADK Sub-Agents with Typed Pydantic Contracts
- **Points:** 20 points
- **What's Broken:** All clinical logic and tools are crammed into a single monolithic prompt, creating an unmaintainable codebase with an unbounded blast radius.
- **Your Goal with AGY:**
  1. Instantiate each of the 5 specialized sub-agents in [`agents/`](agents/) using model `gemini-3.7-flash`:
     - **Oncology Trial Coordinator** ([`agents/trial_matching_supervisor/agent.py`](agents/trial_matching_supervisor/agent.py))
     - **Tumor Genetics Reviewer** ([`agents/genomic_biomarker/biomarker_agent.py`](agents/genomic_biomarker/biomarker_agent.py))
     - **Medication Safety Reviewer** ([`agents/pharmacovigilance/pv_agent.py`](agents/pharmacovigilance/pv_agent.py))
     - **Patient Health & Lab Reviewer** ([`agents/clinical_cohort/cohort_agent.py`](agents/clinical_cohort/cohort_agent.py))
     - **Final Trial Decision Maker** ([`agents/trial_eligibility_synthesizer/synthesizer_agent.py`](agents/trial_eligibility_synthesizer/synthesizer_agent.py))
  2. Bind domain-specific FastMCP and routing tools to each corresponding agent instance.
  3. Verify that all agents communicate using the strongly-typed Pydantic contracts in [`app/contracts.py`](app/contracts.py).
- **How to Check Your Score:** `make verify-task-4`
- **Need a Hint?** Run `make hint TASK=4 LEVEL=1` or `make hint TASK=4 LEVEL=2`.

---

### Task 5: Least Privilege IAM & OIDC Bearer Token Enforcement
- **Points:** 20 points
- **What's Broken:** The system executes under a single God-mode account (`sa-legacy-god-mode`), and when asked off-topic questions about diabetes medication or Boston weather (`PT-905`), it wastes tokens answering them instead of refusing.
- **Your Goal with AGY:**
  1. Open [`agents/trial_matching_supervisor/routing_tools.py`](agents/trial_matching_supervisor/routing_tools.py).
  2. Implement `verify_mesh_caller_authorization` using [`lego_blocks/block_6_oidc_auth_guard.py`](lego_blocks/block_6_oidc_auth_guard.py).
  3. Strictly reject calls from `sa-legacy-god-mode`, validate downscoped OIDC tokens against target audiences (`https://agents.aegis.health/...`), enforce the authorized calling topology, and ensure out-of-scope prompts return audited refusal notices.
- **How to Check Your Score:** `make verify-task-5`
- **Need a Hint?** Run `make hint TASK=5 LEVEL=1` or `make hint TASK=5 LEVEL=2`.

---

## 8. Quick Command Cheat Sheet & Live Cloud Resources (`prod-proj-ge`)

### Make Command Reference

All grading, attacking, testing, and hint commands are wired into the project [`Makefile`](Makefile):

| Command | What It Does |
| :--- | :--- |
| `make scoreboard` | **Display the Interactive CISO Scoreboard:** Shows your autograder score (0-100 pts) and calculates remaining statutory liability ($2.2M down to $0). |
| `make attack-mega-agent` | **Execute 13 CISO Attack Prompts:** Runs adversarial test cases against the live vulnerable Reasoning Engine to reproduce all 6 audit failures. |
| `make verify-task-1` | **Verify Task 1 (15 pts):** Tests HIPAA direct identifier scrubbing and GINA family DNA quarantine. |
| `make verify-task-2` | **Verify Task 2 (20 pts):** Tests FastMCP medication cooldown math, kidney lab normalization, and ECOG 0 falsy-zero fix. |
| `make verify-task-3` | **Verify Task 3 (25 pts):** Tests Gate 1 (Human Review FIRST) and Gate 2 (Approve/Deny SECOND) deterministic decision logic. |
| `make verify-task-4` | **Verify Task 4 (20 pts):** Tests that all 5 ADK sub-agents are properly instantiated with tools and typed contracts. |
| `make verify-task-5` | **Verify Task 5 (20 pts):** Tests rejection of God-mode identities and enforcement of OIDC bearer token audiences. |
| `make verify-all` | **Run Complete Autograder Suite (100 pts):** Executes all 5 checkpoints sequentially. |
| `make hint TASK=X LEVEL=Y` | **Display Progressive Hints:** `LEVEL=1` provides an architectural concept nudge; `LEVEL=2` provides an AGY prompting strategy. |
| `make verify-bonus` | **Verify Fast-Finisher Bonus (+10 pts):** Tests prompt injection and jailbreak defense using Google Cloud Model Armor. |
| `make clean` | **Clean Environment:** Removes temporary Python bytecode and test cache files. |

---

### Live Google Cloud Resources (`prod-proj-ge`, `us-central1`)

Both the vulnerable Mega Agent and the hardened reference multi-agent mesh are deployed and running live in Google Cloud Project `prod-proj-ge`:

#### 1. Live Broken POC Agent (Audit Target)
- **Deployment Platform:** Vertex AI Agent Runtime (Reasoning Engine)
- **Resource ID:** `projects/679847132899/locations/us-central1/reasoningEngines/2694371110929039360`
- **Display Name:** `TrialShield POC Agent`
- **Underlying Model:** `gemini-3.7-flash`
- **Gemini Enterprise Registered Agent:**
  - Collection: `default_collection`
  - Engine: `gemini-enterprise-demo_1789999455608`
  - Assistant: `default_assistant`
  - Agent Resource: `projects/679847132899/locations/global/collections/default_collection/engines/gemini-enterprise-demo_1789999455608/assistants/default_assistant/agents/1277172829742580937`
  - Description: `"Legacy v0.1 Monolithic TrialShield POC Agent (CISO Audit Target — Binary Approve/Deny Only)"`

#### 2. Live Hardened 5-Agent Mesh (Reference Architecture)
- **Production Reasoning Engine:** `projects/679847132899/locations/us-central1/reasoningEngines/7204215964345303040`
- **Production Cloud Run Services:**
  - Medication Safety Reviewer: `https://pharmacovigilance-679847132899.us-central1.run.app/a2a/pharmacovigilance`
  - Patient Health & Lab Reviewer: `https://clinical-cohort-679847132899.us-central1.run.app/a2a/clinical-cohort`
- **Side-by-Side Live Testing UI:**
  - Visit the [Gemini Enterprise Console](https://console.cloud.google.com/gen-app-builder/engines) -> Select App `gemini-enterprise-demo_1789999455608` (`aegis-oncology-portal-app`) to compare responses between both systems live!

---

## 9. Red-Team Benchmark & CISO Audit Reports

For comprehensive technical and regulatory breakdowns, consult these audit reports:
- **CISO Regulatory Liability & Vulnerability Audit:** [`CISO_AUDIT_REPORT.md`](CISO_AUDIT_REPORT.md) — Full legal and compliance risk analysis ($1.9M HIPAA + $300K GINA).
- **Red-Team Failure Matrix & Test Cases:** [`POC_AGENT_FAILURE_REPORT.md`](POC_AGENT_FAILURE_REPORT.md) — Case-by-case breakdown of all 13 patient test runs (`PT-701` to `PT-905`).
- **Benchmark Execution Script:** [`scripts/benchmark_poc_mega_agent.py`](scripts/benchmark_poc_mega_agent.py) (`make attack-mega-agent`)
- **Raw Benchmark Results (JSON):** [`eval/poc_benchmark_results.json`](eval/poc_benchmark_results.json)

---

## 10. Fast-Finisher Bonus Challenge: Google Cloud Model Armor (+10 Extra Credit Points)

Finished all 5 core challenges early? Earn 10 extra credit points by adding an adversarial prompt shield:
- **The Challenge:** Protect the clinical intake boundary from direct prompt injection, system prompt extraction, and DAN-style jailbreak persona evasion attacks using Google Cloud Model Armor (`sanitizeUserPrompt`) with an offline deterministic fallback.
- **Verification Script:** [`scripts/verify_bonus_model_armor.py`](scripts/verify_bonus_model_armor.py) (`make verify-bonus`)
- **Scoring Invariants:**
  - `[2/2 pts]` Clean clinical intake notes pass unhindered without false alarms.
  - `[3/3 pts]` Direct prompt injections are intercepted and safely quarantined.
  - `[2/2 pts]` DAN persona adoption and jailbreak evasion attempts are blocked.
  - `[3/3 pts]` Deterministic offline fallback maintains complete protection even without cloud network access.
