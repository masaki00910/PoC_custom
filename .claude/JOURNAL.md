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

## 2026-04-28 (T-003 KEN_ALL フォールバック実装)

### セッション目的
住所まわりの一次チェックロジックの追加移行。T-003 → T-004 → T-005 の順に進める方針合意 → T-003 のみ完了したところで一旦停止。

### この時点までに合意した方針
- 元フローは `sample_modernflows/` 配下の **【エラー回復】(live, StateCode=Activated)** 版を正とする (【工藤修正中】=draft は参照しない)
- T-001 と同じく「F-05-008 の延長」として T-003 を進め、Aflac ヒット 0 件分岐を埋める
- F-05-007 文字数超過チェックの子フロー呼び出しは T-003 のスコープ外 (T-006 で別実装)

### 元フロー読解メモ (F-05-008 KEN_ALL フォールバック分岐)
- Aflac マスタ 0 件のとき:
  1. AI 「住所漢字分割」(prompt4) で `text_3` (契約申込書) → 都道府県名/市区町村名/町域名 に 3 分割
  2. `ca_japan_post_address_masters` を `ca_prefecture_name` AND `ca_municipality_name` AND `ca_town_name` の完全一致で絞り込み
  3. ヒット 0 件 → NG (`recovery_reason: "[XX住所(該当〒番号なし)]問合せ"`)
  4. ヒット 1+ 件:
     - 郵便番号で重複削除 → 1 種類なら OK + KEN_ALL マスタ側のカナ列を連結 → 全角→半角カナ変換 (PA フローに hardcoded された 78 文字マッピング辞書を忠実に使用)
     - 複数 → ビジネスエラー (PA は空 Scope。Python では NG として明示)
- recovery_reason (KEN_ALL OK): `[XX住所(〒・カナ)]　郵便局住所マスタにて強制回復※「字・大字」有の場合は、除外の上、AFLAC住所マスタで要検索`
- recovery_process (KEN_ALL): `エラー回復(郵便局住所マスタ突合)よりロジック判定`

### 変更内容 (backend)
- 新規:
  - `app/domain/rules/address/kana_converter.py` (78 文字マッピング辞書 + `to_halfwidth_kana()`)
  - `app/infrastructure/ai/prompts/address_kanji_split_v1.txt`
  - `tests/unit/rules/address/test_kana_converter.py` (6 件)
- 変更:
  - `app/domain/entities/master_data.py` - `JapanPostAddressMasterRecord` 追加
  - `app/domain/interfaces/address_master_repository.py` - `find_japan_post_by_prefecture_municipality_town` 抽象メソッド追加
  - `app/domain/entities/application.py` - `address_kanji: str = ""` 追加 (text_3 相当、後方互換)
  - `app/domain/rules/address/address_master_match.py` - rule_version 1.0.0 → 1.1.0、`_fallback_japan_post()` メソッド追加、Aflac 0 件 → KEN_ALL フォールバック合流ロジック
  - `app/infrastructure/ai/fake_client.py` - `address_kanji_split` プロンプト対応 (汎用化されたフィクスチャ実装)
  - `app/infrastructure/db/repositories/in_memory_address_master.py` - KEN_ALL フィクスチャ追加 (横浜市青葉区美しが丘・港区南青山) + メソッド実装
  - `app/api/v1/schemas.py` / `app/api/v1/checks.py` - リクエスト DTO に `address_kanji` 追加
  - `tests/integration/test_api_address_master_match.py` - フォールバック OK / NG ケース追加
  - `tests/unit/rules/address/test_address_master_match.py` - フォールバック 3 ケース追加 + 既存 1 ケースの期待値更新 (空カナ分割時は KEN_ALL に合流するためメッセージ変更)

### 設計上の判断
- **空カナ分割の扱い**: 当初は「カナ分割で必須フィールドが空 → 即 NG」として実装したが、PA フローは Aflac ヒット 0 件 → KEN_ALL に合流する流れだったので、空カナ分割でも Aflac をスキップして KEN_ALL に進む形に修正。これで「漢字住所のみ取得できる」ケースも自動回復可能になる
- **半角カナ変換**: PA フローの MappingList Compose に hardcoded された 78 文字マッピングを Python に忠実コピー。`unicodedata.normalize` や `jaconv` のような汎用ライブラリは使わず、マスタ値との照合互換性を優先 (ヴ等 PA に無い文字はそのまま保持)
- **ビジネスエラーの扱い**: PA フローでは空 Scope (結果配列に何も追加しない) で正常応答する動作。Python のルール契約は `execute() -> CheckResult` で必ず1つの結果を返す前提のため、NG として「自動回復不可（候補件数=N）」と recovery_reason に明示
- **半角カナの details 格納**: F-05-007 文字数超過チェック (T-006) で使うため `details["address_kana_halfwidth"]` に格納しておく

### 動作確認結果
- `pytest -q` → **19 passed in 0.72s** (単体 14 + 統合 5)
- Cloud Run へのデプロイ・curl 動作確認は **次セッションで実施**

### 次セッションへの申し送り
1. **T-003 を git commit** (10 ファイル変更 + 3 ファイル追加、全テスト pass 状態)
2. ユーザーが Cloud Shell で `make gcb-deploy && make run-deploy` → curl で `address_kanji` を含むペイロードでフォールバック動作確認
3. **T-004 (F-05-006 住所漢字・カナ突合)** に進む
   - F-05-006 JSON は読解開始済み (要点は STATUS.md の T-004 セクション参照)
   - 先に決めること: SharePoint 画像取得 + メイン書類読取り AI をどこまでモックで再現するか (API 入力に `extracted_address_kanji` を直接渡す形が現実的)
4. T-005 (F-05-005 オーケストレータ) は T-004 完了後

## 2026-04-30 (T-003 コミット + T-004 F-05-006 案A 実装)

### セッション目的
1. 前セッションで未コミットだった T-003 を整理してコミット
2. T-004 (F-05-006 住所漢字・カナ突合) を案A で実装

### この時点までに合意した方針
- T-003 を先にコミット (`7a886db`) → その後 T-004 着手
- T-004 は **案A** = SharePoint/OCR (prompt1) は完全スキップし、API 入力で `address_kanji` を直接受け取る
- `Application.address_kanji` (T-003 で追加済み) をそのまま流用 (= prompt1 出力相当)
- `CheckRule.execute()` の単一 `CheckResult` 返却契約を維持。元 PA の document_item1/document_item2 別の複数結果は PoC では `details` に集約し、商用化時に複数返却対応を検討

### 元フロー読解メモ (F-05-006)
- 入力: text(親フロー情報) / text_1(プロンプト) / text_2(属性情報) / text_3(ATLAS登録データ=カナ) / text_4(点検結果テーブル)
- 処理:
  1. メイン書類 (SharePoint base64) → AI prompt1 で住所漢字抽出 (案A ではスキップ)
  2. AI prompt2 で 漢字 vs カナ の整合チェック (`check_result` OK/NG)
  3. 整合 OK → F-05-008 子フロー呼び出し (text_4='')
  4. 整合 NG → AI prompt5 で補完試行 (`results` 配列、document_item に "address_kana" 含めば補完済み)
     - 補完 OK → 補完後カナで F-05-008 呼び出し
     - 補完 NG → 補完不可結果のみ返す

### 変更内容 (backend)
- 新規:
  - `app/domain/rules/address/address_kanji_kana_match.py` (`AddressKanjiKanaMatchRule`, rule_version 1.0.0)
  - `app/infrastructure/ai/prompts/address_kanji_kana_consistency_v1.txt`
  - `app/infrastructure/ai/prompts/address_kanji_kana_complement_v1.txt`
  - `tests/unit/rules/address/test_address_kanji_kana_match.py` (7 件)
  - `tests/integration/test_api_address_kanji_kana_match.py` (4 件)
- 変更:
  - `app/infrastructure/ai/fake_client.py` - `address_kanji_kana_consistency` / `address_kanji_kana_complement` プロンプト対応 (漢字→カナマッピングフィクスチャ)
  - `app/api/deps.py` - `get_address_kanji_kana_match_rule()` 追加
  - `app/api/v1/schemas.py` - `AddressKanjiKanaMatchRequest` / `Response` DTO 追加
  - `app/api/v1/checks.py` - `POST /v1/checks/address-kanji-kana-match` エンドポイント追加

### 設計上の判断
- **`AddressKanjiKanaMatchRule` は `AddressMasterMatchRule` を依存注入で委譲呼び出し**: F-05-008 のロジックを再実装せず、`Application.address_kana` を補完値で差し替えて (`model_copy(update=...)`) 委譲する。これにより F-05-008 単体での動作互換性も維持
- **`FakeAIClient` の整合チェック擬似ロジック**: 漢字側に既知フィクスチャ (`神宮前`/`歌舞伎町`/`南青山`/`丸の内`/`美しが丘`) が含まれ、カナ側にも対応する短いカナ (`ジングウマエ` 等) が含まれれば OK、漢字だけマッチでカナ側不一致なら NG (補完候補あり)、漢字フィクスチャ無しなら NG (補完不可)。これで「整合 OK / 整合 NG・補完 OK / 整合 NG・補完 NG / 補完後 KEN_ALL フォールバック」の 4 ケースを網羅できる
- **複数 CheckResult 返却の見送り**: 元 PA は document_item1 (住所(〒)) と document_item2 (住所カナ) で別々の回復結果を返すが、PoC では単一 `CheckResult` に集約 (recovery_reason に補完 reason を prefix、`details` に整合・補完情報を全て格納)。`CheckRule.execute()` 抽象を変更すると影響範囲が大きいため商用化時の課題として明文化
- **API 入力契約**: `address_kanji` を必須化 (案A の意図を反映)。F-05-008 の `address_kanji` は KEN_ALL フォールバック専用 (任意) だったが、F-05-006 では必須

### 動作確認結果
- `pytest -q` → **30 passed in 0.56s** (T-004 単体 7 + 統合 4 + 既存 19)
- Cloud Run へのデプロイ・curl 動作確認は **次セッションで実施**

### 次セッションへの申し送り
1. **T-004 を git commit** (新規 5 ファイル、変更 4 ファイル、テスト全 pass 状態)
2. ユーザーが Cloud Shell で `make gcb-deploy && make run-deploy` → 4 ケース curl 確認
   - 整合 OK: `address_kanji=東京都渋谷区神宮前..., address_kana=トウキョウトシブヤクジングウマエ...` → 150-0001
   - 整合 NG & 補完 OK: `address_kanji=...神宮前..., address_kana=トウキョウトチヨダクマルノウチ` → 150-0001 (補完後)
   - 整合 NG & 補完 NG: `address_kanji=存在しない漢字町, address_kana=ジングウマエ` → NG
   - 補完 OK & KEN_ALL フォールバック: `address_kanji=...美しが丘..., address_kana=トウキョウトチヨダクマルノウチ` → 225-0002
3. **T-005 (F-05-005 オーケストレータ)** に進む — F-05-006 が F-05-008 を内部委譲済みなので薄い実装で済む見込み
