# Schema Overview

本スキーマは **保険申込書の一次チェック** を支えるデータ層。元は PowerPlatform (Dataverse) で構成されていたが、
商用移行と保守性向上を目的に PostgreSQL + Alembic 管理へ再設計した。

- 出典: `sample_table/` 配下の Dataverse 設計書 18 本
- 移行計画: [`migration-plan.md`](./migration-plan.md)
- 詳細対応表: [`migration-from-dataverse.md`](./migration-from-dataverse.md)
- データ辞書: [`data-dictionary.md`](./data-dictionary.md)
- ER 図: [`er-diagram.md`](./er-diagram.md)

---

## 分類とディレクトリ

`schema/tables/` 配下を用途別に 5 サブディレクトリに分けている。

### core — トランザクション業務エンティティ
業務の中核。証券番号単位のエラーリストと、その項目・AI点検・問い合わせ。

| テーブル | 役割 |
|---|---|
| `error_lists` | エラーリスト管理。証券番号・帳票種別単位。二次/三次チェック担当者や処理ステータスも保持 |
| `error_list_items` | 項目単位のデータ。OCR 値、AI 判定、手動補正。BPF 状態を `workflow_state` で保持 |
| `ai_check_results` | AI 点検の実行結果。プロンプト・モデル・トークン消費を記録 |
| `inquiries` | 二次チェック以降の問い合わせ記録 |

### masters — マスタデータ (`masters/*.csv` で管理)
業務ルールの Source of Truth。CSV で管理し、DB へは冪等投入。

| テーブル | 役割 |
|---|---|
| `code_master` | 汎用コード (書類種別・処理ステータス等) |
| `users` | 業務ユーザー (管理者・オペレータ)。Entra ID OID を保持 |
| `error_list_item_master` | エラーリスト項目 (項目名・エラー種別・グループ) |
| `japan_post_address_master` | 日本郵便の公式住所 |
| `aflac_address_master` | Aflac 独自住所 (大字・字の階層、新旧コード) |

### settings — アプリ設定
業務設定。マスタと区別しているのは、これらが参照ではなく **動作ロジックを定義** する性質のため。

| テーブル | 役割 |
|---|---|
| `document_types` | 処理対象書類の種別・プログラム ID |
| `ai_prompts` | AI 点検プロンプト (最大 8 スロット、配列で保持) |

### external_imports — 外部から取り込むデータ
当システムが**書き換えない**前提のデータ。論理キーは `policy_number`。商用時は一部を外部 DB 参照に差し替え。

| テーブル | 役割 |
|---|---|
| `kanji_error_imports` | 漢字エラーリスト (契約者・被保険者・配偶者・子供等の名前情報) |
| `address_error_imports` | 住所エラーリスト |
| `atlas_existing_contracts` | ATLAS 既契約データ (PoC モック) |
| `atlas_registered_contracts` | ATLAS 登録データ (PoC モック) |

### logs — 実行・監査ログ
運用・監査のためのログ。INSERT 主体。

| テーブル | 役割 |
|---|---|
| `system_error_logs` | システム実行時エラー (旧 Power Automate のエラー集約相当) |
| `process_executions` | バッチ・フロー実行の依頼・完了状況 |
| `audit_logs` | 監査ログ (INSERT only、7 年保持、詳細は JSONB) |

---

## データフロー概略

```
外部システム (ATLAS / エラー検出バッチ)
  ↓  バッチ取込
external_imports.*                              ── policy_number 論理結合 ──┐
                                                                         ↓
  ↓ backend が集約                                                         │
error_lists  ─1:N→  error_list_items  ─1:N→  ai_check_results            │
  │                     │                       ↑                          │
  │                     │                       └─── ai_prompts ←── document_types
  │                     └─ field_master_id → error_list_item_master        │
  │                                                                         │
  └─1:N→  inquiries                                                        │
                                                                            │
すべての重要操作 → audit_logs (backend が書き込み)                          │
                                                                            │
マスタ/設定: code_master, users, *_address_master は上記全体から参照 ──────┘
```

---

## 設計のキー原則 (再掲)

`database/CLAUDE.md` §3 の原則を適用:

- 主キーは UUID v4 (`gen_random_uuid()`)
- タイムスタンプは `TIMESTAMPTZ`、日付は `DATE`
- 列挙は **VARCHAR + CHECK**（ENUM 型は使わない）
- 論理削除は使わない (旧 Dataverse `statecode`/`statuscode` は未移行)
- 画像本体は DB に保存しない（本スキーマに画像バイナリカラムは存在しない）
- すべての FK に ON DELETE ポリシーを明示
- 主要クエリを想定したインデックスを設計段階で付与

### 論理削除不使用の理由
Dataverse の `statecode` (0/1) は暗黙の論理削除として使われがちだが、以下の問題がある:
- 「削除済みを除外する」クエリを忘れると業務バグになる
- インデックスと CHECK 制約の恩恵を受けにくい
- 監査ログと二重管理になる

本スキーマでは **DELETE は audit_logs を伴う正式な削除**、ライフサイクル状態は `workflow_state` や `report_status` 等の意味のあるカラムに持たせる。

---

## 商用移行時の注意

`migration-plan.md` §6 のリスクを再掲:

- `atlas_*_contracts` テーブルは PoC モック。商用では backend 側の `ContractStore` 抽象実装に差し替え、このテーブルは削除する
- `*_address_master` は全国データに差し替え（数百万行）。バルクロード戦略を事前に検証
- `audit_logs` は 7 年運用前提でパーティショニングを導入（月次 or 年次）
- `updated_at` の自動更新はトリガーで実装するか、アプリ側で統一するかを決定する（R1）
