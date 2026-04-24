# CLAUDE.md — Database

このファイルは Claude Code がこのリポジトリで作業するときに必ず最初に読む規約です。
書かれている内容はプロジェクト全体の設計判断であり、**個別タスクの実装中にこれらの方針から逸脱してはいけません**。方針自体を変える必要があると判断した場合は、コード変更の前にその旨を明示して確認を取ってください。

---

## 1. プロジェクト概要

### 目的
保険申込書の一次チェックシステムの **データベース層の Single Source of Truth**。
PostgreSQL のスキーマ定義、マイグレーション、マスタデータ、関連 IaC をすべてこのリポジトリで管理する。

### 位置づけ
- 現在は **PoC フェーズ** だが、**商用利用を見据えた設計・実装**を行う
- DB は業務データの生命線。**このリポジトリの品質が本番運用の安全性を決める**
- スキーマ変更は慎重かつ可逆に。破壊的変更は 2 段階デプロイ前提で設計する

### 全体構成での役割
本システムは **3 リポジトリ構成**:
- `frontend/` — Power Apps PCF (React)
- `backend/` — Python FastAPI
- `database/` — PostgreSQL スキーマ、マイグレーション、マスタデータ、IaC (**このリポジトリ**)

```
[backend (FastAPI)]
       ↓ 参照のみ
[Cloud SQL (PostgreSQL)]  ← このリポジトリが唯一の書き換え権限を持つ
       ├─ スキーマ (applications, check_results, audit_logs, image_references 等)
       └─ マスタデータ (商品コード、疾病コード等)
```

### このリポジトリの責務
- **スキーマ定義** (テーブル、インデックス、制約、ビュー)
- **マイグレーション管理** (Alembic)
- **マスタデータ** (CSV → DB 投入スクリプト、CSV のバージョン管理)
- **ER 図・データ辞書** の維持
- **DB 関連 IaC** (Cloud SQL 構築、バックアップ設定、IAM)
- **本番環境へのマイグレーション適用手順**

### このリポジトリ**ではない**責務
- アプリケーションロジック (`backend/` の責務)
- ORM モデル定義 (`backend/infrastructure/db/models.py` に記述、このリポジトリに追従する)

---

## 2. ディレクトリ構造 (正)

```
database/
├── CLAUDE.md                      ← このファイル
├── README.md
├── Makefile
├── pyproject.toml                 ← Alembic 実行用 (uv で管理)
├── .env.example
├── .gitignore
├── compose.yml                    ← ローカル開発用 PostgreSQL (Podman Compose)
│
├── docs/
│   ├── schema-overview.md         ← スキーマ全体の説明
│   ├── er-diagram.md              ← ER 図 (Mermaid)
│   ├── data-dictionary.md         ← テーブル・カラムの意味辞書
│   ├── migration-guide.md         ← マイグレーション運用手順
│   ├── master-data.md             ← マスタデータの管理方針
│   └── adr/                       ← DB 設計の決定記録
│
├── schema/                        ← 宣言的なスキーマ参考資料 (可読性のため)
│   ├── tables/
│   │   ├── applications.sql       ← 参考用 DDL (実行はしない)
│   │   ├── check_results.sql
│   │   ├── audit_logs.sql
│   │   ├── image_references.sql
│   │   └── masters/
│   │       ├── product_codes.sql
│   │       └── disease_codes.sql
│   ├── views/
│   └── indexes/
│
├── migrations/                    ← Alembic マイグレーション (実行される正)
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_initial_schema.py
│       ├── 0002_add_check_results.py
│       └── ...
│
├── masters/                       ← マスタデータ CSV (Source of Truth)
│   ├── product_codes.csv
│   ├── disease_codes.csv
│   └── README.md                  ← CSV のフォーマット仕様
│
├── seeds/                         ← 開発・テスト用シードデータ
│   ├── dev/
│   └── test/
│
├── scripts/
│   ├── apply_migrations.py        ← マイグレーション実行
│   ├── load_masters.py            ← CSV → DB 投入
│   ├── load_seeds.py              ← シードデータ投入
│   ├── export_schema.py           ← 現行スキーマを SQL としてエクスポート
│   └── check_drift.py             ← 実 DB と migrations の乖離検出
│
├── tests/                         ← スキーマ・マイグレーションのテスト
│   ├── test_migrations.py         ← up/down を通せるか
│   ├── test_masters.py            ← マスタデータの整合性
│   └── test_constraints.py        ← 制約が機能しているか
│
├── infra/                         ← IaC (Terraform)
│   ├── environments/
│   │   ├── dev/
│   │   ├── stg/
│   │   └── prd/
│   └── modules/
│       └── cloud-sql/
│
└── .github/workflows/
    ├── ci.yml                     ← マイグレーション・マスタ検証
    └── deploy.yml                 ← 本番マイグレーション適用
```

**新しいディレクトリを勝手に増やさない**。必要な場合は先に提案して合意を取る。

---

## 3. スキーマ設計の原則

### 基本方針
- **業務用語をテーブル名・カラム名に素直に使う** (例: `applications`, `underwriters`)。技術用語 (`master_data`, `data_table`) で抽象化しすぎない
- **スネークケース、複数形テーブル名**
- **すべてのテーブルに `id` (UUID)、`created_at`、`updated_at` を持たせる**
- **論理削除は安易に使わない**。必要なら `deleted_at` カラムで明示的に
- **外部キー制約を省略しない**。参照整合性は DB で担保
- **NULL 許可の意味を常に考える**。NULL と空文字を使い分ける
- **インデックスは設計時に検討して貼る**。運用でスロークエリが出てから貼るのではなく、設計段階で主要クエリを想定

### ID の扱い
- 主キーは **UUID v4 または ULID** を推奨 (連番は業務上の意味があるものだけ別カラムに)
- 業務 ID (申込番号等) は業務ルールで決まる形式なので、主キーとは別カラムで保持

### タイムゾーン
- すべての timestamp カラムは `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`)
- アプリ側は UTC で扱い、表示時のみ JST に変換
- `DATE` 型は業務日付用 (生年月日等)、それ以外は必ず `TIMESTAMPTZ`

### 列挙型
- ステータス等は PostgreSQL の `ENUM` 型ではなく、**`VARCHAR` + CHECK 制約** で実装
- 理由: ENUM 型は値の追加が ALTER になり、マイグレーションが面倒

```sql
status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'checking', 'passed', 'failed'))
```

### JSONB の使い方
- 構造が確定しない補助データ (AI の生レスポンス等) は JSONB で保持
- **業務クエリで頻繁にフィルタする項目を JSONB に入れない**。通常カラムとして正規化
- JSONB への GIN インデックスが必要なら明示的に設計

### 画像データの特別ルール
- **画像本体を自分たちの DB に格納しない**
- 画像は既存の外部 DB に存在し、参照情報のみ `image_references` テーブルで管理
- `image_references` テーブルのカラム例: `id`, `application_id`, `external_image_id` (既存DBのキー), `document_type`, `registered_at`
- **BYTEA カラムや Large Object を画像本体の格納目的で追加してはいけない**

### 監査ログテーブル
- `audit_logs` テーブルは **INSERT only**。UPDATE/DELETE は禁止
- 構造例:
  ```sql
  CREATE TABLE audit_logs (
      id UUID PRIMARY KEY,
      occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      actor_type VARCHAR(20) NOT NULL,    -- 'user' | 'system' | 'ai'
      actor_id VARCHAR(255),               -- Entra ID oid 等
      event_type VARCHAR(50) NOT NULL,    -- 'application.created' 等
      target_type VARCHAR(50),
      target_id VARCHAR(255),
      details JSONB NOT NULL               -- 個人情報は含めない
  );
  ```
- 保存期間 7 年を想定し、パーティショニングを視野に入れる (PoC では未実装でも可、設計書には記載)

---

## 4. マイグレーション運用

### ツール
- **Alembic** を使用
- `migrations/versions/` 配下に番号プレフィックス付きで命名 (`0001_*.py`, `0002_*.py`)
- autogenerate を使う場合も、**必ず手で内容を確認・修正**してからコミット

### マイグレーション作成の鉄則

1. **1 マイグレーション = 1 論理変更**。複数の変更を 1 ファイルに混ぜない
2. **必ず `downgrade()` を実装**。戻せない変更は原則として行わない
3. **データ移行を含むマイグレーションは超慎重に**。本番データ量でのテストを事前に
4. **破壊的変更は 2 段階デプロイ**:
   - Phase 1: 新カラム追加、新旧両対応コードをデプロイ
   - Phase 2: 旧カラム削除
5. **`down_revision` を改ざんしない**。過去のマイグレーションを修正したくなったら新しいマイグレーションで対応
6. **一度 main にマージされたマイグレーションは書き換えない**。修正は新しいマイグレーションで

### マイグレーション命名規則
`{番号}_{動詞}_{対象}.py` の形式:
- `0005_add_severity_to_check_results.py`
- `0006_create_audit_logs_partition.py`
- `0007_rename_user_id_to_actor_id.py`

### 適用手順
```bash
# ローカル
make migrate-up           # 最新まで適用
make migrate-down         # 1 つ戻す
make migrate-status       # 現在のバージョン確認
make migrate-create name=add_xxx_to_yyy  # 新規作成

# dev 環境
make deploy-migrations-dev

# stg/prd 環境
# → GitHub Actions の手動承認 workflow から実行
```

### 本番適用前チェックリスト
- [ ] ローカルで up / down が両方通る
- [ ] dev 環境で適用済み、動作確認済み
- [ ] stg 環境で本番相当のデータ量で適用・動作確認済み
- [ ] ロールバック手順が文書化されている
- [ ] 破壊的変更の場合、バックエンドの対応コードが先行デプロイされている
- [ ] メンテナンスウィンドウが必要か判断済み

---

## 5. マスタデータ管理

### 基本方針
- マスタデータの **Source of Truth は `masters/*.csv`**
- CSV を Git 管理することで、業務ルール変更の履歴が追える
- DB への投入は `scripts/load_masters.py` で**冪等に**実施

### CSV のフォーマット規約
- 文字コードは UTF-8 (BOM なし)
- 改行コードは LF
- 先頭行はヘッダ必須
- カラム区切りはカンマ、値にカンマを含む場合はダブルクォート囲み
- 各 CSV ファイルにバージョン情報をメタデータとして管理 (別ファイル or コミットハッシュで代替)

### 更新手順
1. `masters/*.csv` を編集
2. PR を作成 → 業務担当者のレビュー必須
3. マージ後、各環境に `load_masters.py` で反映
4. 変更内容を監査ログに記録

### 投入スクリプトの要件
- **冪等性**: 何度実行しても同じ結果になる (UPSERT または TRUNCATE + INSERT)
- **トランザクション**: 全行成功 or 全行ロールバック
- **バリデーション**: CSV フォーマット、必須項目、型、参照整合性を事前チェック
- **差分レポート**: 実行前に「何件追加・更新・削除されるか」を出力

### マスタデータの変更と監査
- マスタデータ変更は**業務ルールの変更そのもの**
- 誰が・いつ・何を変更したかを `audit_logs` に記録
- 本番反映は承認フローを通す

---

## 6. 環境と切り替え

### 環境の種類
- `local`: 開発者 PC, Podman Compose の PostgreSQL
- `dev`: GCP dev プロジェクトの Cloud SQL
- `stg`: GCP stg プロジェクトの Cloud SQL
- `prd`: GCP prd プロジェクトの Cloud SQL

### 接続情報の管理
- 本番・stg の接続情報は Secret Manager に格納
- ローカル開発は `.env` (コミット禁止)
- `.env.example` に必要な環境変数を列挙

### ローカル開発
```bash
make db-up       # podman-compose で PostgreSQL 起動
make migrate-up  # マイグレーション適用
make load-masters  # マスタデータ投入
make load-seeds    # 開発用シード投入
```

backend リポジトリから参照する場合、同じ Podman ネットワークに接続するか、`.env` で `localhost:5432` を指定。Rootless Podman では `127.0.0.1` からの接続になる点に注意。

---

## 7. セキュリティと個人情報の扱い

### ハードルール
- **DB 接続情報 (特にパスワード) をコミットしない**
- **本番データをローカルに持ってこない**。検証は匿名化済みデータで
- **個人情報を含むサンプルデータをコミットしない**。`seeds/` 配下は完全ダミーデータのみ
- **DB スナップショット・ダンプファイルをリポジトリに置かない**
- **ログに個人情報を出力しない** (マイグレーションスクリプト内も含む)

### アクセス制御
- Cloud SQL への接続は Cloud Run のサービスアカウントからのみ許可
- DB ユーザーは用途別に分離:
  - `app_user`: アプリからの接続用 (SELECT/INSERT/UPDATE/DELETE のみ、DDL 不可)
  - `migration_user`: マイグレーション用 (DDL 権限)
  - `readonly_user`: 分析・デバッグ用 (SELECT のみ)
- 人間の直接接続は原則禁止。必要な場合は IAM Database Authentication 経由

### 暗号化・バックアップ
- Cloud SQL の保存時暗号化、SSL 強制を有効化
- 自動バックアップ: 毎日、7 日間保持
- PITR (Point-in-Time Recovery): 有効化
- 本番バックアップからの復旧手順を半年に 1 回訓練

---

## 8. テスト方針

### 基本原則
- **マイグレーションはテストする**。「migrate-up して migrate-down して migrate-up」が通ることを CI で確認
- マスタデータは投入スクリプトのテストと、データ自体の整合性テストを分ける

### テストの種類
- **マイグレーションテスト** (`tests/test_migrations.py`):
  - 全マイグレーションの up が通る
  - 全マイグレーションの down が通る
  - up → down → up が通る
- **マスタデータテスト** (`tests/test_masters.py`):
  - CSV フォーマットが正しい
  - 必須項目が埋まっている
  - 他マスタへの参照が解決する
  - 重複キーがない
- **制約テスト** (`tests/test_constraints.py`):
  - 主要制約が機能している (NOT NULL, FK, CHECK)
  - インデックスが期待通り作られている

### テスト環境
- Podman Compose で立ち上げた PostgreSQL に対して実行
- CI (GitHub Actions) でも同様に PostgreSQL サービスコンテナを使う (Podman)
- 本番データには絶対にテストを走らせない

---

## 9. リポジトリ間連携

### backend リポジトリとの関係
- **このリポジトリがスキーマの Source of Truth**
- backend の ORM モデル (`infrastructure/db/models.py`) は、このリポジトリのスキーマに**追従する側**
- 変更順序の鉄則:
  1. `database/` リポジトリでスキーマ変更 PR 作成 → レビュー
  2. マイグレーション適用 (dev → stg → prd の順)
  3. `backend/` リポジトリで ORM モデルを更新
  4. backend をデプロイ

- 逆順 (backend の ORM 変更が先) は禁止

### 破壊的変更時のプロトコル
カラム削除やリネームを行う場合、以下の 3 フェーズを踏む:

1. **Phase 1 (このリポジトリ)**: 新カラム追加 or 新旧両方用意
2. **Phase 2 (backend リポジトリ)**: 新旧両対応コードをデプロイ、データ移行
3. **Phase 3 (このリポジトリ)**: 旧カラム削除

各フェーズの間に最低 1 リリースサイクル空ける。

### frontend リポジトリとの関係
- 直接の連携はない (frontend は backend 経由でのみ DB に触れる)
- ただし**スキーマ変更が API 変更を引き起こす場合、frontend にも影響する**ため、影響範囲を PR に明記

---

## 10. Claude Code への作業指示

### 作業前に必ず確認すること
1. このファイル (`CLAUDE.md`) 全体を読む
2. 関連する `docs/` 配下のドキュメントを確認 (特に `schema-overview.md`, `data-dictionary.md`)
3. 既存のマイグレーション履歴を確認
4. タスクが不明瞭な場合は実装前に質問する

### 作業中の原則
- **過去のマイグレーションファイルを書き換えない**
- **downgrade を必ず実装する**
- **勝手にスキーマ設計を変えない**。変更は必ずレビュー対象
- **マスタデータ CSV を編集するときは、件数・差分をコミットメッセージに明記**
- **データ移行スクリプトは必ず dry-run モードを用意**

### コード生成時のチェックリスト
新しいマイグレーションを書いたら、以下を自己チェック:

- [ ] upgrade / downgrade が両方実装されている
- [ ] 破壊的変更なら 2 段階デプロイを想定している
- [ ] ローカルで up → down → up が通った
- [ ] 必要な制約 (NOT NULL, FK, CHECK) が漏れていない
- [ ] タイムスタンプは TIMESTAMPTZ になっている
- [ ] インデックスの必要性を検討した
- [ ] 命名規則に従っている (スネークケース、複数形)
- [ ] 個人情報をデフォルト値やサンプルに含めていない
- [ ] 対応する ER 図・データ辞書を更新した

### 禁止事項まとめ
- 過去のマイグレーションファイルを書き換えない
- `down_revision` を改ざんしない
- downgrade を省略しない
- 画像本体を格納するカラム (BYTEA 等) を追加しない
- 個人情報を含むサンプル・テストデータをコミットしない
- 本番データをローカルに持ってこない
- DB 接続情報をコミットしない
- スキーマ変更を backend より後回しにしない (必ず DB が先)
- 新しいディレクトリ構造を勝手に作らない
- 設計方針を無断で変更しない

### 推奨事項まとめ
- 不明点は先に質問する
- 1 マイグレーション = 1 論理変更にする
- ER 図・データ辞書をコードと同時に更新する
- マスタデータ変更は業務担当者のレビューを必ず通す
- PoC でも商用品質を意識する

---

## 11. よく使うコマンド

```bash
# 初期セットアップ
make setup                # uv sync

# ローカル DB (Podman Compose)
make db-up                # podman-compose up
make db-down              # podman-compose down
make db-reset             # DB を落として作り直し

# マイグレーション
make migrate-up           # 最新まで適用
make migrate-down         # 1 つ戻す
make migrate-status       # 現在のバージョン
make migrate-create name=add_xxx  # 新規作成 (autogenerate)

# マスタデータ
make load-masters         # CSV → DB 投入
make validate-masters     # CSV の妥当性チェック

# シードデータ
make load-seeds           # 開発用データ投入

# テスト
make test                 # 全テスト
make test-migrations      # マイグレーションテストのみ

# 環境デプロイ
make deploy-migrations-dev   # dev 環境適用
make deploy-masters-dev      # dev 環境マスタ反映
# stg, prd は GitHub Actions 経由
```

詳細は `Makefile` と `README.md` を参照。

---

## 12. 参考: PoC から商用への昇格基準

このリポジトリが商用品質と判断できる条件:

- 全マイグレーションに up/down 両方が実装されている
- CI で migration up/down/up のラウンドトリップテストが通る
- マスタデータの投入スクリプトが冪等
- マスタデータ CSV に検証テストがある
- 監査ログテーブルがパーティション運用可能な状態
- バックアップ・PITR が本番で有効
- リストア訓練が実施済み
- DBA またはそれに準ずるレビュー体制が確立している
- スキーマの ER 図・データ辞書が最新に保たれている
- 個人情報を含むカラムが明確に識別・管理されている

PoC 中のコードはすべて、これらの条件を満たす将来の自分を見据えて書く。