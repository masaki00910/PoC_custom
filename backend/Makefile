# GCP / Cloud Run 設定
GCP_PROJECT       ?= poc-custom
GCP_REGION        ?= asia-northeast1
AR_REPO           ?= error-recovery-backend
SERVICE_NAME      ?= error-recovery-backend
IMAGE_TAG         ?= latest
IMAGE_URI         := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(AR_REPO)/$(SERVICE_NAME):$(IMAGE_TAG)

.PHONY: help setup dev test lint format build run clean \
        ar-create gcb-deploy run-deploy deploy

help:
	@echo "Targets:"
	@echo "  setup        : ローカル開発環境セットアップ (uv sync)"
	@echo "  dev          : ローカルで FastAPI 起動 (uvicorn --reload)"
	@echo "  test         : pytest 実行"
	@echo "  lint         : ruff check + mypy"
	@echo "  format       : ruff format"
	@echo "  build        : Podman でコンテナビルド"
	@echo "  run          : ビルドしたコンテナをローカル起動 (port 8080)"
	@echo ""
	@echo "GCP デプロイ (ユーザー実行用):"
	@echo "  ar-create    : Artifact Registry リポジトリ作成 (初回 1 回のみ)"
	@echo "  gcb-deploy   : Cloud Build でビルド + push"
	@echo "  run-deploy   : Cloud Run へデプロイ"
	@echo "  deploy       : gcb-deploy + run-deploy"

setup:
	uv sync --extra dev

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run mypy app

format:
	uv run ruff format .

build:
	podman build -t $(SERVICE_NAME):$(IMAGE_TAG) -f Containerfile .

run:
	podman run --rm -p 8080:8080 -e AI__PROVIDER=fake -e APP_ENV=local $(SERVICE_NAME):$(IMAGE_TAG)

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache __pycache__ *.egg-info dist build

# === GCP デプロイ用 (ユーザーが Cloud Shell 等で実行) ===

ar-create:
	gcloud artifacts repositories create $(AR_REPO) \
		--repository-format=docker \
		--location=$(GCP_REGION) \
		--description="Insurance check backend container images" \
		--project=$(GCP_PROJECT)

gcb-deploy:
	gcloud builds submit \
		--config=cloudbuild.yaml \
		--substitutions=_REGION=$(GCP_REGION),_REPO=$(AR_REPO),_IMAGE=$(SERVICE_NAME),_TAG=$(IMAGE_TAG) \
		--project=$(GCP_PROJECT)

run-deploy:
	gcloud run deploy $(SERVICE_NAME) \
		--image=$(IMAGE_URI) \
		--region=$(GCP_REGION) \
		--project=$(GCP_PROJECT) \
		--platform=managed \
		--allow-unauthenticated \
		--set-env-vars=APP_ENV=dev,AI__PROVIDER=fake,LOG_LEVEL=INFO \
		--cpu=1 --memory=512Mi --min-instances=0 --max-instances=3

deploy: gcb-deploy run-deploy
