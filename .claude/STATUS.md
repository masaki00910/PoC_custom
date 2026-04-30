# プロジェクト現状サマリ

最終更新: 2026-04-30 (T-003/T-004/T-010 デプロイ + 動作確認完了)

## 概要
保険申込書の一次チェックを AI で自動化するシステムの PoC。Power Automate で動いている既存のエラー回復フローを Python (FastAPI) に移行し、Cloud Run 上で動作させる。3 リポジトリ構成 (frontend / backend / database)。

## 現在のフェーズ
- **T-001 / T-003 / T-004 / T-010 すべて Cloud Run デプロイ済 + 動作確認 OK** ✅
  - 5 ケース全部期待通り (health / Aflac ヒット / KEN_ALL フォールバック / F-05-006 整合 OK / F-05-006 整合 NG→補完 OK)

## いま着手中のタスク
- なし（セッション終了）

## 直近完了したタスク
- **T-010** Hexagonal Architecture / インフラ可搬性ガードレール整備 — **2026-04-30 完了**
  - ADR-0001 採択 (`backend/docs/adr/0001-hexagonal-portability.md`)
  - 境界テスト 6 本追加 (`backend/tests/architecture/test_layer_boundaries.py`) — domain → infrastructure 依存禁止 / クラウド SDK 直接 import 禁止を CI で機械検証
  - `config.py` 再構成: `AIProviderKind` リネーム、`AISettings` + `BedrockProxySettings` のネスト、`env_nested_delimiter='__'` 採用
  - 連動: `.env.example` / `Makefile` / `README.md` を `AI__PROVIDER` 形式に統一
  - コメント抽象化: `main.py` `Containerfile` から特定クラウド名を一般化
  - 全テスト pass: バックエンド 34 + 境界 4 + skip 2 = 40

- **T-004** F-05-006 住所漢字・カナ突合 (案A) — **2026-04-30 完了 (commit 68205c0)**
  - 案A: SharePoint/OCR スキップ、API 入力で address_kanji を直接受け取る
  - 動作: 整合 OK → F-05-008 委譲 / 整合 NG & 補完 OK → 補完カナで F-05-008 委譲 / 整合 NG & 補完 NG → NG
  - テスト: 単体 7 + 統合 4 = 計 11 件 pass

## 直近完了したタスク
- **T-003** F-05-008 郵政住所マスタ (KEN_ALL) フォールバック + 全角→半角カナ変換 — **2026-04-28 完了 (ローカルテストのみ)**
  - 追加: `JapanPostAddressMasterRecord` エンティティ, `find_japan_post_by_prefecture_municipality_town` リポジトリメソッド, `address_kanji_split` AI プロンプト + Fake 応答, KEN_ALL フィクスチャ, `kana_converter.py` (PA フローの 78 文字マッピング忠実コピー)
  - 変更: `AddressMasterMatchRule` (バージョン 1.0.0 → 1.1.0)、Aflac ヒット 0 件 → KEN_ALL 漢字突合 → 単一郵便番号なら OK + 半角カナ変換、複数なら NG、0 件なら NG (該当〒番号なし)
  - 変更: `Application` に `address_kanji` 追加 (デフォルト空文字、後方互換)
  - 変更: API スキーマに `address_kanji` 追加
  - テスト: 単体 11 (kana_converter 6 + address_master_match 8) + 統合 5 = **19 件全 pass**
  - **未コミット / 未デプロイ**: ローカルでテストパスのみ。次セッション冒頭で commit + Cloud Run 再デプロイ → curl 動作確認の流れを推奨

## 次にやること（次セッションで実装する候補）

優先度順:

- **T-005** F-05-005 住所回復処理オーケストレータ
  - 元フロー: `65f74109-84fa-f011-8406-002248f17ef0`
  - F-05-006 (T-004 で実装済み) → F-05-008 (T-001/T-003 で実装済み) を順に呼ぶ親フロー
  - PoC スコープでは F-05-006 を呼ぶだけで F-05-008 は内部委譲しているので、オーケストレータの実装は薄くなる見込み
- **T-002** Bedrock プロキシ実 AI クライアント
- **T-006** F-05-007 文字数超過 / F-05-009 中間結果登録
- **T-007** Cloud SQL 接続 / SqlAlchemyAddressMasterRepository
- **T-008** Entra ID JWT 検証ミドルウェア
- **T-009** API Gateway

### スモークテストスクリプト (再利用可)
将来別エンドポイントを追加したら同形式で `backend/scripts/smoke_test.sh` (※未 commit) を更新する想定。今は git 管理外で `bash scripts/smoke_test.sh ${SERVICE_URL}` でも `bash <貼り付けスクリプト>` でも可
- **T-002** Bedrock プロキシ実クライアント (Bedrock レスポンス JSON 形式の共有が前提)
- **T-006** F-05-007 文字数超過チェック / F-05-009 中間結果登録 (T-003 で details に半角カナ変換済みの結果を保持済み → 文字数比較ロジックが本体)
- **T-007** Cloud SQL 接続 + ORM モデル + SqlAlchemyAddressMasterRepository
- **T-008** Entra ID JWT 検証ミドルウェア

## 重要な前提・制約・既知の問題

### 元 PA フローのバージョン選択
- `sample_modernflows/` 配下に各フロー 2 バージョン存在 (【エラー回復】=live / 【工藤修正中】=draft)
- T-001 / T-003 は **【エラー回復】(live)** 版を正として移行済み
- T-004 以降も同方針で進める (差し戻し指示があれば変更)

### GCP 環境 (`poc-custom` プロジェクト)
- 有効な API: Cloud Run / Artifact Registry / Cloud Build / Secret Manager / Logging / Monitoring 等
- **未有効**: Vertex AI / Cloud SQL Admin / API Gateway
- リージョン: `asia-northeast1`

### AI クライアント
- 暫定: AWS API Gateway 経由の Bedrock プロキシ `https://6mlsx5sseg.execute-api.ap-northeast-1.amazonaws.com/dev/chat`
- リクエスト形式: `{"message": "...", "model": "global.anthropic.claude-sonnet-4-6"}`、認証なし
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
- **インフラ基盤可搬性: ADR-0001 (`backend/docs/adr/0001-hexagonal-portability.md`) に従う。Hexagonal Architecture を厳守。アプリケーションコアはインフラ基盤・クラウド SDK に依存しない。新しい外部依存を追加するときは Port を先に切る。境界テスト (`tests/architecture/test_layer_boundaries.py`) が CI で違反を検出**
- 個人情報をリポジトリ・ログに出さない
- スキーマ変更は `database/` リポジトリの責務（backend からマイグレーション実行禁止）
