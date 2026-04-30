# ADR-0001: Hexagonal Architecture とインフラ基盤可搬性

- ステータス: Accepted
- 採択日: 2026-04-30
- 関連: `backend/CLAUDE.md` §2 (アーキテクチャ), §8 (外部依存の扱い), §9 (環境と切り替え)

## 背景

本システムは PoC 段階で GCP (Cloud Run / Cloud SQL / Vertex AI) を前提に開発を進めている。
しかし以下の理由から、アプリケーションコアが特定インフラ基盤に密結合した状態は望ましくない:

- 本番運用フェーズで AWS / Azure / オンプレミス / Kubernetes など別基盤への移行・並行運用が発生しうる
- 顧客側のセキュリティ要件・コンプライアンス要件によっては、特定クラウドが選択肢から外れる可能性がある
- ベンダロックインは事業継続上のリスク (価格交渉力・SLA 起因の事業停止リスク等)
- PoC 中に染み込んだ前提は本番化時に書き直しコストとして顕在化しやすい

PoC 中の意思決定が将来コストを決定するため、**早期に境界を引く**。

## 決定事項

本リポジトリは **Hexagonal Architecture (Ports & Adapters)** を厳密に適用する。
アプリケーションコアはインフラ基盤・クラウドプロバイダ・特定 SDK に依存してはいけない。

### レイヤーの位置づけ

| レイヤー | パス | 役割 | 外部依存 |
|---|---|---|---|
| Domain (Pure Core) | `app/domain/` | ビジネスロジック・ルール・エンティティ | stdlib + pydantic のみ |
| Application | `app/application/` | ユースケース (オーケストレーション) | Domain のみ |
| API | `app/api/` | HTTP 受け口・DTO 変換・DI 配線 | Application + Domain (Port) + フレームワーク (FastAPI 等) |
| Infrastructure (Adapters) | `app/infrastructure/` | Port の具象実装 (差し替え対象) | 自由 (各クラウド SDK 等を許容) |

### Port (= 抽象)

すべての外部依存は `app/domain/interfaces/` 配下に Python ABC として Port を定義する。
Domain / Application は **常に Port のみを参照** し、具象実装の存在を知らない。

該当する外部依存:

- 永続化 (DB, KVS, ファイルシステム)
- AI 推論サービス
- オブジェクトストア / 画像参照
- シークレット取得
- 認証・JWT 検証
- 監査ログ書き込み
- 観測性 (トレーシング・メトリクス)
- 通知・メッセージング

### Adapter (= 具象)

Port の実装は `app/infrastructure/{category}/` 配下に置く。
**1 プロバイダ = 1 ファイル** を原則とする。

例 (将来形):

```
app/infrastructure/
├── ai/
│   ├── fake_client.py            # 開発・テスト用
│   ├── bedrock_proxy_client.py   # AWS Bedrock 経由 (現行 PoC AI バックエンド)
│   ├── vertex_client.py          # GCP Vertex AI
│   └── azure_openai_client.py    # Azure OpenAI
├── db/
│   └── repositories/
│       ├── in_memory_address_master.py
│       └── sqlalchemy_address_master.py    # PostgreSQL (Cloud SQL/RDS/Azure DB のいずれでも動く)
├── secrets/
│   ├── env_var_secrets_loader.py           # ローカル開発
│   ├── gcp_secret_manager.py
│   ├── aws_secrets_manager.py
│   └── azure_key_vault.py
├── image_store/
│   ├── mock_store.py
│   ├── legacy_db_store.py
│   ├── s3_store.py
│   └── gcs_store.py
└── audit/
    ├── logging_audit_logger.py             # stdout 構造化 JSON (どのクラウドでも拾える)
    └── db_audit_logger.py                  # audit_logs テーブル書き込み
```

切り替えは `app/api/deps.py` の DI factory + `app/config.py` の Settings で行う。

### 設定の構造

プロバイダ依存の設定は `Settings.<category>.<provider>` のネストモデルに格納する:

```python
class Settings(BaseSettings):
    ai: AISettings
    # 将来: secrets: SecretsSettings, image_store: ImageStoreSettings, ...
```

フィールド名にプロバイダ名を平坦に並べてはいけない (`bedrock_url`, `vertex_url`, `azure_url` 等の混在禁止)。
プロバイダ判別は `<category>.provider` enum で表現する。

### 禁止事項 (CI で機械検証)

- `domain/` から `infrastructure/` の具象を import しない
- `application/` から `infrastructure/` の具象を import しない
- `domain/` からクラウド SDK (`google.cloud.*`, `boto3`, `azure.*` 等) を import しない
- `app/main.py` `app/config.py` で特定クラウド SDK を import しない
- ベースイメージは汎用 (`docker.io/library/python:*`) を使い、クラウド固有レジストリ専用イメージに依存しない

`tests/architecture/test_layer_boundaries.py` で上記を ast 解析により検証する。

### コメント・ドキュメントのトーン

コード内コメントで特定クラウドサービス名を「前提」として書かない。
理由を一般化して記述する:

- 悪い例: `# Cloud Run は PORT 環境変数を渡してくる`
- 良い例: `# 12-Factor 準拠: PORT 環境変数でリッスンポートを上書き可能`

クラウド固有の落とし穴 (Knative queue-proxy の予約パス問題等) は memory ファイル
あるいは ADR で別途記録する。

### 新しい外部依存を追加する手順

1. `domain/interfaces/{name}.py` に Port (ABC) を先に書く
2. `tests/unit/` に Port 契約のテスト (`Fake{Name}` を使ったもの) を書く
3. `infrastructure/{category}/{provider}_*.py` に Adapter を書く
4. `app/api/deps.py` で DI factory に登録する
5. `app/config.py` の Settings 階層に必要なら設定を追加する

**Adapter を先に書いて Port を後付けすることは禁止**。

### デプロイ・ビルド成果物の扱い

- アプリケーションリポジトリ (本リポジトリ) は `Containerfile` (汎用 OCI イメージ) のみを Source of Truth とする
- 各クラウド固有のデプロイ定義 (`cloudbuild.yaml`, GitHub Actions の AWS workflow, Azure Pipelines 等) は同居可能だが、**`deploy/<platform>/` 配下に分離**することを推奨 (将来作業)
- Makefile のデプロイターゲットは `deploy-gcp` `deploy-aws` 等 platform-suffix で分けることを推奨

## 影響 (Consequences)

### 利点

- 任意のインフラ基盤への移植が「Adapter 1 クラス追加 + DI 配線 1 行」で完結する
- ベンダロックインリスクが管理可能になる
- ドメインロジックがインフラ詳細に汚染されない (テスト容易性・可読性が向上)
- Fake/NoOp 実装でテストを完全に独立させられる

### 制約

- Adapter のボイラープレート (薄いラッパクラス) が増える
- 設定構造が浅い辞書から見ると複雑になる
- 「ちょっとだけ SDK を直接呼ぶ」が許されなくなる

これらのコストは将来の移植コスト・本番化コストに比べれば十分小さく、トレードオフとして許容する。

## 検証方法

1. **境界テスト**: `tests/architecture/test_layer_boundaries.py` が CI で実行され、依存方向違反を機械検出する
2. **コードレビュー**: 新しい外部依存を追加する PR は「Port が先に切られているか」をチェック項目に含める
3. **設定構造**: `Settings` がプロバイダ平坦フィールドを持っていないことを定期的に見直す

## 関連メモリ

- `~/.claude/projects/.../memory/project_cloud_run_reserved_paths.md` — Cloud Run / Knative の予約パス問題 (基盤固有の罠の記録例)
