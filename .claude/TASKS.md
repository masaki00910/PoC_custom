# タスク一覧

## 進行中
（なし）

## 未着手
- [ ] **T-002** Bedrock プロキシ実クライアント実装（`BedrockProxyClient` を `AIClient` 抽象に差し込み）
  - 前提: ユーザーから Bedrock プロキシのレスポンス形式共有
  - リクエスト形式は判明済: `{"message": "...", "model": "global.anthropic.claude-sonnet-4-6"}`
- [ ] **T-005** F-05-005 住所回復処理（オーケストレータ）実装
  - 元フロー: `65f74109-84fa-f011-8406-002248f17ef0` (【エラー回復】F-05-005_項目補正-住所回復処理)
  - F-05-006 → F-05-008 を順に呼ぶ親フロー
- [ ] **T-006** F-05-007 文字数超過チェック・F-05-009 中間結果登録 子フロー本体実装
- [ ] **T-007** Cloud SQL 接続 + ORM モデル + SqlAlchemyAddressMasterRepository
  - 前提: Cloud SQL Admin API 有効化 + インスタンス作成（ユーザー作業）
- [ ] **T-008** Entra ID JWT 検証ミドルウェア
- [ ] **T-009** API Gateway 配置（必要に応じて）

## 完了
- [x] **T-010** Hexagonal Architecture / インフラ可搬性ガードレール整備 — 2026-04-30 完了
  - ADR-0001 採択: アプリケーションコアはインフラ基盤に依存しない方針を明文化
  - 境界テスト追加: domain → infrastructure / クラウド SDK import 禁止を CI で機械検証
  - `config.py` 再構成: `AIProviderKind` リネーム、`AISettings` + `BedrockProxySettings` ネスト構造、`env_nested_delimiter='__'`
  - 連動: `.env.example` / `Makefile` / `README.md` を `AI__PROVIDER` 形式に
  - コメント抽象化: `main.py` `Containerfile` から特定クラウド名を一般化
  - 撤回: 未実装 Port 雛形 (`SecretsLoader` 等) は実 callers が出るまで追加しない (境界テスト + ADR で同等保護)

- [x] **T-004** F-05-006 住所漢字・カナ突合ルール実装 — 2026-04-30 commit 済 (`68205c0`) / 未デプロイ
  - 案A 採用: SharePoint/OCR (prompt1) はスキップし、API 入力で `address_kanji` を直接受け取る
  - 新規: `AddressKanjiKanaMatchRule`, 整合チェック/補完プロンプト 2 本, FakeAIClient 拡張, 新エンドポイント `/v1/checks/address-kanji-kana-match`
  - テスト: 単体 7 + 統合 4 = 計 11 件 pass

- [x] **T-001** 住所フロー最小移行（F-05-008 単体）— 2026-04-27 完了
  - サブタスク全完了:
    - [x] T-001-1 バックエンド骨格セットアップ
    - [x] T-001-2 ドメイン層実装
    - [x] T-001-3 F-05-008 住所マスタ突合ルール実装 (Aflac のみ)
    - [x] T-001-4 インフラ Fake/InMemory 実装
    - [x] T-001-5 API エンドポイント実装
    - [x] T-001-6 単体テスト 5 + 統合テスト 3 (全 pass)
    - [x] T-001-7 デプロイ手順整備
- [x] **T-003** F-05-008 KEN_ALL フォールバック + 全角→半角カナ変換 — 2026-04-28 ローカル完了, 2026-04-30 commit 済 (`7a886db`) / 未デプロイ
  - サブタスク全完了:
    - [x] T-003-1 `JapanPostAddressMasterRecord` エンティティ追加
    - [x] T-003-2 `find_japan_post_by_prefecture_municipality_town` リポジトリインターフェース追加
    - [x] T-003-3 `Application` に `address_kanji` フィールド追加
    - [x] T-003-4 `kana_converter.py` 新規 (PA フローの 78 文字マッピング忠実コピー)
    - [x] T-003-5 `AddressMasterMatchRule` に KEN_ALL フォールバック分岐追加 (rule_version 1.0.0 → 1.1.0)
    - [x] T-003-6 `FakeAIClient` に `address_kanji_split` プロンプト対応追加 (フィクスチャ整理含む)
    - [x] T-003-7 `InMemoryAddressMasterRepository` に KEN_ALL フィクスチャ + メソッド追加
    - [x] T-003-8 プロンプトファイル `address_kanji_split_v1.txt` 追加
    - [x] T-003-9 API スキーマに `address_kanji` フィールド追加
    - [x] T-003-10 単体・統合テスト追加 (kana_converter 6 + 統合 5 + 既存テスト更新 = 計 19 件 pass)
  - **次セッション TODO**: git commit → Cloud Run 再デプロイ → 動作確認

## 保留・廃止
（なし）
