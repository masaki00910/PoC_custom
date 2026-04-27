# 作業ログ

## 2026-04-27 (バックエンド最小実装セッション)

### セッション目的
バックエンドを試しに移行して動作チェック。住所フロー最小（F-05-008 単体）を Cloud Run まで届ける。

### この時点までに合意した方針
- 移行対象は **F-05-008 住所マスタ突合 1 本のみ**（住所3ルール全体ではない）
- AI は **`FakeAIClient` のみ** 配線、実 AI は次タスク
- 郵政住所マスタフォールバック・F-05-007/009 連携・ATLAS 登録データ照会・全角→半角カナ変換は **次タスクに先送り**
- 認証なしで Cloud Run に公開し curl で動作確認
- デプロイ実行はユーザーが行う（Claude は `gcloud` を叩かない）

### 環境情報（記録）
- GCP プロジェクト: `poc-custom`
- リージョン: `asia-northeast1`
- 有効 API: Cloud Run / Artifact Registry / Cloud Build / Secret Manager / Logging / Monitoring 等
- 未有効: Vertex AI / Cloud SQL Admin / API Gateway
- AI 暫定: `https://6mlsx5sseg.execute-api.ap-northeast-1.amazonaws.com/dev/chat` (POST, JSON, 認証なし)
- AI リクエスト形式: `{"message": "...", "model": "global.anthropic.claude-sonnet-4-6"}`

### 元フロー読解メモ（F-05-008）
- トリガー: `text` / `text_1` / `text_2` / `text_3` / `text_4` / `text_5` の 6 文字列入力（中身は stringify された JSON）
  - `text_4` = 補完後の住所カナ（重要）
- 主要ロジック:
  1. AI プロンプト「住所カナ分割」で 都道府県カナ/市区町村カナ/大字カナ/字丁カナ に 4 分割
  2. `ca_aflac_address_masters` を `市区町村名カナ` AND `大字・通称名カナ` で絞り込み
  3. ヒット件数 0 → 郵政住所マスタ (KEN_ALL) フォールバック
  4. 郵便番号が 1 種類なら OK (回復値として返す)、複数ならビジネスエラー

### 変更内容
- `.claude/STATUS.md` `.claude/TASKS.md` `.claude/JOURNAL.md` 新規作成
- backend に最小実装を追加 (38 ソースファイル、テスト含む)
  - 骨格: `pyproject.toml` / `Containerfile` / `cloudbuild.yaml` / `Makefile` / `.env.example` / `.gitignore` / `.containerignore` / `README.md`
  - エントリ: `app/main.py` / `app/config.py`
  - ドメイン層: `app/domain/{exceptions,rules/base,rules/address/address_master_match,entities/{application,check_context,check_result,master_data},interfaces/{ai_client,address_master_repository}}.py`
  - インフラ: `app/infrastructure/ai/{fake_client.py,prompts/address_kana_split_v1.txt}`、`app/infrastructure/db/repositories/in_memory_address_master.py`
  - API: `app/api/{deps,v1/{checks,router,schemas}}.py`
  - テスト: 単体 5 (`tests/unit/rules/address/test_address_master_match.py`) + 統合 3 (`tests/integration/test_api_address_master_match.py`)、すべて pass

### 動作確認結果
- Python 3.14 + venv + pip install で `pytest -q` → 8 passed in 0.49s
- Cloud Run へのデプロイは未実施（ユーザーが実行する）

### 次セッションへの申し送り
- 上記の `make ar-create` → `make gcb-deploy` → `make run-deploy` をユーザーが Cloud Shell で実行 → 払い出された Service URL に curl で疎通確認
- 動作確認の応答が期待値（README の「期待レスポンス」と一致）であれば T-001 デプロイ成功
- 失敗時のログ確認は: Cloud Run コンソール → Logs、または `gcloud run services logs read error-recovery-backend --region=asia-northeast1`
- 次タスク候補は STATUS.md の「次にやること B」を参照（推奨は T-002 = Bedrock プロキシ実クライアント実装）

## 2026-04-27 (デプロイ後の `/healthz` 404 問題対応)

### 事象
- Cloud Shell から `make ar-create` → `make gcb-deploy` → `make run-deploy` を実行、Service URL 払い出し成功
- 公開 URL (`https://error-recovery-backend-691038404010.asia-northeast1.run.app` / `https://error-recovery-backend-awvvdiqaua-an.a.run.app`) どちらでも `GET /healthz` が Google エッジの **404 HTML** を返す
- コンテナ自身は健全（uvicorn 起動、ログにスタートアップ完了表示）
- ingress=all、IAM に `allUsers: roles/run.invoker` 設定済（公開アクセス可）

### 切り分け
1. `gcloud run services proxy` で複数パスをテスト:
   - `GET /healthz` → 404 HTML、`Server` ヘッダ無し ❌（コンテナに届いていない）
   - `GET /openapi.json` → 200 JSON、`Server: Google Frontend` ✅
   - `GET /docs` → 200 HTML、`Server: Google Frontend` ✅
   - `GET /` → 404 JSON (FastAPI の)、`Server: Google Frontend` ✅
   - `POST /v1/checks/address-master-match` → FastAPI のバリデーションエラー ✅
2. `/healthz` だけがエッジで横取り → **Cloud Run / Knative の queue-proxy が `/healthz` を予約**しているため

### 対応
- `app/main.py` のヘルスチェックパスを `/healthz` → `/health` にリネーム
- 関連修正: `tests/integration/test_api_address_master_match.py` のテスト、README の curl サンプル
- `pytest` 全 8 件 pass で再確認
- メモリに `project_cloud_run_reserved_paths.md` を追加（次回以降の Cloud Run 案件で同事象を即特定するため）

### ユーザ次アクション
- ローカルで commit & push → Cloud Shell で `git pull` → `make gcb-deploy && make run-deploy`
- 再デプロイ後は `${SERVICE_URL}/health` で動作確認

## 2026-04-27 (T-001 Cloud Run 動作確認 完了)

### 結果
全 5 ケースが期待通りに動作:

| ケース | エンドポイント | 入力 | 結果 |
|---|---|---|---|
| 0 | GET /health | — | `{"status":"ok","env":"dev"}` ✅ |
| 1 | POST address-master-match | ジングウマエ | OK / 150-0001 ✅ |
| 2 | POST address-master-match | ミナミアオヤマ | OK / 107-0062 (字丁複数→重複削除→1件) ✅ |
| 3 | POST address-master-match | マルノウチ | NG (候補件数=2 で自動回復不可) ✅ |
| 4 | POST address-master-match | 未知の住所 | NG (住所カナ分割で特定できず) ✅ |

`recovery_reason` の文言は Power Automate 元フロー (`[新住所(〒)]　AFLAC住所マスタより回復` 等) と整合。
`details` に AI プロンプト名・バージョン・生レスポンス・ヒットしたカナを記録、CLAUDE.md §7 (AI 説明可能性) の要件を満たす。

### 副次的な学び
- Cloud Shell の curl コマンドで JSON ボディを `-d` 渡しすると、ターミナル幅で行折り返しされたコマンドをコピペした際に**改行が JSON 文字列内に混入**して `json_invalid` エラーになる。
- 対処: 短い変数定義 + 配列ループで構成すると折り返し耐性がある。あるいはヒアドキュメント or ファイル経由 (`--data @file.json`)。

### T-001 ステータス
**完全完了**。Cloud Run でのスタック起動 → API 動作 → 業務ロジック (突合 OK/NG) すべて期待通り。
次タスク (T-002 以降) は STATUS.md 参照。

### 設計上の判断ログ
- **`AIClient` 抽象**: プロンプト名 + 入力 dict → 構造化 dict の汎用 API として定義 (元 PA の AI Builder Custom Prompt と同じ抽象度)。Bedrock プロキシ・Vertex AI の両方に差し込めるよう汎用化
- **`AddressMasterRepository` 抽象**: 検索メソッドはユースケース駆動で命名 (`find_aflac_by_municipality_and_oaza_kana`)。汎用 CRUD ではなく業務クエリ単位で抽象化することで、SqlAlchemy 実装時に最適化しやすくする
- **`details` フィールド**: `CheckResult.details` に AI プロンプト名・バージョン・生レスポンスを格納し、CLAUDE.md §7 (AI 説明可能性) に対応
- **`cloudbuild.yaml`**: `gcloud builds submit --tag` は Dockerfile 固定のため、CLAUDE.md §10 の Containerfile 命名規約と Cloud Build を両立させる目的で追加
- **`@lru_cache` for DI**: Settings/AIClient/Repository/Rule は全アプリ寿命でシングルトン化。Pydantic Settings の env 読み込みも 1 回のみ
