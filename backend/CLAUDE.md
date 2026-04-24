# CLAUDE.md — Backend

このファイルは Claude Code がこのリポジトリで作業するときに必ず最初に読む規約です。
書かれている内容はプロジェクト全体の設計判断であり、**個別タスクの実装中にこれらの方針から逸脱してはいけません**。方針自体を変える必要があると判断した場合は、コード変更の前にその旨を明示して確認を取ってください。

---

## 1. プロジェクト概要

### 目的
保険申込書の一次チェックを AI で自動化するシステムのバックエンド。
既存の Power Automate ベースの業務フローを Python に再構成し、オブジェクト指向で保守性・拡張性を高める。

### 位置づけ
- 現在は **PoC フェーズ** だが、**商用利用を見据えた設計・実装**を行う
- PoC で作ったコードがそのまま本番に昇格できる品質を目指す
- 「PoC だから雑に」は禁止。ただし「商用だから過剰に」も禁止。**インターフェースは本番想定、実装は段階的**というバランスを取る

### 全体構成
本システムは **3 リポジトリ構成**:
- `frontend/` — Power Apps PCF (React)
- `backend/` — Python FastAPI (**このリポジトリ**)
- `database/` — PostgreSQL スキーマ、マイグレーション、マスタデータ、IaC

```
[ユーザー (M365認証済)]
       ↓
[Power Apps (PCF + React)]  ← frontend リポジトリ
       ↓ Entra ID トークン付き HTTPS
       ↓
[GCP API Gateway]  ← JWT 検証
       ↓
[Cloud Run: FastAPI (このリポジトリ)]
       ├─ Cloud SQL (PostgreSQL)  ← database リポジトリがスキーマ管理
       ├─ 既存画像DB (PoC ではモック) ← 画像取得のみ、読み取り専用
       └─ Vertex AI (Gemini / Agent Builder) ← AI チェック
```

---

## 2. アーキテクチャ

### レイヤー構成 (クリーンアーキテクチャ風 4 層)

```
app/
├── api/              ← HTTP 受け口、認証、DTO 変換
├── application/      ← ユースケース (業務操作の単位)
├── domain/           ← ビジネスロジック。外部依存なし
└── infrastructure/   ← DB、AI、外部サービス実装。差し替え対象
```

### 依存方向の絶対ルール

```
api → application → domain ← infrastructure
```

- `domain/` は他層に依存してはいけない (stdlib と pydantic のみ許可)
- `infrastructure/` は `domain/interfaces/` を実装する側。`domain` から `infrastructure` の具象クラスを import することは禁止
- `application/` は `domain/` の抽象を使う。`infrastructure/` の具象には依存しない (DI で注入される)
- `api/` は `application/` のユースケースを呼ぶ。`domain/` のエンティティを DTO に変換するのみ許可

この依存方向を破る実装は商用化時に必ず技術的負債になる。**レイヤー違反は必ず指摘・修正すること**。

### ディレクトリ構造 (正)

```
backend/
├── CLAUDE.md                       ← このファイル
├── README.md
├── pyproject.toml                  ← uv で管理
├── Containerfile                   ← Podman 用 (Dockerfile 互換)
├── compose.yml                     ← ローカル用。DB は database リポジトリの compose を参照
├── Makefile
├── .env.example
├── .gitignore
├── .containerignore
│
├── docs/
│   ├── architecture.md
│   ├── domain-model.md
│   ├── check-rules-catalog.md      ← 全チェック観点の一覧
│   ├── data-migration.md
│   └── adr/                        ← アーキテクチャ決定記録
│
├── app/
│   ├── __init__.py
│   ├── main.py                     ← FastAPI エントリポイント
│   ├── config.py                   ← Pydantic Settings
│   │
│   ├── api/
│   │   ├── deps.py                 ← DI コンテナ
│   │   ├── middleware/
│   │   │   └── auth.py             ← Entra ID JWT 検証
│   │   └── v1/
│   │       ├── applications.py
│   │       ├── checks.py
│   │       ├── images.py
│   │       ├── masters.py
│   │       └── schemas.py          ← Pydantic DTO
│   │
│   ├── application/
│   │   ├── run_checks.py
│   │   ├── get_check_result.py
│   │   └── upload_application.py
│   │
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── application.py
│   │   │   ├── check_result.py
│   │   │   ├── image_reference.py
│   │   │   └── master_data.py
│   │   ├── rules/
│   │   │   ├── base.py             ← CheckRule 抽象基底クラス
│   │   │   ├── identity/
│   │   │   ├── medical/
│   │   │   └── contract/
│   │   ├── orchestrator.py
│   │   └── interfaces/
│   │       ├── ai_client.py
│   │       ├── repository.py
│   │       ├── image_store.py
│   │       └── master_loader.py
│   │
│   └── infrastructure/
│       ├── db/
│       │   ├── session.py
│       │   ├── models.py              ← ORM モデル (database リポジトリのスキーマに追従)
│       │   └── repositories/
│       ├── image_store/
│       │   ├── mock_store.py          ← PoC 用
│       │   ├── legacy_db_store.py     ← 商用時に実装
│       │   └── fixtures/
│       └── ai/
│           ├── vertex_client.py
│           ├── fake_client.py         ← ローカル開発用
│           └── prompts/
│
├── scripts/
│   └── seed_dev_data.py               ← 開発用シードデータ投入
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
└── .github/workflows/
```

**注**: スキーマ定義・マイグレーション・CSV マスタ・シードデータは別リポジトリ (`database/`) で管理する。詳細は後述。

**新しいディレクトリを勝手に増やさない**。必要な場合は先に提案して合意を取る。

---

## 3. ドメイン設計の核: CheckRule

### 基本方針
- Power Automate の「1 フロー」に相当するものを、`CheckRule` を継承したクラスとして実装する
- **1 観点 = 1 クラス = 1 ファイル** を原則とする
- 業務カテゴリごとに `domain/rules/{category}/` にサブディレクトリを切る

### CheckRule 抽象基底クラスの契約

```python
class CheckRule(ABC):
    name: str            # ルールの一意識別子
    category: str        # 業務カテゴリ
    severity: Severity   # ERROR / WARNING / INFO
    version: str         # ルールのバージョン (監査用)

    @abstractmethod
    async def execute(
        self,
        application: Application,
        context: CheckContext,
    ) -> CheckResult:
        ...
```

### 新しいチェックルールを追加する手順

Claude Code が「新しいチェック観点を追加して」と依頼されたときは、以下の手順を**必ず**踏む:

1. `domain/rules/{category}/{rule_name}.py` を作成し、`CheckRule` を継承
2. `execute()` を実装 (外部依存は DI でコンストラクタ注入)
3. `tests/unit/rules/{category}/test_{rule_name}.py` にテストを追加 (正常系・異常系・境界値)
4. `api/deps.py` のルール登録リストに追加
5. `docs/check-rules-catalog.md` に観点の説明を追記

上記 5 ステップのうち、どれか 1 つでも欠けたら未完成扱い。勝手にスキップしない。

---

## 4. コーディング規約

### Python バージョン
- Python 3.12 以上を前提
- 型ヒント必須 (`from __future__ import annotations` を使う)
- `mypy --strict` が通ることを目指す

### スタイル
- フォーマッタ: `ruff format`
- リンター: `ruff check`
- 設定は `pyproject.toml` に集約

### 命名規則
- クラス: PascalCase (`CheckRule`, `ApplicationRepository`)
- 関数・変数: snake_case
- 定数: UPPER_SNAKE_CASE
- プライベート: `_` プレフィックス
- ドメインエンティティは**業務用語**をそのまま使う (例: `Application`, `Underwriter`)。技術用語 (`Data`, `Model`) を安易につけない

### 型の扱い
- ドメインエンティティは `dataclass(frozen=True)` または `pydantic.BaseModel` で不変に
- ID は `UUID` 型、または `NewType` で意味的に区別する (例: `ApplicationId = NewType("ApplicationId", UUID)`)
- `Any` 型の使用は禁止。やむを得ない場合は理由をコメントで明記

### 非同期処理
- I/O を伴う処理 (DB、HTTP、AI 呼び出し) はすべて `async`
- 同期と非同期を混ぜない。`asyncio.run` を関数内で呼ばない
- 並列実行は `asyncio.gather` を使い、エラー伝播方針を明示する

### エラーハンドリング
- ドメイン例外は `domain/exceptions.py` に集約。業務エラー (`ValidationError`, `RuleExecutionError` 等) を定義
- `except Exception:` の裸 catch は禁止。必ず具体的な例外型を指定
- ログを出さずに例外を握りつぶすのは禁止
- API 層でドメイン例外を HTTP ステータスコードに変換する

---

## 5. テスト方針

### 基本原則
- **テストを書かないコードを main にマージしない**
- PoC だからテストを省略、はしない。PoC 段階で書かないと商用化時に誰も書かなくなる

### カバレッジ目標
- `domain/` 層: 90% 以上
- `application/` 層: 80% 以上
- `infrastructure/` 層: 主要経路をカバーする統合テストがあれば 60% 以上で可
- `api/` 層: E2E で主要ユースケースを網羅

### テストの種類と配置
- **unit**: `tests/unit/` — 外部依存を持たない純粋なロジック。モック不要で書けるものが理想
- **integration**: `tests/integration/` — DB や AI 等の外部を含む。Podman Compose で起動
- **e2e**: `tests/e2e/` — API を HTTP 越しに叩く

### フレームワーク
- `pytest` + `pytest-asyncio`
- フィクスチャは `tests/conftest.py` と各階層の `conftest.py` に分割
- モックは `unittest.mock` ではなく、**fake 実装を優先** (例: `FakeAIClient`, `FakeImageStore`)。fake は `infrastructure/` 配下に正式な実装として置く

### テストデータ
- テスト用画像・CSV は `tests/fixtures/` に配置
- 業務で扱う本物のデータは**絶対にコミットしない**。個人情報を含むデータはリポジトリに入れない

---

## 6. セキュリティと個人情報の扱い

### 最優先事項
保険申込書には**機微個人情報 (氏名、住所、生年月日、健康情報、家族関係等)** が含まれる。漏洩は事業継続に関わる重大事故。以下を絶対に守る。

### ハードルール
- **個人情報をログに出力しない**。ログには ID や件数のみを記録し、内容は記録しない
- **個人情報を平文で外部通信に乗せない**。すべて HTTPS、DB 接続は SSL 必須
- **個人情報をリポジトリにコミットしない**。テストデータは必ずダミー
- **Secret を環境変数以外で管理しない**。Secret Manager 経由で読み込む
- **エラーメッセージに個人情報を含めない**。ユーザー向けエラーは「申込 ID xxx のチェックに失敗しました」までに留める

### DB アクセス
- DB 接続は必ず Secret Manager から取得。`.env` にベタ書きしない
- クエリは ORM (SQLAlchemy) 経由。生 SQL を書く場合は必ずパラメータ化
- 監査ログ用テーブルへの書き込みは業務処理と同一トランザクションで行う

### 認証
- API への未認証アクセスは全て拒否 (ヘルスチェックを除く)
- JWT 検証は `api/middleware/auth.py` で行い、全ルーターに適用
- ユーザー識別は Entra ID の `oid` (Object ID) を使う。メールアドレスは identifier として使わない

### データ保管
- Cloud SQL のリージョンは `asia-northeast1` (東京)
- 保存時暗号化、バックアップ自動取得、PITR 有効化
- アクセス権限は最小権限の原則 (Cloud Run のサービスアカウントから DB への接続のみ許可)

---

## 7. 監査ログと AI 説明可能性

### 監査ログの要件
保険業務は説明責任が重い。**「誰が、いつ、何を、どうチェックしたか」を後から完全に再現できる**ことを必須とする。

### 監査対象
- 申込の受付・更新・削除
- チェック実行の開始・終了・失敗
- AI への入力 (プロンプト、画像参照、パラメータ)
- AI からの出力 (生レスポンス含む)
- ユーザーによる手動操作 (判定の上書き等)
- 認証失敗

### 監査ログの保存先
- `audit_logs` テーブル (PostgreSQL)
- 構造化ログ (JSON) として Cloud Logging にも出力
- 保存期間は 7 年を想定 (保険業法の記録保存義務に合わせる)

### AI 説明可能性の要件
- 各チェック結果には、**使用したプロンプトのバージョン**、**入力データの要約**、**AI の生レスポンス**を紐付けて保存
- プロンプトはコードに埋め込まず、`infrastructure/ai/prompts/` でバージョン管理
- 判定根拠をユーザーに表示できる形で `check_results.details` (JSONB) に格納
- AI の出力が非決定的なため、**同じ入力で再実行して検証できる仕組み**を残す (プロンプトバージョン + モデルバージョン + パラメータを記録)

### 判定の人間によるレビュー
- AI の判定は「一次チェック」であり、**最終判定は人が行う**前提で設計する
- 「AI 判定を人が上書きした」という操作も監査ログに残す

---

## 8. 外部依存の扱い

### リポジトリ間の関係
本プロジェクトは **3 リポジトリ構成** (`backend/`, `frontend/`, `database/`)。バックエンドから見ると、DB スキーマは**外部契約**として扱う。

- **スキーマの Source of Truth は `database/` リポジトリ**
- バックエンドの `infrastructure/db/models.py` (ORM モデル) は、`database/` リポジトリのスキーマ定義に**追従する側**
- スキーマ変更が必要なときは**先に `database/` リポジトリで PR を作り、合意・マイグレーション適用 → その後バックエンドの ORM モデルを更新**する順序を守る
- バックエンドから Alembic マイグレーションを実行しない (責務が `database/` 側)

### 4 つの外部依存

| 依存先 | 用途 | 本番 | PoC |
|---|---|---|---|
| 自分たちの Postgres | 申込・結果・監査 | Cloud SQL (`database/` 管理) | Podman Compose (`database/` の compose 設定を参照) |
| 既存画像 DB | 画像取得 (Read only) | 既存 DB 接続 | **MockImageStore** |
| Vertex AI | AI チェック | Vertex AI | FakeAIClient (開発時) |
| マスタデータ | 業務マスタ参照 | DB (`database/` が投入) | DB (`database/` が投入) |

### 画像データの特別ルール
- 画像本体は**既存の外部 DB に格納されており、本プロジェクトでは参照のみ**
- **画像を自分たちの DB に保存してはいけない**
- `image_references` テーブルには**画像 ID や種別などの参照情報のみ**格納
- 画像取得は必ず `domain/interfaces/image_store.py::ImageStore` 経由
- PoC では `MockImageStore` を使う。本番接続 (`LegacyDbImageStore`) への切り替えは `config.py` の設定のみで完結させる
- **`infrastructure/db/` 配下に画像本体を扱うコードを書いてはいけない**

### マスタデータ (Excel → CSV 移行)
- CSV マスタの管理は `database/` リポジトリの責務
- バックエンドからは**通常のテーブルとして参照するだけ**。CSV を直接読み込まない
- バックエンド内に `infrastructure/csv/` は置かない
- マスタデータの更新は `database/` リポジトリで PR → マイグレーション反映

### AI クライアント
- `domain/interfaces/ai_client.py` で抽象を定義
- Vertex AI 実装は `infrastructure/ai/vertex_client.py`
- プロンプトは `infrastructure/ai/prompts/*.txt` にバージョン付きで管理
- ローカル開発では `FakeAIClient` を使い、Vertex AI 課金なしで開発できるようにする
- リトライ、タイムアウト、トークン数超過のハンドリングを必ず実装

---

## 9. 環境と切り替え

### 環境の種類
- `local`: 開発者 PC, Podman Compose, モック多用
- `dev`: GCP dev プロジェクト, 実 Vertex AI, モック画像 DB
- `stg`: GCP stg プロジェクト, 実画像 DB 接続検証
- `prd`: GCP prd プロジェクト, 本番運用

### 設定管理
- すべての環境差分は `config.py` (Pydantic Settings) と環境変数で制御
- コード内で環境名を直接分岐 (`if env == "prd":`) するのは禁止。設定値で制御する
- `.env.example` に必要な環境変数をすべて列挙し、実際の値はコミットしない

### 切り替え可能にしておくもの
- 画像取得先 (`MockImageStore` / `LegacyDbImageStore`)
- AI クライアント (`VertexClient` / `FakeAIClient`)
- DB 接続先
- ログレベル
- 認証の有効/無効 (ローカル開発のみ無効化可能)

---

## 10. コンテナ運用 (Podman)

### 前提
- **コンテナエンジンは Podman を使用する。Docker は使用禁止**
- 開発者の PC には Podman および `podman-compose` がインストールされている前提
- CI / 本番ビルドもすべて Podman で統一

### 命名・フォーマット規約
- Dockerfile ではなく **`Containerfile`** を使用 (Podman 公式推奨、中身は互換)
- Compose 定義は **`compose.yml`** (または `podman-compose.yml`) を使用
- `.dockerignore` ではなく **`.containerignore`** を使用 (Podman が認識)
- イメージ参照は**レジストリを完全指定**:
  - ✅ `docker.io/library/postgres:16`
  - ✅ `gcr.io/distroless/python3`
  - ❌ `postgres:16` (Podman の `unqualified-search-registries` 設定に依存するため避ける)

### Rootless コンテナ
- **Podman はデフォルトで rootless 実行される** (Docker との大きな違い)
- rootless でのファイル権限・ネットワーク制約 (ポート 1024 未満へのバインド不可等) を考慮する
- 開発時のファイルマウントでは UID マッピングに注意 (`--userns=keep-id` 等)

### よくある落とし穴と対策
- **SELinux 環境でのボリュームマウント**: `:Z` または `:z` サフィックスを付ける (例: `-v ./data:/data:Z`)
- **ネットワーク**: Podman の rootless モードでは `slirp4netns` が使われる。ホストから `127.0.0.1` 経由で接続する
- **`host.docker.internal` が使えない**: 代わりに `host.containers.internal` を使用
- **Pod の概念**: 複数コンテナを 1 Pod にまとめる Podman ネイティブ機能もあるが、**Compose との互換性を優先**し PoC では使わない

### CI での Podman
- GitHub Actions ランナーに Podman を事前インストール
- `podman build` → `podman push` の流れは Docker と同じ
- Artifact Registry 認証は `podman login` で実施

### Kubernetes への将来移行
- Podman は `podman generate kube` で Kubernetes YAML を生成可能
- Cloud Run 以外 (GKE 等) へ移行する際のパスとして認識しておく
- PoC 段階では不要

---

## 11. デプロイと CI/CD

### デプロイ先
- Cloud Run (asia-northeast1)
- IaC は Terraform (`infra/` リポジトリで別管理、またはサブディレクトリ)

### コンテナ
- **コンテナエンジンは Podman** を使用 (Docker は使用禁止)
- `Containerfile` を使用 (Dockerfile 互換フォーマット、拡張子のみ変更)
- マルチステージビルド、最終イメージは `docker.io/library/python:3.12-slim` ベース (Podman はレジストリを完全指定推奨)
- **rootless コンテナで実行** (Podman のデフォルト)。本番 (Cloud Run) も非 root ユーザーで実行
- `/healthz` エンドポイントで liveness/readiness を返す
- ビルド時は `podman build -t <tag> -f Containerfile .`
- Cloud Run へのデプロイには OCI 互換イメージを Artifact Registry に push (`podman push`)

### CI (GitHub Actions)
- PR で走るもの: `ruff check`, `ruff format --check`, `mypy`, `pytest`, カバレッジチェック
- main マージで走るもの: Podman でコンテナビルド、Artifact Registry へ push、dev 環境へ自動デプロイ
- stg/prd へのデプロイは手動承認
- GitHub Actions 上では Podman を事前インストール (`redhat-actions/podman-login` 等を利用)

### マイグレーション
- スキーマ変更は `database/` リポジトリの責務 (本リポジトリからは実行しない)
- バックエンドのデプロイタイミングと、DB マイグレーションの適用タイミングの調整は運用手順書で明文化
- ダウンタイムゼロを目指し、破壊的変更は 2 段階デプロイで行う

---

## 12. Claude Code への作業指示

### 作業前に必ず確認すること
1. このファイル (`CLAUDE.md`) 全体を読む
2. 関連する `docs/` 配下のドキュメントを確認
3. 既存の類似実装がないか確認 (重複実装を避ける)
4. タスクが不明瞭な場合は実装前に質問する

### 作業中の原則
- **小さく変更し、頻繁にテストを流す**。巨大な差分を一度に作らない
- **レイヤー違反をしない**。迷ったら依存方向ルールに戻る
- **勝手に設計判断を変えない**。方針変更が必要なら先に相談
- **TODO コメントを残さない**。残す場合は Issue 化して番号を書く

### コード生成時のチェックリスト
新しいコードを書いたら、以下を自己チェック:

- [ ] 型ヒントがすべてついている
- [ ] `domain/` が外部に依存していない
- [ ] 新しいルールなら 5 ステップをすべて踏んだ
- [ ] テストを書いた
- [ ] 個人情報をログに出していない
- [ ] Secret をハードコードしていない
- [ ] 監査ログが必要な操作に監査ログを仕込んだ
- [ ] エラーハンドリングが具体的な例外型で書かれている
- [ ] 非同期処理に同期処理を混ぜていない

### 禁止事項まとめ
- `domain/` から `infrastructure/` の具象を import しない
- 画像を自分たちの DB に保存しない
- **バックエンドリポジトリ内にマイグレーションファイルを作らない** (`database/` の責務)
- **バックエンドから直接 DDL (CREATE TABLE 等) を実行しない**
- **ORM モデルを先に変更してスキーマを追従させない**。必ず `database/` リポジトリ側でスキーマ変更 → バックエンドが追従
- CSV マスタファイルをバックエンドリポジトリに置かない
- 個人情報・Secret をリポジトリにコミットしない
- 個人情報をログに出さない
- `except Exception:` の裸 catch を書かない
- `Any` 型を安易に使わない
- テストなしでコードをコミットしない
- 設計方針を無断で変更しない
- 新しいディレクトリ構造を勝手に作らない

### 推奨事項まとめ
- 不明点は先に質問する
- 既存コードのパターンを踏襲する
- 小さい PR にする
- ドキュメントをコードと同時に更新する
- PoC でも商用品質を意識する

---

## 13. よく使うコマンド

```bash
# 初期セットアップ
make setup              # uv sync + pre-commit install

# 開発
make dev                # podman-compose up (DB は database リポジトリ参照)
make dev-down           # podman-compose down
make test               # pytest 全実行
make test-unit          # 単体テストのみ
make lint               # ruff check + mypy
make format             # ruff format

# 開発データ投入 (アプリ固有の開発用シードのみ)
make seed

# コンテナビルド (Podman)
make build              # podman build -t error-recovery-backend -f Containerfile .
make run                # podman run (ローカル動作確認)

# デプロイ (手元から dev 環境へ)
make deploy-dev         # podman push + Cloud Run デプロイ
```

**DB スキーマ操作** (マイグレーション、マスタデータ更新) は `database/` リポジトリ側で実施する。本リポジトリからマイグレーションコマンドは実行しない。

詳細は `Makefile` と `README.md` を参照。

---

## 14. 参考: PoC から商用への昇格基準

このプロジェクトは PoC だが、以下を満たせば「商用利用可」と判断できる状態を目指す:

- すべてのチェックルールに単体テストがある
- 主要ユースケースに E2E テストがある
- 監査ログが完全に取れている
- 認証が Entra ID で機能している
- 画像 DB が実接続に切り替わっている (`LegacyDbImageStore` 実装)
- 個人情報の取り扱いがセキュリティレビューを通過している
- DR (災害復旧) 手順が文書化されている
- 運用監視 (アラート、メトリクス) が設定されている
- プロンプトのバージョン管理と A/B 検証の仕組みがある

PoC 中のコードはすべて、これらの条件を満たす将来の自分を見据えて書く。