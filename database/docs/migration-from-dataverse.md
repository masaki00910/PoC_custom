# Dataverse → PostgreSQL カラム対応表

`sample_table/` 配下の PowerPlatform (Dataverse) テーブル定義を、本リポジトリの PostgreSQL スキーマに
どうマッピングしたかを**カラム単位で**記録する。

- 方針合意: [`migration-plan.md`](./migration-plan.md) §1
- 変換ルール: [`migration-plan.md`](./migration-plan.md) §4

凡例:
- ➡ 列名変更のみ
- 🔄 型変換あり (picklist → CHECK 文字列、datetime → TIMESTAMPTZ など)
- ❌ 未移行 (未使用 / 論理削除 / BPF 固有)
- 🆕 新設カラム
- 📦 配列化 / 統合

---

## 1. ca_document_import → `error_lists`

**テーブル分類**: core

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_document_importid | ➡ | id | UUID | GUID → UUID 互換 | `gen_random_uuid()` |
| 2 | ca_formid | ➡ | form_code | VARCHAR(850) | — | `F-XXXX`, UNIQUE |
| 3 | ca_id | ➡ | display_code | VARCHAR(100) | — | 自動採番 |
| 4 | ca_policy_number | ➡ | policy_number | VARCHAR(100) NOT NULL | — | |
| 5 | ca_batch_number | ➡ | batch_number | VARCHAR(100) NOT NULL | — | |
| 6 | ca_error_type | ➡ | error_type | VARCHAR(100) NOT NULL | — | |
| 7 | ca_vouchertype | 🔄 | voucher_type | VARCHAR(30) + CHECK | picklist → 文字列 | 1→`error_list`, 2→`application`, 3→`intent_confirmation`, 4→`corporate_confirmation`, 5→`bank_transfer_request` |
| 8 | ca_is_degimo | 🔄 | is_degimo | BOOLEAN | bit → bool | |
| 9 | ca_reportstatus | 🔄 | report_status | VARCHAR(20) + CHECK | picklist → 文字列 | 0→`ocr_running`, 1→`new`, 2→`corrected`, 3→`inputting`, 4→`filed` |
| 10 | ca_status_updated_datetime | 🔄 | status_updated_at | TIMESTAMPTZ NOT NULL | UserLocal → UTC | |
| 11 | ca_main_document_url | 🔄 | main_document_url | TEXT | ntext → TEXT | |
| 12 | ca_import_date | 🔄 | imported_on | DATE | DateOnly → DATE | |
| 13 | ca_from_name | ➡ | import_file_name | VARCHAR(100) | — | |
| 14 | ca_document_url | ➡ | document_url | VARCHAR(4000) | — | |
| 15 | ca_sub_document_url | 🔄 | sub_document_url | TEXT | ntext | |
| 16 | ca_fulltext | 🔄 | full_text | TEXT | ntext 1MB | |
| 17 | ca_document_id (lookup) | 🔄 | document_type_id | UUID FK | Lookup → FK | → `document_types.id` |
| 18 | ca_contactperson (lookup systemuser) | 🔄 | contact_person_entra_oid | VARCHAR(255) | systemuser → Entra oid | 方針③A |
| 19 | ca_inquery_datetime | 🔄 | inquiry_at | TIMESTAMPTZ | UserLocal → UTC | typo 修正 (inquery→inquiry) |
| 20 | ca_inquiry_category | ➡ | inquiry_category | VARCHAR(100) | — | |
| 21 | ca_inquiry_content | ➡ | inquiry_content | VARCHAR(100) | — | |
| 22 | ca_processing_status | ➡ | processing_status | VARCHAR(100) | — | |
| 23 | ca_workflow_status | ❌ | — | — | 未使用 | 設計書に「【未使用】」明記 |
| 24 | ca_2nd_check_owner | ➡ | second_check_owner_name | VARCHAR(100) | — | `users.user_name` と論理結合 |
| 25 | ca_2nd_check_reviewer | ➡ | second_check_reviewer_name | VARCHAR(100) | — | |
| 26 | ca_2nd_check_result | 🔄 | second_check_ng | BOOLEAN | bit → bool (true=NG) | 意味を明示 |
| 27 | ca_2nd_check_completed_datetime | 🔄 | second_check_completed_at | TIMESTAMPTZ | — | |
| 28 | ca_3rd_check_owner | ➡ | third_check_owner_name | VARCHAR(100) | — | |
| 29 | ca_3rd_check_reviewer | ➡ | third_check_reviewer_name | VARCHAR(100) | — | |
| 30 | ca_3rd_check_result | 🔄 | third_check_ng | BOOLEAN | — | |
| 31 | ca_3rd_check_completed_datetime | 🔄 | third_check_completed_at | TIMESTAMPTZ | — | |
| 32 | ca_appid | ➡ | app_id | VARCHAR(100) | — | |
| 33 | ca_input_token_sum | 🔄 | input_token_sum | NUMERIC(18,4) | rollup → 通常列 | アプリで更新 |
| 34 | ca_output_token_sum | 🔄 | output_token_sum | NUMERIC(18,4) | rollup → 通常列 | アプリで更新 |
| 35 | ca_ai_usage_amount | 🔄 | ai_usage_amount_jpy | NUMERIC(18,4) | calc → 通常列 | アプリで更新 |
| 36 | cre00_total_page_count | ➡ | total_page_count | INTEGER | — | |
| — | (新設) | 🆕 | created_at | TIMESTAMPTZ | — | 全テーブル共通 |
| — | (新設) | 🆕 | updated_at | TIMESTAMPTZ | — | 全テーブル共通 |

---

## 2. ca_document_item → `error_list_items`

**テーブル分類**: core

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_document_itemid | ➡ | id | UUID | — | |
| 2 | ca_document_item_id | ➡ | item_code | VARCHAR(850) | — | `I-XXXX` |
| 3 | ca_policy_number | ➡ | policy_number | VARCHAR(100) NOT NULL | — | |
| 4 | ca_document_id (lookup) | 🔄 | error_list_id | UUID FK CASCADE | — | → `error_lists.id` |
| 5 | ca_document_id_ai | ➡ | ai_document_code | VARCHAR(200) | — | |
| 6 | ca_document_item | ➡ | item_label | VARCHAR(100) | — | |
| 7 | ca_document_value | 🔄 | item_value | TEXT | ntext | |
| 8 | ca_field_id (lookup) | 🔄 | field_master_id | UUID FK | — | → `error_list_item_master.id` |
| 9 | ca_error_flag | 🔄 | error_flag | BOOLEAN NOT NULL | bit → bool | |
| 10 | ca_ai_inspection_status | 🔄 | ai_inspection_status | VARCHAR(30) + CHECK | picklist synapselinksynapsetablecreationstate → 文字列 | `pending`/`creating`/`created`/`failed`/`unknown` |
| 11 | ca_confidence | ➡ | confidence_score | VARCHAR(100) | — | |
| 12 | ca_reportstatus | 🔄 | report_status | VARCHAR(20) + CHECK | picklist → 文字列 | デフォルト `new` |
| 13 | ca_status_updated_datetime | 🔄 | status_updated_at | TIMESTAMPTZ NOT NULL | — | |
| 14 | ca_processing_status | ➡ | processing_status | VARCHAR(100) | — | |
| 15 | ca_1st_check_result | 🔄 | first_check_ng | BOOLEAN | — | 意味明示 |
| 16 | ca_1st_check_recovery_value | ➡ | first_check_recovery_value | VARCHAR(1000) | — | |
| 17 | ca_1st_check_recovery_reason | ➡ | first_check_recovery_reason | VARCHAR(1000) | — | |
| 18 | ca_2nd_check_recovery_value | ➡ | second_check_recovery_value | VARCHAR(1000) | — | |
| 19 | ca_2nd_check_recovery_reason | ➡ | second_check_recovery_reason | VARCHAR(100) | — | |
| 20 | ca_left | ➡ | ocr_bbox_left | VARCHAR(100) | — | |
| 21 | ca_top | ➡ | ocr_bbox_top | VARCHAR(100) | — | |
| 22 | ca_width | ➡ | ocr_bbox_width | VARCHAR(100) | — | |
| 23 | ca_height | ➡ | ocr_bbox_height | VARCHAR(100) | — | |
| 24 | cre00_manual_fix_value | 🔄 | manual_fix_value | TEXT | ntext | |
| 25 | cre00_page_count | ➡ | page_count | INTEGER | — | |
| 26 | cre00_sort | ➡ | sort_order | INTEGER | — | |
| — | (BPF 由来) | 🆕 | workflow_state | VARCHAR(30) + CHECK | BPF 代替 | 方針②A。`pending/ai_checking/manual_review/resolved/cancelled` |
| — | (BPF 由来) | 🆕 | workflow_entered_at | TIMESTAMPTZ | — | `activestagestartedon` 相当 |
| — | (BPF 由来) | 🆕 | workflow_duration_seconds | INTEGER | — | `bpf_duration` (分→秒) |

---

## 3. ca_ai → `ai_check_results`

**テーブル分類**: core

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_aiid | ➡ | id | UUID | — | |
| 2 | ca_inspection_id | ➡ | inspection_code | VARCHAR(850) | — | `CHK-XXXXXXXXX` |
| 3 | ca_id (lookup) | 🔄 | error_list_id | UUID FK CASCADE | — | → `error_lists.id` |
| 4 | ca_document_id (lookup) | 🔄 | document_type_id | UUID FK | — | → `document_types.id` |
| 5 | ca_document_item_id (lookup) | 🔄 | error_list_item_id | UUID FK CASCADE | — | → `error_list_items.id` |
| 6 | ca_document_item | ➡ | item_label | VARCHAR(100) | — | |
| 7 | ca_prompt_id (lookup) | 🔄 | ai_prompt_id | UUID FK | — | → `ai_prompts.id` |
| 8 | ca_modelname | ➡ | model_name | VARCHAR(100) | — | |
| 9 | ca_operationstatus | ➡ | operation_status | VARCHAR(100) | — | |
| 10 | ca_inspection_details | 🔄 | inspection_details | TEXT | ntext | |
| 11 | ca_ai_inspection_details | 🔄 | ai_response | TEXT | ntext / 名前を意味に合わせて変更 | |
| 12 | ca_prompttokens | ➡ | prompt_tokens | INTEGER | — | |
| 13 | ca_completiontokens | ➡ | completion_tokens | INTEGER | — | |
| 14 | ca_totaltokens | ➡ | total_tokens | INTEGER | — | |
| 15 | ca_imagescount | ➡ | images_count | INTEGER | — | |

---

## 4. ca_inquiry → `inquiries`

**テーブル分類**: core

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_inquiryid | ➡ | id | UUID | — | |
| 2 | ca_formid | ❌ | — | — | 未使用 | 「【使用しない】」明記 |
| 3 | ca_error_list_management_id (lookup) | 🔄 | error_list_id | UUID FK CASCADE | — | → `error_lists.id` |
| 4 | ca_inquiry_datetime | 🔄 | inquired_at | TIMESTAMPTZ | — | |
| 5 | ca_inquiry_category | ➡ | category | VARCHAR(100) | — | テーブル名 inquiries で冗長を解消 |
| 6 | ca_inquiry_content | ➡ | content | VARCHAR(100) | — | 同上 |
| 7 | ca_processing_status | ➡ | processing_status | VARCHAR(100) | — | |
| 8 | ca_status_updated_datetime | 🔄 | status_updated_at | TIMESTAMPTZ | — | |

---

## 5. ca_error_list_item_master → `error_list_item_master`

**テーブル分類**: masters

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_error_list_item_masterid | ➡ | id | UUID | — | |
| 2 | ca_field_id | ➡ | field_code | VARCHAR(850) NOT NULL UNIQUE | — | PrimaryName |
| 3 | ca_field_name | ➡ | field_name | VARCHAR(100) NOT NULL | — | |
| 4 | ca_error_type | ➡ | error_type | VARCHAR(100) NOT NULL | — | |
| 5 | ca_group | ➡ | field_group | VARCHAR(100) | — | `group` は SQL 予約語なので回避 |
| 6 | ca_attribute | ➡ | attribute | VARCHAR(100) | — | |

---

## 6. ca_ai_prompt → `ai_prompts`

**テーブル分類**: settings

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_ai_promptid | ➡ | id | UUID | — | |
| 2 | ca_name (論理名: プロンプトID) | ➡ | prompt_code | VARCHAR(850) NOT NULL UNIQUE | — | Dataverse では論理名と物理名が逆転していたため意味に沿って命名 |
| 3 | ca_id (論理名: プロンプト名前) | ➡ | prompt_name | VARCHAR(100) NOT NULL | — | 同上 |
| 4 | ca_processing_order | ➡ | processing_order | INTEGER NOT NULL | — | |
| 5 | ca_knowledge | 🔄 | use_knowledge | BOOLEAN NOT NULL | bit → bool | |
| 6 | ca_ai | 🔄 | status | VARCHAR(20) + CHECK | picklist documenttemplate_status → 文字列 | `active`/`inactive` |
| 7 | ca_condition | ➡ | condition_field | VARCHAR(100) | — | |
| 8 | ca_documentid (lookup) | 🔄 | document_type_id | UUID FK | — | → `document_types.id` |
| 9 | ca_prompt ... ca_prompt8 | 📦 | prompts | TEXT[] | 8 カラム → 配列 | 最大 8 スロット、CHECK で制限 |
| 17 | ca_sample_data | 🔄 | sample_data | TEXT | ntext | |

---

## 7. ca_japan_post_address_master → `japan_post_address_master`

**テーブル分類**: masters
**Source of Truth**: 日本郵便 KEN_ALL.CSV (`utf_ken_all.csv` / UTF-8 版) — https://www.post.japanpost.jp/zipcode/dl/utf-zip.html
本テーブルは KEN_ALL の **公式 15 カラム** に準拠する。Dataverse 側に存在しなかった #2/#10〜#15 は新規追加、命名は KEN_ALL を正とする。

### Dataverse → 新カラム 対応

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_japan_post_address_masterid | ➡ | id | UUID | — | |
| 2 | ca_postal_code | ➡ | postal_code | VARCHAR(7) NOT NULL | 🔄 型縮小 | KEN_ALL #3 (7桁)。850→7。非 UNIQUE (複数町域) |
| 3 | ca_postal_code_first3 | 🔄 | postal_code_first3 | VARCHAR(3) GENERATED | 自動計算化 | `LEFT(postal_code,3)` の STORED 派生列 |
| 4 | ca_area_code | 🔄 | local_government_code | VARCHAR(5) | リネーム+型変更 | KEN_ALL #1: JIS X0401+X0402 全国地方公共団体コード |
| 5 | ca_prefecture_name | ➡ | prefecture_name | VARCHAR(20) | — | KEN_ALL #7 (漢字) |
| 6 | ca_prefecture_name_kana | ➡ | prefecture_name_kana | VARCHAR(200) | — | KEN_ALL #4 (半角カナ) |
| 7 | ca_municipality_name | ➡ | municipality_name | VARCHAR(100) | — | KEN_ALL #8 |
| 8 | ca_municipality_name_kana | ➡ | municipality_name_kana | VARCHAR(200) | — | KEN_ALL #5 |
| 9 | ca_town_name | 🔄 | town_name | TEXT | 型変更 | KEN_ALL #9 — 括弧内サブ町域列挙で 400+ 文字になる行があるため TEXT |
| 10 | ca_town_name_kana | 🔄 | town_name_kana | TEXT | 型変更 | KEN_ALL #6 — 同上 |

### KEN_ALL 由来で新規追加されたカラム

| KEN_ALL # | 新カラム | 型 | 内容 |
|---|---|---|---|
| #2 | old_postal_code | VARCHAR(5) | (旧)郵便番号 5 桁 |
| #10 | multiple_postal_codes_flag | SMALLINT (0/1) | 一町域が二以上の郵便番号で表される場合 |
| #11 | koaza_banchi_flag | SMALLINT (0/1) | 小字毎に番地が起番されている町域 |
| #12 | chome_flag | SMALLINT (0/1) | 丁目を有する町域 |
| #13 | multiple_towns_flag | SMALLINT (0/1) | 一つの郵便番号で二以上の町域 |
| #14 | update_status | SMALLINT (0/1/2) | 更新の表示 (0=変更なし, 1=変更あり, 2=廃止) |
| #15 | change_reason | SMALLINT (0-6) | 変更理由 (0=変更なし, 1=市政等, 2=住居表示, 3=区画整理, 4=郵便区調整, 5=訂正, 6=廃止) |

これにより `utf_ken_all.csv` を `\COPY` で 15 カラムそのまま投入できる。`postal_code_first3` は派生列のため CSV からは投入しない。

---

## 8. ca_aflac_address_master → `aflac_address_master`

**テーブル分類**: masters

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_aflac_address_masterid | ➡ | id | UUID | — | |
| 2 | ca_id | 🔄 | legacy_id | VARCHAR(850) | NULL/重複許容 | Dataverse PrimaryName。実データに重複(例:`14`)と空欄が混在するため NOT NULL/UNIQUE 制約は外した |
| 3 | ca_address_code | ➡ | address_code | VARCHAR(100) | — | |
| 4 | ca_new_address_code | ➡ | new_address_code | VARCHAR(100) | — | |
| 5 | ca_postal_code | ➡ | postal_code | VARCHAR(100) | — | |
| 6〜9 | 県/市区郡町村 (漢字+カナ) | ➡ | prefecture_name(_kana), municipality_name(_kana) | VARCHAR(100) | — | |
| 10 | ca_oaza_common_name | ➡ | oaza_common_name | VARCHAR(100) | — | 大字・通称名 |
| 11 | ca_oaza_common_name_kana | ➡ | oaza_common_name_kana | VARCHAR(100) | — | |
| 12 | ca_oaza_flag | 🔄 | oaza_flag | BOOLEAN | bit → bool | |
| 13 | ca_aza_cho_name | ➡ | aza_cho_name | VARCHAR(100) | — | |
| 14 | ca_aza_cho_name_kana | ➡ | aza_cho_name_kana | VARCHAR(100) | — | |
| 15 | ca_aza_flag | 🔄 | aza_flag | BOOLEAN | — | |
| 16 | ca_customer_barcode | ➡ | customer_barcode | VARCHAR(100) | — | |
| 17 | ca_effective_year_month | ➡ | effective_year_month | VARCHAR(100) | — | |
| 18 | ca_abolished_year_month | ➡ | abolished_year_month | VARCHAR(100) | — | |
| 19 | ca_search_f | ➡ | search_flag | VARCHAR(100) | — | |

---

## 9. new_a_kanji_error_list → `kanji_error_imports`

**テーブル分類**: external_imports

大量のカラムがあるが、すべて以下の変換ルールを機械的に適用:

- `new_a_` プレフィックス除去 → `policy_number`, `batch_number`, ...
- `group` → `group_name` (SQL 予約語回避)
- 子供 (child1..4), 受取人 (beneficiary_1..4 + \_2 suffix), 介護年金 (ltcpr_beneficiary_1..2), 指定代理請求人 (claim_agent_1..2), 除外者 (excluded_person) はそのまま
- **新設**: `imported_at` (取込日時, TIMESTAMPTZ)
- **新設**: `created_at`, `updated_at` (全テーブル共通)
- 外部キーなし。`policy_number` で論理結合

カラム対応は数が多いため、[`schema/tables/external_imports/kanji_error_imports.sql`](../schema/tables/external_imports/kanji_error_imports.sql) の直接参照を正とする。

---

## 10. new_a_address_error_list → `address_error_imports`

**テーブル分類**: external_imports

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 |
|---|---|---|---|---|---|
| 1 | new_a_address_error_listid | ➡ | id | UUID | — |
| 2 | new_a_policy_number | ➡ | policy_number | VARCHAR(850) NOT NULL | — |
| 3 | new_a_batch_number | ➡ | batch_number | VARCHAR(100) NOT NULL | — |
| 4 | new_a_agency_code | ➡ | agency_code | VARCHAR(100) | — |
| 5 | new_a_document_code | ➡ | document_code | VARCHAR(100) | — |
| 6 | new_a_group_code | ➡ | group_code | VARCHAR(100) | — |
| 7〜12 | 契約者/被保険者 (名/〒/住所) | ➡ | policyholder_name_kana, policyholder_postal_code, policyholder_address_kana, insured_* | VARCHAR | — |
| 13 | new_a_msg | ➡ | message | VARCHAR(850) NOT NULL | — |
| 14 | new_a_sts | ➡ | sts | VARCHAR(100) | — |
| — | (新設) | 🆕 | imported_at | TIMESTAMPTZ | — |

---

## 11. ca_existing_contract_data → `atlas_existing_contracts`

**テーブル分類**: external_imports (PoC モック)

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_existing_contract_dataid | ➡ | id | UUID | — | |
| 2 | ca_policy_number | ➡ | policy_number | VARCHAR(100) NOT NULL UNIQUE | — | 実質検索キー |
| 3 | ca_postal_code (PrimaryName) | ❌ | — | — | — | 「【使用しない】」明記、廃止 |
| 4 | ca_effective_date | 🔄 | effective_date | DATE | DateOnly → DATE | |
| 5〜10 | 契約者 (氏名漢字/カナ/生年月日/〒/住所カナ/漢字) | ➡ | policyholder_name_kanji, policyholder_name_kana, policyholder_birthday (DATE), policyholder_postal_code, policyholder_address_kana, policyholder_address_kanji | — | birthday は DATE | |
| 11〜16 | 被保険者 (同様) | ➡ | insured_name_kanji, insured_name_kana, insured_birthday, insured_postal_code, insured_address_kana, insured_address_kanji | — | — | |
| 17 | ca_sts | ➡ | sts | VARCHAR(100) | — | |

**商用時**: このテーブルは削除し、backend の `ContractStore` 実装 (`LegacyAtlasStore`) に差し替える。

---

## 12. ca_registered_data → `atlas_registered_contracts`

**テーブル分類**: external_imports (PoC モック)

`atlas_existing_contracts` と**同一構造**。`ca_postal_code` (使用しない) は同様に廃止。

---

## 13. ca_error_log → `system_error_logs`

**テーブル分類**: logs

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_error_logid | ➡ | id | UUID | — | |
| 2 | ca_log_id | ➡ | log_code | VARCHAR(850) NOT NULL | — | PrimaryName |
| 3 | ca_system_type | 🔄 | system_type | VARCHAR(20) + CHECK | picklist → 文字列 | 1→`power_automate`, 2→`copilot_studio`, 99→`other` |
| 4 | ca_error_location | ➡ | error_location | VARCHAR(100) NOT NULL | — | |
| 5 | ca_error_massage | 🔄 | error_message | TEXT NOT NULL | **typo 修正** | massage → message |
| 6 | ca_execution_id | ➡ | execution_id | VARCHAR(100) NOT NULL | — | |
| 7 | ca_execution_user | ➡ | execution_user | VARCHAR(100) NOT NULL | — | |
| 8 | ca_input_parameters | 🔄 | input_parameters | TEXT NOT NULL | ntext | |
| 9 | ca_stacktrace | 🔄 | stacktrace | TEXT NOT NULL | ntext | |
| 10 | ca_error_code | ➡ | error_code | VARCHAR(100) | — | |
| 11 | ca_check_name | ➡ | check_name | VARCHAR(100) | — | |
| 12 | ca_business_type | 🔄 | business_type | VARCHAR(20) + CHECK | picklist → 文字列 | 1→`kanji`, 2→`address` |
| 13 | ca_policy_number | ➡ | policy_number | VARCHAR(100) | — | |
| 14 | ca_item | ➡ | item | VARCHAR(100) | — | |

---

## 14. ca_code_management → `code_master`

**テーブル分類**: masters

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_code_managementid | ➡ | id | UUID | — | |
| 2 | ca_display_name | ➡ | display_name | VARCHAR(850) NOT NULL | — | PrimaryName |
| 3 | ca_code_category | ➡ | category_name | VARCHAR(100) | — | 大分類名 |
| 4 | ca_code_value | ➡ | category_code | VARCHAR(100) | — | 大分類コード |
| 5 | ca_middle_code | ➡ | middle_code | INTEGER | — | 中分類コード |
| 6 | ca_middle_code_name | ➡ | middle_name | VARCHAR(1000) | — | 中分類名 |
| 7 | ca_key | ➡ | code_key | VARCHAR(100) | — | |
| 8 | ca_value | ➡ | code_value | VARCHAR(4000) | — | |
| 9 | ca_display_order | ➡ | display_order | VARCHAR(100) | — | 原文が nvarchar のまま踏襲 |
| 10 | ca_contents | 🔄 | contents | TEXT | ntext | |
| 11 | ca_additionalinfo | 🔄 | additional_info | TEXT | ntext | |
| 12 | cre00_flowai | ➡ | flow_ai | VARCHAR(100) | — | |

追加制約: `(category_code, middle_code)` で UNIQUE (部分インデックス、NULL 時は除外)。

---

## 15. ca_document_selection → `document_types`

**テーブル分類**: settings

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_document_selectionid | ➡ | id | UUID | — | |
| 2 | ca_document_id | ➡ | document_code | VARCHAR(850) UNIQUE | — | `DOC-XXXXXX` |
| 3 | ca_name | ➡ | name | VARCHAR(200) NOT NULL | — | |
| 4 | ca_program_id | ➡ | program_code | VARCHAR(100) | — | |
| 5 | ca_program_name | ➡ | program_name | VARCHAR(100) | — | |
| 6 | ca_document (lookup) | 🔄 | document_category_id | UUID FK NOT NULL | — | → `code_master.id` |
| 7 | ca_aiconfig (lookup) | 🔄 | ai_config_id | UUID FK | — | → `code_master.id` |

---

## 16. ca_processmanagement → `process_executions`

**テーブル分類**: logs

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | ca_processmanagementid | ➡ | id | UUID | — | |
| 2 | ca_process_name | ➡ | process_name | VARCHAR(850) NOT NULL | — | PrimaryName |
| 3 | ca_process_status (lookup) | 🔄 | process_status_id | UUID FK | — | → `code_master.id` |
| 4 | ca_processtype (lookup) | 🔄 | process_type_id | UUID FK | — | → `code_master.id` |
| 5 | ca_requester (lookup systemuser) | 🔄 | requester_entra_oid | VARCHAR(255) | systemuser → Entra oid | 方針③A |
| 6 | ca_requestdatetime | 🔄 | requested_at | TIMESTAMPTZ | UserLocal → UTC | |
| 7 | ca_completedatetime | 🔄 | completed_at | TIMESTAMPTZ | — | |
| 8 | ca_description | ➡ | description | VARCHAR(100) | — | |
| 9 | ca_parentflow_runid | ➡ | parent_flow_run_id | VARCHAR(1000) | — | |
| 10 | ca_executionloglink | ➡ | execution_log_url | VARCHAR(2000) | URL | 長さ拡張 |
| 11 | ca_resultmessage | 🔄 | result_message | TEXT | ntext | |

---

## 17. ca_reportprocessingstatus (BPF) → **廃止**

**方針②A**: Dataverse BPF は独自概念。PostgreSQL には対応する概念がなく、backend 側の状態機械 (`CheckRule` の制御フロー) で代替するのが自然。

`error_list_items` に以下を移設:
- `businessprocessflowinstanceid` → (廃止)
- `bpf_name` → (廃止、`error_list_items.item_code` で代替)
- `activestageid` → `workflow_state` (VARCHAR + CHECK、文字列化)
- `activestagestartedon` → `workflow_entered_at`
- `bpf_ca_document_itemid` → (`error_list_items` 自身なので不要)
- `bpf_duration` → `workflow_duration_seconds` (分 → 秒に単位変換)
- `completedon` → `workflow_state = 'resolved'` 時点の `updated_at` で代替
- `traversedpath` → `audit_logs` で過去遷移を追跡

---

## 18. new_a_user_master → `users`

**テーブル分類**: masters

| # | Dataverse 論理名 | → | 新カラム | 型 | 変更 | 備考 |
|---|---|---|---|---|---|---|
| 1 | new_a_user_masterid | ➡ | id | UUID | — | |
| 2 | new_a_user_id | ➡ | user_code | VARCHAR(850) NOT NULL UNIQUE | — | PrimaryName |
| 3 | new_a_user_name | ➡ | user_name | VARCHAR(100) NOT NULL | — | `error_lists.*_owner_name` と論理結合 |
| 4 | new_a_authority | 🔄 | authority | VARCHAR(20) + CHECK | picklist → 文字列 | 1→`admin`, 2→`operator` |
| 5 | ca_flag | 🔄 | assignment_target | BOOLEAN NOT NULL | bit → bool | 名前も意味化 |
| 6 | statecode | ❌ | — | — | 論理削除不使用 | 方針 |
| 7 | statuscode | ❌ | — | — | 論理削除不使用 | 方針 |
| — | (新設) | 🆕 | entra_oid | VARCHAR(255) | — | 商用時の認証キー |

---

## 全体サマリ

| 種別 | 件数 |
|---|---|
| Dataverse テーブル数 | 18 |
| PostgreSQL テーブル数 | 18 (= Dataverse 18 − BPF 1 廃止 + audit_logs 1 新設 + error_list_items が BPF を吸収) |
| カラムレベルの変更点 | 約 30 箇所 (picklist → CHECK、Lookup → FK、datetime → TIMESTAMPTZ 等) |
| 未移行カラム | 約 10 (未使用 / 論理削除 / レガシー PrimaryName) |
| 新設テーブル | `audit_logs` (1) |
| 新設カラム | 全テーブルに `created_at`/`updated_at`、`error_list_items` に `workflow_*` 3 本、各種 `imported_at`、`users.entra_oid` 等 |
