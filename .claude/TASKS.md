# タスク一覧

## 進行中
（なし）

## 未着手
- [ ] **T-002** Bedrock プロキシ実クライアント実装（`BedrockProxyClient` を `AIClient` 抽象に差し込み）
  - 前提: ユーザーから Bedrock プロキシのレスポンス形式共有
  - リクエスト形式は判明済: `{"message": "...", "model": "global.anthropic.claude-sonnet-4-6"}`
- [ ] **T-003** F-05-008 郵政住所マスタフォールバック実装（KEN_ALL 突合 + 全角→半角カナ変換）
- [ ] **T-004** F-05-006 住所漢字・カナ突合ルール実装
- [ ] **T-005** F-05-005 住所回復処理（オーケストレータ）実装
- [ ] **T-006** F-05-007 文字数超過チェック・F-05-009 中間結果登録 子フロー本体実装
- [ ] **T-007** Cloud SQL 接続 + ORM モデル + SqlAlchemyAddressMasterRepository
  - 前提: Cloud SQL Admin API 有効化 + インスタンス作成（ユーザー作業）
- [ ] **T-008** Entra ID JWT 検証ミドルウェア
- [ ] **T-009** API Gateway 配置（必要に応じて）

## 完了
- [x] **T-001** 住所フロー最小移行（F-05-008 単体）— 2026-04-27 完了
  - サブタスク全完了:
    - [x] T-001-1 バックエンド骨格セットアップ（pyproject / Containerfile / cloudbuild.yaml / Makefile / config）
    - [x] T-001-2 ドメイン層実装（CheckRule 抽象 / エンティティ / インターフェース）
    - [x] T-001-3 F-05-008 住所マスタ突合ルール実装
    - [x] T-001-4 インフラ Fake/InMemory 実装（FakeAIClient + InMemoryAddressMasterRepository）
    - [x] T-001-5 API エンドポイント実装（/v1/checks/address-master-match + /healthz）
    - [x] T-001-6 単体テスト 5 + 統合テスト 3 (全 pass)
    - [x] T-001-7 デプロイ手順整備（Makefile + cloudbuild.yaml + README）

## 保留・廃止
（なし）
