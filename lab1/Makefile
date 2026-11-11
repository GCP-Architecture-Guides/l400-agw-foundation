# Makefile for CEPF128-L400: Aegis TrialShield Starter Lab
# Architecture: Deconstruct the Monolithic Mega Agent and Architect a Secure Healthcare Multi-Agent Mesh

.PHONY: help deploy-poc-agent attack-mega-agent verify-task-1 verify-task-2 verify-task-3 verify-task-4 verify-task-5 verify-all scoreboard hint verify-bonus clean

help:
	@echo "Aegis TrialShield Lab Commands:"
	@echo "  make deploy-poc-agent    - Deploy TrialShield POC Agent to Vertex AI Agent Runtime"
	@echo "  make attack-mega-agent   - Execute all 13 CISO red-team prompts against TrialShield POC Agent"
	@echo "  make verify-task-1       - Run Autograder Checkpoint 1 (HIPAA/GINA Pre-Model Interceptor, 15 pts)"
	@echo "  make verify-task-2       - Run Autograder Checkpoint 2 (Deterministic Synthesis Engine, 20 pts)"
	@echo "  make verify-task-3       - Run Autograder Checkpoint 3 (FastMCP Server Decomposition, 25 pts)"
	@echo "  make verify-task-4       - Run Autograder Checkpoint 4 (ADK Sub-Agent Decoupling, 20 pts)"
	@echo "  make verify-task-5       - Run Autograder Checkpoint 5 (Least Privilege & End-to-End Mesh, 20 pts)"
	@echo "  make verify-all          - Run all 5 checkpoints sequentially (Total 100 pts)"
	@echo "  make scoreboard          - Display CISO Red-Team Scoreboard & Statutory Liability Meter"
	@echo "  make hint TASK=<1-5> LEVEL=<1-2> - Display 2-tier progressive hints for lab tasks"
	@echo "  make verify-bonus        - Run Fast-Finisher Bonus Check (Model Armor Prompt Shield, 10 pts)"
	@echo "  make clean               - Clean temporary caches and test artifacts"

deploy-poc-agent:
	@echo "Deploying TrialShield POC Agent to Vertex AI Agent Runtime..."
	agents-cli deploy \
		--deployment-target agent_runtime \
		--service-name "TrialShield POC Agent" \
		--project prod-proj-ge \
		--region us-central1 \
		--agent-identity \
		--env-vars "GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_ENTERPRISE=true" \
		--no-confirm-project

attack-mega-agent:
	@echo "Executing 13 CISO attack prompts against TrialShield POC Agent..."
	uv run python scripts/benchmark_poc_mega_agent.py

verify-task-1:
	@echo "Verifying Task 1: HIPAA Safe Harbor & GINA Title II Interceptor..."
	uv run python scripts/verify_task_1.py

verify-task-2:
	@echo "Verifying Task 2: Deterministic Synthesis Engine & HITL Guardrails..."
	uv run python scripts/verify_task_2.py

verify-task-3:
	@echo "Verifying Task 3: FastMCP MedDRA & FHIR Server Decomposition..."
	uv run python scripts/verify_task_3.py

verify-task-4:
	@echo "Verifying Task 4: ADK Sub-Agent Decoupling & Least Privilege..."
	uv run python scripts/verify_task_4.py

verify-task-5:
	@echo "Verifying Task 5: End-to-End Multi-Agent Mesh & Audit Trail..."
	uv run python scripts/verify_task_5.py

verify-all:
	-@uv run python scripts/verify_task_1.py
	-@uv run python scripts/verify_task_2.py
	-@uv run python scripts/verify_task_3.py
	-@uv run python scripts/verify_task_4.py
	-@uv run python scripts/verify_task_5.py
	@echo "\n======================================================================"
	@echo "🏁 Checkpoint Run Complete: Review any 0/X scores and TODOs above."
	@echo "======================================================================"

scoreboard:
	uv run python scripts/ciso_scoreboard.py

hint:
	uv run python scripts/lab_hints.py --task $(or $(TASK),1) --level $(or $(LEVEL),1)

verify-bonus:
	@echo "Verifying Fast-Finisher Bonus: Google Cloud Model Armor Integration..."
	uv run python scripts/verify_bonus_model_armor.py

clean:
	rm -rf .pytest_cache __pycache__ */__pycache__ */*/__pycache__
