# Convenience commands for local dev

.PHONY: help init-db pipelines app gcp-setup gcp-deploy workstation-check diagnose audit git-doctor git-now

help:
	@echo "Targets:"
	@echo "  init-db             Apply sql/schema.sql to DATABASE_URL (requires psql)"
	@echo "  pipelines           Run full pipeline chain (run_all.py)"
	@echo "  app                 Launch Streamlit app"
	@echo "  gcp-setup           Set up Google Cloud infrastructure (Cloud SQL, Artifact Registry, etc.)"
	@echo "  gcp-deploy          Deploy to Google Cloud Run using Cloud Build"
	@echo "  workstation-check   Verify/start Cloud Workstation and print Gateway steps"
	@echo "  diagnose            Run repo/app connection diagnostics"
	@echo "  git-doctor          Diagnose Git 'nothing showing' issues"
	@echo "  git-now             Stage, commit, and push current repo (set GIT_REMOTE if origin missing)"

init-db:
	@[ -n "$$DATABASE_URL" ] || (echo "Set DATABASE_URL env var" && exit 1)
	psql "$$DATABASE_URL" -f sql/schema.sql

pipelines:
	python run_all.py

app:
	streamlit run app/Home.py

gcp-setup:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID env var" && exit 1)
	bash scripts/gcp_setup.sh

gcp-deploy:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID env var" && exit 1)
	gcloud builds submit --config cloudbuild.yaml

workstation-check:
	@[ -n "$$PROJECT_ID" ] || (echo "Set PROJECT_ID, REGION, CLUSTER, CONFIG, WORKSTATION env vars" && exit 1)
	@[ -n "$$REGION" ] || (echo "Set PROJECT_ID, REGION, CLUSTER, CONFIG, WORKSTATION env vars" && exit 1)
	@[ -n "$$CLUSTER" ] || (echo "Set PROJECT_ID, REGION, CLUSTER, CONFIG, WORKSTATION env vars" && exit 1)
	@[ -n "$$CONFIG" ] || (echo "Set PROJECT_ID, REGION, CLUSTER, CONFIG, WORKSTATION env vars" && exit 1)
	@[ -n "$$WORKSTATION" ] || (echo "Set PROJECT_ID, REGION, CLUSTER, CONFIG, WORKSTATION env vars" && exit 1)
	bash scripts/workstation_check.sh

diagnose:
	python scripts/diagnose.py

git-doctor:
	bash scripts/git_doctor.sh

git-now:
	bash scripts/git_now.sh
