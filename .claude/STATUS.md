# プロジェクト現状サマリ

最終更新: 2026-04-27 (T-001 Cloud Run デプロイ動作確認完了)

## 概要
保険申込書の一次チェックを AI で自動化するシステムの PoC。Power Automate で動いている既存のエラー回復フローを Python (FastAPI) に移行し、Cloud Run 上で動作させる。3 リポジトリ構成 (frontend / backend / database)。

## 現在のフェーズ
- **バックエンド最小フロー (F-05-008) が Cloud Run 上で稼働中** ✅
- 動作確認済: `/health` + `POST /v1/checks/address-master-match` (OK 2 件 / NG 2 件のシナリオ全て期待通り)
- frontend は LLM クライアント抽象まで実装済（モック中心）
- database はスキーマ・マスタ CSV 定義済（Cloud SQL 立ち上げはまだ）

## いま着手中のタスク
- なし。次セッション開始時にユーザーの判断で T-002 (Bedrock 配線) または T-003+ (郵政マスタ・他ルール) に進む。

## 直近完了したタスク
- **T-001** 住所フロー最小移行（F-05-008 単体）— **2026-04-27 完了 (Cloud Run 稼働確認まで)**
  - 実装: backend スケルトン・ドメイン層・F-05-008 ルール・Fake/InMemory・API・テスト・デプロイ手順
  - テスト: 単体 5 + API 統合 3 = 8 件 pass
  - デプロイ: GCP `poc-custom` プロジェクト / Cloud Run `error-recovery-backend` (asia-northeast1) / `--allow-unauthenticated`
  - Service URL: `https://error-recovery-backend-awvvdiqaua-an.a.run.app` (旧形式), `https://error-recovery-backend-691038404010.asia-northeast1.run.app` (新形式は 404、旧形式が動作)
  - 途中で `/healthz` が Cloud Run / Knative の queue-proxy 予約パスで届かない問題を発見、`/health` にリネームして対応 (`memory/project_cloud_run_reserved_paths.md` に記録済)

## 次にやること（次セッションで実装する候補）

優先度順:

- **T-002** Bedrock プロキシ実クライアント (`BedrockProxyClient` 実装 + AI_CLIENT 切替)
  - 前提: ユーザーから Bedrock プロキシのレスポンス JSON 形式を共有
- **T-003** F-05-008 郵政住所マスタフォールバック (KEN_ALL 突合 + 全角→半角カナ変換)
- **T-004** F-05-006 住所漢字・カナ突合ルール
- **T-005** F-05-005 住所回復処理 (オーケストレータ)
- **T-007** Cloud SQL 接続 + ORM モデル + SqlAlchemyAddressMasterRepository
- **T-008** Entra ID JWT 検証ミドルウェア

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
