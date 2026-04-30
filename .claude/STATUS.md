# プロジェクト現状サマリ

最終更新: 2026-04-28 (T-003 KEN_ALL フォールバック実装完了 / 未コミット)

## 概要
保険申込書の一次チェックを AI で自動化するシステムの PoC。Power Automate で動いている既存のエラー回復フローを Python (FastAPI) に移行し、Cloud Run 上で動作させる。3 リポジトリ構成 (frontend / backend / database)。

## 現在のフェーズ
- **T-001 (F-05-008 Aflac 突合) は Cloud Run 稼働中** ✅
- **T-003 (F-05-008 KEN_ALL フォールバック + 全角→半角カナ変換) 実装・テスト完了 / 未コミット・未デプロイ** ✅
- **T-004 (F-05-006 住所漢字・カナ突合) は未着手**
  - 元フロー JSON (`【エラー回復】F-05-006`) の読解は途中。実装は未開始

## いま着手中のタスク
- なし（セッション終了）

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

- **(まず)** T-003 を git commit → Cloud Shell で `make gcb-deploy && make run-deploy` → curl で `address_kanji` 経由のフォールバック動作確認
- **T-004** F-05-006 住所漢字・カナ突合ルール
  - 元フロー: `【エラー回復】F-05-006_住所漢字・カナ突合` (`ff08e2ed-7001-f111-8406-002248ef6599`)
  - **読解済みポイント**:
    - 入力: text(親フロー情報) / text_1(プロンプト) / text_2(属性情報) / text_3(ATLAS登録データ) / text_4(点検結果テーブル)
    - 主要ロジック:
      1. メイン書類 (SharePoint から base64 取得) を AI 「メイン書類読取り」(prompt1) に投げて住所漢字を抽出
      2. AI 「住所漢字とカナの整合チェック」(prompt2) で 漢字 vs カナ の整合チェック
      3. 整合 OK → そのまま F-05-008 子フロー呼び出し (text_4='' = 補完なし)
      4. 整合 NG → AI 「住所漢字・住所カナ補完」(prompt5) で補完試行
         - 補完 OK & 補完項目に "address_kana" 含まれる → 補完後カナを変数に保存して F-05-008 子フロー呼び出し (text_4=補完後カナ)
         - F-05-008 結果配列を `document_item2` (=カナ用) と それ以外 で分岐し recovery_reason を結合する処理あり
         - 補完 NG → 補完不可の回復結果のみ返す
    - PoC スコープでの簡略化案:
      - SharePoint からの画像取得・base64・「メイン書類読取り」AI は **モック** (画像 OCR 入力をテキストで受ける形にする) — 既存 `FakeAIClient` に新プロンプトを追加するか、API 入力で漢字を直接渡す形にして整合チェックから始めるかの判断が必要
  - **次セッションで先に決めること**: 上記「メイン書類読取り」をどこまでモックで再現するか (API 入力に `extracted_address_kanji` を直接渡す形が現実的)
- **T-005** F-05-005 住所回復処理オーケストレータ (T-004 完了後)
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
- 個人情報をリポジトリ・ログに出さない
- スキーマ変更は `database/` リポジトリの責務（backend からマイグレーション実行禁止）
