# Convenience commands for local dev

.PHONY: help init-db pipelines app staging staging-quick staging-full staging-validate docker-test docker-build docker-stop docker-clean gcp-setup gcp-deploy workstation-check diagnose audit git-doctor git-now

help:
	@echo "Targets:"
	@echo "  init-db             Apply sql/schema.sql to DATABASE_URL (requires psql)"
	@echo "  pipelines           Run full pipeline chain (run_all.py)"
	@echo "  app                 Launch Streamlit app"
	@echo "  staging             Create instant staging environment (standard 90 days)"
	@echo "  staging-quick       Create quick staging environment (30 days)"
	@echo "  staging-full        Create full staging environment (365 days)"
	@echo "  staging-validate    Validate existing staging environment"
	@echo "  docker-test         🐳 Launch complete system with Docker (instant local test)"
	@echo "  docker-build        🐳 Build Docker image only"
	@echo "  docker-stop         🐳 Stop Docker containers"
	@echo "  docker-clean        🐳 Clean up Docker containers and volumes"
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

staging:
	@[ -n "$$DATABASE_URL" ] || (echo "Set DATABASE_URL env var" && exit 1)
	@echo "🏗️  Creating instant staging environment (standard 90-day setup)..."
	python scripts/instant_staging.py --mode standard
	@echo "✅ Staging environment ready! Run 'make app' to launch dashboard."

staging-quick:
	@[ -n "$$DATABASE_URL" ] || (echo "Set DATABASE_URL env var" && exit 1)
	@echo "⚡ Creating quick staging environment (30-day setup)..."
	python scripts/instant_staging.py --mode quick
	@echo "✅ Quick staging ready! Run 'make app' to launch dashboard."

staging-full:
	@[ -n "$$DATABASE_URL" ] || (echo "Set DATABASE_URL env var" && exit 1)
	@echo "🌟 Creating full staging environment (365-day setup)..."
	python scripts/instant_staging.py --mode full
	@echo "✅ Full staging ready! Run 'make app' to launch dashboard."

staging-validate:
	@[ -n "$$DATABASE_URL" ] || (echo "Set DATABASE_URL env var" && exit 1)
	@echo "🔍 Validating existing staging environment..."
	python scripts/instant_staging.py --validate-only

docker-test:
	@echo "🐳 LAUNCHING CBI-V13 WITH DOCKER (COMPLETE LOCAL TEST)"
	@echo "======================================================="
	@echo "This will:"
	@echo "  ✅ Start PostgreSQL database"
	@echo "  ✅ Build CBI-V13 application"
	@echo "  ✅ Create instant staging data (30 days)"
	@echo "  ✅ Launch dashboard at http://localhost:8501"
	@echo ""
	@echo "🚀 Starting in 3 seconds..."
	@sleep 3
	docker-compose -f docker-compose.local.yml up --build

docker-build:
	@echo "🔨 Building Docker image..."
	docker-compose -f docker-compose.local.yml build

docker-stop:
	@echo "🛑 Stopping Docker containers..."
	docker-compose -f docker-compose.local.yml down

docker-clean:
	@echo "🧹 Cleaning up Docker containers and volumes..."
	docker-compose -f docker-compose.local.yml down -v --remove-orphans
	@echo "✅ Cleanup complete"

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
