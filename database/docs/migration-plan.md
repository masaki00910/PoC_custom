# Dataverse → PostgreSQL 移行計画

> このファイルは `sample_table/` (PowerPlatform / Dataverse の設計書) を
> `database/` リポジトリの PostgreSQL スキーマに移行するための**実行計画兼進捗管理**。
> 作業中は随時更新し、完了時には最終ステータスを残す。

**作成日**: 2026-04-24
**最終更新**: 2026-04-24 (T1〜T5 完了)

---

## 1. 合意済み方針

`CLAUDE.md` (database / backend) の原則と照合して、以下で合意済み。

| # | 観点 | 方針 | 根拠 |
|---|---|---|---|
| ① | 命名 | **業務用語ベースで全面リネーム**（`ca_` / `new_a_` 除去、業務意味に沿ったテーブル名） | database/CLAUDE.md §3「業務用語をテーブル名・カラム名に素直に使う」 |
| ② | BPF (`ca_reportprocessingstatus`) | **DB層から削除**し、`error_list_items.workflow_state` (VARCHAR+CHECK) で代替 | backend/CLAUDE.md §3「Power Automate の1フロー → CheckRule クラス」 |
| ③ | `systemuser` 参照 | **`{role}_entra_oid VARCHAR(255)`** に置換、FK は張らない | backend/CLAUDE.md §6「ユーザー識別は Entra ID の oid」 |
| ④ | ATLAS既契約/登録 (table_11, 12) | **PoC はDB内モック** (`seeds/dev/`)、商用時は backend の `ContractStore` 抽象へ差し替え前提で DDL 作成 | backend/CLAUDE.md §8 の MockImageStore と同様の構造 |
| ⑤ | ディレクトリ構成 | schema/tables 配下を `core/ / masters/ / settings/ / external_imports/ / logs/` に分類、docs に `migration-from-dataverse.md` を追加 | CLAUDE.md §2 の正構造を尊重しつつ可読性のため細分化 (承認済み) |
| 追加 | `audit_logs` | 設計書に無くても必ず作成 (INSERT only、details JSONB) | database/CLAUDE.md §3 で必須 |

---

## 2. テーブル移行対応表（概略）

詳細カラム対応は `migration-from-dataverse.md` 参照。

| # | Dataverse 論理名 | 新テーブル名 | 分類 | 備考 |
|---|---|---|---|---|
| 01 | ca_document_import | `error_lists` | core | 業務のトップレベル。エラーリスト管理 |
| 02 | ca_document_item | `error_list_items` | core | 項目単位。`workflow_state` で BPF 代替 |
| 03 | ca_ai | `ai_check_results` | core | AI 点検結果 |
| 04 | ca_inquiry | `inquiries` | core | 問い合わせ |
| 05 | ca_error_list_item_master | `error_list_item_master` | masters | 項目定義マスタ |
| 06 | ca_ai_prompt | `ai_prompts` | settings | プロンプト。`prompt1..8` を配列正規化 |
| 07 | ca_japan_post_address_master | `japan_post_address_master` | masters | 日本郵便住所 |
| 08 | ca_aflac_address_master | `aflac_address_master` | masters | Aflac 住所 |
| 09 | new_a_kanji_error_list | `kanji_error_imports` | external_imports | 漢字エラー取込 |
| 10 | new_a_address_error_list | `address_error_imports` | external_imports | 住所エラー取込 |
| 11 | ca_existing_contract_data | `atlas_existing_contracts` | external_imports | ATLAS 既契約 (モック) |
| 12 | ca_registered_data | `atlas_registered_contracts` | external_imports | ATLAS 登録済 (モック) |
| 13 | ca_error_log | `system_error_logs` | logs | システムエラー。typo (`massage`) 修正 |
| 14 | ca_code_management | `code_master` | masters | コード管理 |
| 15 | ca_document_selection | `document_types` | settings | 書類種別 |
| 16 | ca_processmanagement | `process_executions` | logs | 処理実行ログ |
| 17 | ca_reportprocessingstatus | **廃止** | — | BPF。`error_list_items.workflow_state` で代替 |
| 18 | new_a_user_master | `users` | masters | 業務ユーザー |
| +  | (新設) | `audit_logs` | logs | 監査ログ (CLAUDE.md §3 必須) |

実テーブル数: **17** (Dataverse 18 → BPF 削除 +1 追加 = 18、内 1 は `error_list_items` に畳み込み)

---

## 3. 実行計画（タスクとDoD）

| # | タスク | 成果物 | DoD | ステータス |
|---|---|---|---|---|
| T0 | 方針合意 | 本ファイル §1 | 5 項目すべて合意 | ✅ 完了 |
| T1 | 参考DDL作成 | `schema/tables/{category}/*.sql` 18 本 | 全テーブルの DDL、CHECK/FK/INDEX 含む | ✅ 完了 |
| T2 | 初期マイグレーション | `migrations/versions/0001_initial_schema.py` | upgrade/downgrade 両実装、依存順序 | ✅ 完了 |
| T3 | マスタ CSV テンプレ | `masters/*.csv` 7本 + `masters/README.md` | ヘッダ行のみの空 CSV + フォーマット仕様 | ✅ 完了 |
| T4 | ER 図 + データ辞書 + 対応表 | `docs/er-diagram.md` / `docs/data-dictionary.md` / `docs/migration-from-dataverse.md` | 全 18 テーブルを網羅、Dataverse ↔ 新スキーマの双方向対応表 | ✅ 完了 |
| T5 | schema-overview.md | `docs/schema-overview.md` | 各分類の責務とテーブル一覧 | ✅ 完了 |

進捗は本ファイルの「ステータス」列を都度更新する。

---

## 4. 重要な設計変換ルール（全テーブル共通）

参考DDL / マイグレーション作成時は以下を**必ず適用**する。

### 4.1 カラム変換
| Dataverse | PostgreSQL | 備考 |
|---|---|---|
| `uniqueidentifier` (PK) | `UUID PRIMARY KEY DEFAULT gen_random_uuid()` | `pgcrypto` 前提 |
| Lookup (FK) | `UUID REFERENCES {parent}(id) ON DELETE RESTRICT` | `{col}_id` 命名 |
| `nvarchar(n)` | `VARCHAR(n)` | 850 文字は `VARCHAR(850)` のまま |
| `ntext` | `TEXT` | PostgreSQL では `TEXT` 一択 |
| `datetime` (UserLocal) | `TIMESTAMPTZ` | UTC で保持、表示時に JST 変換 |
| `datetime` (DateOnly) | `DATE` | 業務日付 |
| `bit` | `BOOLEAN` | 1/0 → true/false |
| `int` | `INTEGER` | |
| `decimal` | `NUMERIC(18,4)` | 金額・トークン用 |
| `picklist` (数値コード) | `VARCHAR(n) + CHECK IN (...)` | 意味のあるスネークケース文字列に変換 |
| `state` / `statuscode` | **削除** | 論理削除不使用 (CLAUDE.md §3) |

### 4.2 全テーブル共通カラム
```sql
id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
```
- `updated_at` はアプリ or トリガーで更新。CLAUDE.md には明記ないが、トリガー実装は T1 完了後に別タスクで検討。
- Dataverse の GUID 値を引き継ぐ場合は `id` にそのまま流し込めば UUID 型互換。

### 4.3 命名規則
- テーブル名: スネークケース + **複数形** (`error_lists`, `ai_prompts`)
- マスタ / 辞書系: 原則として**単数形** 扱いを許容 (`code_master`, `error_list_item_master`) — 慣用に合わせる
- カラム名: スネークケース。日本語論理名は data-dictionary に記載
- 参照カラム: `{対象}_id` (例: `document_type_id`)
- 日時: `{動詞過去形}_at` (`imported_at`, `completed_at`) または `{名詞}_datetime` を避け `_at` に統一

### 4.4 picklist → 文字列変換例
```
ca_vouchertype: 1 → 'error_list', 2 → 'application', 3 → 'intent_confirmation',
                 4 → 'corporate_confirmation', 5 → 'bank_transfer_request'
ca_reportstatus: 0 → 'ocr_running', 1 → 'new', 2 → 'corrected', 3 → 'inputting', 4 → 'filed'
ca_system_type: 1 → 'power_automate', 2 → 'copilot_studio', 99 → 'other'
ca_business_type: 1 → 'kanji', 2 → 'address'
new_a_authority: 1 → 'admin', 2 → 'operator'
```

### 4.5 廃止・統合するフィールド
| 旧 | 新 | 理由 |
|---|---|---|
| `statecode` / `statuscode` | 削除 | 論理削除不使用 |
| `ca_postal_code` (atlas_* の PrimaryName) | **削除** | 設計書に「【使用しない】」と明記 |
| `ca_formid`, `ca_id` (自動採番) | `form_code` / `display_code` として維持 | 業務 ID は別カラムで保持 (CLAUDE.md §3) |
| BPF `ca_reportprocessingstatus` | `error_list_items.workflow_state` + `workflow_entered_at` | ②の方針 |

---

## 5. 監査ログ (`audit_logs`) 設計

CLAUDE.md §3 の例に準拠:
```
id UUID PK, occurred_at TIMESTAMPTZ, actor_type, actor_id,
event_type, target_type, target_id, details JSONB
```
INSERT only、7 年保持想定。書き込みは backend 側の責務（このリポでは DDL のみ提供）。

---

## 6. リスク・未決事項

| # | 項目 | 現状 | 対応 |
|---|---|---|---|
| R1 | `updated_at` 自動更新 (トリガー vs アプリ) | 未決 | T1 完了後に別タスクで議論。PoC 中はアプリ側で更新想定 |
| R2 | `atlas_*` モックの商用削除時の影響範囲 | 現時点では backend 接続先抽象化で対応 | backend の `ContractStore` IF 実装時に再確認 |
| R3 | 外部取込データのリロード戦略 (TRUNCATE + INSERT / UPSERT) | 未決 | T3 で マスタと合わせて方針決定 |
| R4 | `ai_prompts` の `prompt1..8` をどう正規化するか | 配列 `prompts TEXT[]` vs 別テーブル `ai_prompt_versions` | 現案: `TEXT[]` で保持。業務上の順序保証があるため |
| R5 | 郵政/Aflac 住所マスタの件数規模 | 不明（全国なら数百万行） | CSV 投入戦略を T3 で決定。COPY 必須の可能性 |

---

## 7. 完了条件

- [x] T1〜T5 すべてのタスクが完了
- [x] `docs/migration-from-dataverse.md` にカラムレベルの対応表がある
- [x] すべての DDL に FK/CHECK/INDEX が適切に設定されている
- [x] 初期マイグレーションで up → down → up が (ローカル DB なしでも) 論理的に通る形になっている
- [x] 各ファイルが CLAUDE.md の禁止事項に抵触していない

---

## 8. 次にやるべきこと（本計画の範囲外）

今回の作業は「スキーマ定義の移行」まで。以下は後続タスク:

| # | タスク | 担当 | 備考 |
|---|---|---|---|
| N1 | `scripts/load_masters.py` 実装 | database リポ | 冪等な CSV 投入。dry-run 必須 |
| N2 | `scripts/apply_migrations.py` 実装 | database リポ | Alembic 薄ラッパ |
| N3 | `updated_at` 自動更新トリガー | database リポ | R1 の結論次第 |
| N4 | `audit_logs` の UPDATE/DELETE 禁止トリガー | database リポ | RULE or TRIGGER |
| N5 | Podman Compose での PostgreSQL 立ち上げ (`compose.yml`) | database リポ | CLAUDE.md §10 準拠 |
| N6 | backend 側の ORM モデル (`infrastructure/db/models.py`) 作成 | backend リポ | 本スキーマに追従 |
| N7 | backend 側のリポジトリ層 (`infrastructure/db/repositories/`) 実装 | backend リポ | ドメインインターフェース準拠 |
| N8 | 住所マスタ投入 (UAT サブセット) | 業務担当 | CSV への実データ投入 |
| N9 | マイグレーションテスト (up/down/up) | database リポ | `tests/test_migrations.py` |
