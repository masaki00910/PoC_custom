# Insurance Check Backend (PoC)

保険申込書一次チェックシステムのバックエンド (Python / FastAPI)。

このリポジトリの設計方針は `CLAUDE.md` を参照してください。

## 現状の実装範囲 (T-001 完了時点)

- `/healthz`
- `POST /v1/checks/address-master-match` — F-05-008 住所マスタ突合の最小実装
  - AI: `FakeAIClient` (固定応答)
  - DB: `InMemoryAddressMasterRepository` (CSV 数件をハードコード)
  - 認証なし
- 単体テスト 5 + API 統合テスト 3

未実装（次タスク以降）:
- 実 AI クライアント (`BedrockProxyClient` → 将来 `VertexAIClient`)
- 郵政住所マスタ (KEN_ALL) フォールバック
- 他の住所ルール (F-05-005 / F-05-006) と他カテゴリのルール
- Cloud SQL 接続
- Entra ID JWT 検証

詳細: `../.claude/TASKS.md`

---

## ローカル開発

### 前提
- Python 3.12 以上 (3.14 で動作確認済)
- Podman (コンテナビルド時のみ)

### セットアップ

```bash
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"   # Windows
# .venv/bin/python -m pip install -e ".[dev]"         # Mac/Linux
```

uv を使う場合は `make setup` でも可。

### 起動

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8080
```

別ターミナルで動作確認:

```bash
curl http://127.0.0.1:8080/healthz

curl -X POST http://127.0.0.1:8080/v1/checks/address-master-match \
  -H 'Content-Type: application/json' \
  -d '{
    "application_id": "11111111-2222-3333-4444-555555555555",
    "address_kana": "トウキョウトシブヤクジングウマエ1チョウメ",
    "attribute": "新",
    "document_item": "申込書住所カナ"
  }'
```

期待レスポンス:

```json
{
  "rule_name": "address_master_match",
  "rule_version": "1.0.0",
  "status": "OK",
  "document_item": "申込書住所カナ",
  "document_recovery_value": "150-0001",
  "recovery_reason": "[新住所(〒)]　AFLAC住所マスタより回復",
  "recovery_process": "エラー回復(AFLAC住所マスタ突合)よりロジック判定",
  "details": {...},
  "correlation_id": "..."
}
```

### テスト

```bash
.venv/Scripts/python.exe -m pytest
```

### Fake AI が認識する住所カナサンプル

| 住所カナ (部分一致) | 結果 | 回復値 |
|---|---|---|
| `ジングウマエ` | OK | 150-0001 |
| `カブキチョウ` | OK | 160-0021 |
| `ミナミアオヤマ` | OK | 107-0062 (字丁2件あるが郵便番号一意) |
| `マルノウチ` | NG | 郵便番号複数 (100-0005 / 100-6390) |
| 上記以外 | NG | AI 分割不可 |

---

## GCP Cloud Run へのデプロイ

> **デプロイ実行はユーザー側で行います。** 本セクションのコマンドを Cloud Shell で順に実行してください。
>
> 前提:
> - GCP プロジェクト: `poc-custom`
> - リージョン: `asia-northeast1`
> - 必要な API は既に有効化済 (Cloud Run / Artifact Registry / Cloud Build)

### 1. Artifact Registry リポジトリ作成 (初回のみ)

```bash
gcloud artifacts repositories create error-recovery-backend \
  --repository-format=docker \
  --location=asia-northeast1 \
  --description="Insurance check backend container images" \
  --project=poc-custom
```

または `make ar-create`。

### 2. Cloud Build でイメージビルド & push

backend ディレクトリで:

```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION=asia-northeast1,_REPO=error-recovery-backend,_IMAGE=error-recovery-backend,_TAG=latest \
  --project=poc-custom
```

または `make gcb-deploy`。

> `cloudbuild.yaml` で `-f Containerfile` を明示しているため、Dockerfile を作る必要はありません
> （CLAUDE.md §10 の Containerfile 命名規約に準拠）。

### 3. Cloud Run へデプロイ

```bash
gcloud run deploy error-recovery-backend \
  --image=asia-northeast1-docker.pkg.dev/poc-custom/error-recovery-backend/error-recovery-backend:latest \
  --region=asia-northeast1 \
  --project=poc-custom \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars=APP_ENV=dev,AI_CLIENT=fake,LOG_LEVEL=INFO \
  --cpu=1 --memory=512Mi --min-instances=0 --max-instances=3
```

または `make run-deploy`。

`--allow-unauthenticated` は最小動作確認のため (T-008 で Entra ID JWT 検証を入れたら外す)。

### 4. 動作確認

デプロイコマンドの出力に表示される Service URL (例: `https://error-recovery-backend-xxxxx-an.a.run.app`) を環境変数に入れて:

```bash
SERVICE_URL=https://error-recovery-backend-xxxxx-an.a.run.app

curl ${SERVICE_URL}/healthz

curl -X POST ${SERVICE_URL}/v1/checks/address-master-match \
  -H 'Content-Type: application/json' \
  -d '{
    "application_id": "11111111-2222-3333-4444-555555555555",
    "address_kana": "トウキョウトシブヤクジングウマエ1チョウメ"
  }'
```

期待: ローカルと同じレスポンスが返る。

---

## ディレクトリ構造

```
backend/
├── app/
│   ├── api/                    # FastAPI ルーティング・DTO・DI
│   │   ├── deps.py
│   │   └── v1/
│   ├── application/            # ユースケース (T-005 以降で本格実装)
│   ├── domain/                 # 業務ロジック (外部依存なし)
│   │   ├── entities/
│   │   ├── interfaces/
│   │   └── rules/
│   │       └── address/
│   │           └── address_master_match.py    # F-05-008
│   ├── infrastructure/         # 差し替え対象実装
│   │   ├── ai/
│   │   │   ├── fake_client.py
│   │   │   └── prompts/
│   │   └── db/
│   │       └── repositories/
│   ├── config.py
│   └── main.py
├── tests/
│   ├── unit/rules/address/
│   └── integration/
├── pyproject.toml
├── Containerfile
├── Makefile
├── .env.example
└── CLAUDE.md
```

---

## トラブルシュート

### Pydantic バリデーションエラー
`application_id` は UUID 形式必須。任意の UUID で OK (例: `11111111-2222-3333-4444-555555555555`)。

### Cloud Build で `service.cloudbuild.googleapis.com` の有効化エラー
Cloud Build API が未有効ならコンソール or `gcloud services enable cloudbuild.googleapis.com` で有効化。
本プロジェクトでは既に有効化済 (確認済)。
