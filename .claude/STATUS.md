# プロジェクト現状サマリ

最終更新: 2026-04-27 (バックエンド最小実装セッション完了)

## 概要
保険申込書の一次チェックを AI で自動化するシステムの PoC。Power Automate で動いている既存のエラー回復フローを Python (FastAPI) に移行し、Cloud Run 上で動作させる。3 リポジトリ構成 (frontend / backend / database)。

## 現在のフェーズ
- **バックエンド初回実装完了**（F-05-008 住所マスタ突合の最小フローをローカル動作確認済）
- **次は GCP Cloud Run へのデプロイ**（ユーザーが Cloud Shell で実行）
- frontend は LLM クライアント抽象まで実装済（モック中心）
- database はスキーマ・マスタ CSV 定義済（Cloud SQL 立ち上げはまだ）

## いま着手中のタスク
- なし。次セッション開始時にユーザーの判断で T-002 (Bedrock 配線) または T-003+ (郵政マスタ・他ルール) に進む。

## 直近完了したタスク
- **T-001** 住所フロー最小移行（F-05-008 単体）— **2026-04-27 完了**
  - backend スケルトン・ドメイン層・F-05-008 ルール・Fake/InMemory・API・テスト・デプロイ手順を整備
  - 単体 5 + API 統合 3 = 8 テスト pass (Python 3.14 で確認)
  - Cloud Run デプロイ用 `cloudbuild.yaml` + Makefile ターゲット用意済

## 次にやること

### A. ユーザー側で実行（このセッションのアウトプット動作確認）
1. Artifact Registry リポジトリ作成: `cd backend && make ar-create`
2. Cloud Build でビルド & push: `make gcb-deploy`
3. Cloud Run デプロイ: `make run-deploy`
4. 払い出された Service URL に curl: `curl ${URL}/healthz` および `POST ${URL}/v1/checks/address-master-match`
5. 期待: ローカルテストと同じレスポンス (詳細は `backend/README.md`)

### B. 次セッションで実装する候補（優先度順）
- **T-002** Bedrock プロキシ実クライアント (`BedrockProxyClient` 実装 + AI_CLIENT 切替)
  - 前提: ユーザーから Bedrock プロキシのレスポンス JSON 形式を共有
- **T-003** F-05-008 郵政住所マスタフォールバック (KEN_ALL 突合 + 全角→半角カナ変換)
- **T-004** F-05-006 住所漢字・カナ突合ルール
- **T-005** F-05-005 住所回復処理 (オーケストレータ)

## 重要な前提・制約・既知の問題

### GCP 環境 (`poc-custom` プロジェクト)
- 有効な API: Cloud Run / Artifact Registry / Cloud Build / Secret Manager / Logging / Monitoring 等
- **未有効**: Vertex AI / Cloud SQL Admin / API Gateway
- リージョン: `asia-northeast1`
- Artifact Registry リポジトリ: 未作成（`make ar-create` で初回作成）

### AI クライアント
- 暫定: AWS API Gateway 経由の Bedrock プロキシ `https://6mlsx5sseg.execute-api.ap-northeast-1.amazonaws.com/dev/chat`
- リクエスト形式: `{"message": "...", "model": "global.anthropic.claude-sonnet-4-6"}`、認証なし、`Content-Type: application/json` のみ
- レスポンス形式は **未確認** (T-002 着手時にユーザーから共有してもらう)
- 現在のデプロイは `AI_CLIENT=fake` でビルド・実行
- 将来は Vertex AI に移行予定

### 認証
- 現在 `--allow-unauthenticated` で公開 (動作確認のため)
- T-008 で Entra ID JWT 検証を導入したら外す

### デプロイ実行
- ユーザーが Cloud Shell 等で `gcloud` コマンドを実行
- Claude 側で `gcloud` / 外部 API への curl は実行しない（メモリ参照: feedback_external_api_probing.md）

### 規約
- backend は `backend/CLAUDE.md` に従う（クリーンアーキテクチャ、Podman、Python 3.12+、テスト必須）
- 個人情報をリポジトリ・ログに出さない
- スキーマ変更は `database/` リポジトリの責務（backend からマイグレーション実行禁止）
