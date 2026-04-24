# データ辞書

各テーブル・カラムの**業務意味**を記録する。命名規則は `database/CLAUDE.md` §3 に従う。

> カラム名（スキーマ正本）、論理名（業務名）、意味、備考の4項目で管理。
> Dataverse 旧名との対応は [`migration-from-dataverse.md`](./migration-from-dataverse.md) 参照。

---

## 全テーブル共通カラム

| カラム | 論理名 | 意味 |
|---|---|---|
| `id` | ID | UUID v4。主キー |
| `created_at` | 作成日時 | UTC で記録 |
| `updated_at` | 更新日時 | UTC。トリガーまたはアプリで更新 |

---

## core

### `error_lists` — エラーリスト管理
業務最上位。証券番号 + 帳票種別 1 つが 1 行。

| カラム | 論理名 | 意味 |
|---|---|---|
| `form_code` | エラー管理ID | `F-XXXX` 形式。業務表示用 |
| `display_code` | 内部連番 | 自動採番 |
| `policy_number` | 証券番号 | 業務キー。論理結合の基軸 |
| `batch_number` | バッチ番号 | 取込バッチ識別 |
| `error_type` | エラー種別 | 取込時のエラー種別 |
| `voucher_type` | 帳票種別 | `error_list` / `application` / `intent_confirmation` / `corporate_confirmation` / `bank_transfer_request` |
| `is_degimo` | デジモフラグ | デジモ帳票かどうか |
| `report_status` | 帳票処理ステータス | `ocr_running` / `new` / `corrected` / `inputting` / `filed` |
| `status_updated_at` | ステータス更新日時 | report_status 変更時点 |
| `main_document_url` | メイン書類 | 書類本体の参照 URL |
| `imported_on` | 取込日付 | 業務日付 (DATE) |
| `import_file_name` | 取込ファイル名 | |
| `document_url` | 書類URL | |
| `sub_document_url` | サブ書類 | 複数書類のうち補助 |
| `full_text` | 帳票内容 | 帳票全体の OCR 結果テキスト |
| `document_type_id` | 書類種別 | FK → document_types |
| `contact_person_entra_oid` | 担当者 | Entra ID OID |
| `inquiry_at` / `inquiry_category` / `inquiry_content` | 問い合わせ一次情報 | 詳細は `inquiries` テーブル |
| `processing_status` | 処理ステータス | 業務側で設定する任意文字列 |
| `second_check_*`, `third_check_*` | 二/三次チェック | owner/reviewer (ユーザー名論理結合)、ng (true=NG)、completed_at |
| `app_id` | App ID | |
| `input_token_sum` / `output_token_sum` | 入出力トークン合計 | AI 利用量。アプリで集計 |
| `ai_usage_amount_jpy` | AI 利用金額 | JPY |
| `total_page_count` | 総ページ数 | |

### `error_list_items` — エラーリスト項目
`error_lists` の子。1 項目 = 1 行。

| カラム | 論理名 | 意味 |
|---|---|---|
| `item_code` | 帳票項目ID | `I-XXXX` |
| `error_list_id` | エラーリスト | FK → error_lists (CASCADE) |
| `field_master_id` | 項目マスタ | FK → error_list_item_master |
| `ai_document_code` | AI用書類ID | AI 連携時の識別子 |
| `item_label` | 項目名 | `error_list_item_master.field_name` の冗長コピー可 |
| `item_value` | 項目値 | OCR 結果 |
| `error_flag` | エラーフラグ | true=エラー有 |
| `ai_inspection_status` | AI点検状態 | `pending` / `creating` / `created` / `failed` / `unknown` |
| `confidence_score` | 信頼度 | OCR/AI の信頼度 (文字列) |
| `report_status` | 項目ステータス | `new` / `corrected` / `inputting` / `filed` |
| `first_check_ng`, `first_check_recovery_*` | 一次チェック | 判定と回復値 |
| `second_check_recovery_*` | 二次チェック回復 | |
| `ocr_bbox_{left,top,width,height}` | OCR 座標 | バウンディングボックス |
| `manual_fix_value` | 手動補正値 | |
| `page_count` / `sort_order` | ページ数 / 表示順 | |
| `workflow_state` | ワークフロー状態 | `pending` / `ai_checking` / `manual_review` / `resolved` / `cancelled` (旧 BPF 代替) |
| `workflow_entered_at` | 状態遷移日時 | |
| `workflow_duration_seconds` | 所要秒数 | |

### `ai_check_results` — AI点検結果
| カラム | 論理名 | 意味 |
|---|---|---|
| `inspection_code` | 点検項目ID | `CHK-XXXXXXXXX` |
| `error_list_id`, `error_list_item_id`, `ai_prompt_id`, `document_type_id` | 各種 FK | 結果を辿るための参照 |
| `model_name` | AIモデル名 | Vertex AI のモデル識別 |
| `operation_status` | 実行ステータス | |
| `inspection_details` | 点検内容 | AI に渡した指示 |
| `ai_response` | AIレスポンス | 生レスポンス (個人情報含みうる) |
| `prompt_tokens` / `completion_tokens` / `total_tokens` / `images_count` | 消費量 | |

### `inquiries` — 問い合わせ
`error_lists` 1:N の問い合わせ記録。

---

## masters

### `code_master` — 汎用コード
大分類 (`category_*`) と中分類 (`middle_*`) の組合せで値を表現。

### `users` — 業務ユーザー
| `authority` | `admin` / `operator` |
| `assignment_target` | ラウンドロビン割当対象 |
| `entra_oid` | 認証基盤との紐付け (商用用途) |

### `error_list_item_master` — 項目定義
`error_type` + `field_group` + `attribute` で項目を分類。

### `japan_post_address_master` — 日本郵便住所
`postal_code` (UNIQUE でない) で照合。

### `aflac_address_master` — Aflac 住所
`postal_code` または `address_code` / `new_address_code` で照合。大字・字階層を持つ。

---

## settings

### `document_types` — 書類種別
| `document_code` | `DOC-XXXXXX` 形式の業務 ID |
| `document_category_id` / `ai_config_id` | `code_master` への参照 |

### `ai_prompts` — AIプロンプト
| `prompts TEXT[]` | 最大 8 スロット、index 順に実行 |
| `status` | `active` / `inactive` |
| `use_knowledge` | ナレッジ機能利用 (トークン消費増) |

---

## external_imports

### `kanji_error_imports` — 漢字エラー取込
契約者・被保険者・配偶者・子供 (1〜4)・受取人 (1〜4, 各 `_2` サブ)・介護年金受取人 (1〜2)・指定代理請求人 (1〜2)・除外者の氏名 (漢字/カナ/エラーフラグ) を保持。

### `address_error_imports` — 住所エラー取込
契約者・被保険者の住所カナ・郵便番号とエラーメッセージ。

### `atlas_existing_contracts` / `atlas_registered_contracts` — ATLAS データ
契約者・被保険者の漢字/カナ氏名、生年月日、郵便番号、住所を保持。`policy_number` UNIQUE。PoC モック。

---

## logs

### `system_error_logs` — システムエラー
| `system_type` | `power_automate` / `copilot_studio` / `other` |
| `business_type` | `kanji` / `address` (任意) |
| `error_message` | 旧 `ca_error_massage` の typo を修正 |

### `process_executions` — 処理実行
バッチ・フロー実行の依頼〜完了を記録。

### `audit_logs` — 監査ログ (INSERT only)
| `actor_type` | `user` / `system` / `ai` |
| `event_type` | ドメインイベント名 (例: `error_list.created`) |
| `target_type` + `target_id` | 対象エンティティ |
| `details JSONB` | 構造化詳細。個人情報は含めない |
