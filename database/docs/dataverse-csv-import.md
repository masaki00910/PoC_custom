# Dataverse CSV → PostgreSQL カラムマッピング

`sample_data/` 配下に置かれた Dataverse 実エクスポート CSV を、本リポジトリのスキーマへ投入する際の **カラム対応表**。

- **作成日**: 2026-04-27
- **CSV ソース**: `sample_data/*.csv` (PowerPlatform Dataverse から直接エクスポート)
- **対象 DB**: PostgreSQL (このリポジトリの schema)
- **ロード方式**: ステージングテーブル方式 (CSV → `staging_*` へ \COPY → INSERT INTO target SELECT で型変換)

---

## 共通ルール

### 全 CSV で **無視するカラム** (Dataverse 内部メタデータ)
これらは投入時に `staging_*` には取り込むが、target テーブルへは **転記しない**。

| 旧カラム | 内容 |
|---|---|
| `utcconversiontimezonecode` | ユーザータイムゾーン |
| `importsequencenumber` | Dataverse 取込順序 |
| `timezoneruleversionnumber` | TZ ルールバージョン |
| `versionnumber` | 楽観排他用バージョン |
| `statecode` | Dataverse 論理削除 (本スキーマでは使わない、CLAUDE.md §3) |
| `statuscode` | 同上 |
| `owningbusinessunit` | Dataverse 所有 BU (本スキーマで FK を張らない) |
| `processid` | フロー実行ID (該当業務ロジックがバックエンド側へ移行) |

### 共通の値変換

| 種別 | 旧値 (Dataverse) | 新値 (PostgreSQL) |
|---|---|---|
| Boolean | `True` / `False` (大文字) | `TRUE` / `FALSE` |
| 日時 | `2026-04-13 04:10:45.0000000` (微秒 7 桁) | `TIMESTAMPTZ`. 末尾の余剰 0 はキャストで除去 |
| 日付 | `2026-03-06 01:40:04.0000000` (実は日付フィールド) | `DATE`(時刻部分は捨てる) |
| 空文字 | `""` | `NULL` |
| GUID | `f9417568-fd18-f111-...` | `UUID`(そのまま流用、Dataverse の id を保持) |

### picklist (数値コード) → 意味付き文字列

`migration-from-dataverse.md` §4.4 に準拠。本ドキュメントでは抜粋を再掲。

| 旧フィールド | 旧値 | 新値 (CHECK 制約付き文字列) |
|---|---|---|
| `ca_vouchertype` | 1 / 2 / 3 / 4 / 5 | `error_list` / `application` / `intent_confirmation` / `corporate_confirmation` / `bank_transfer_request` |
| `ca_reportstatus` | 0 / 1 / 2 / 3 / 4 | `ocr_running` / `new` / `corrected` / `inputting` / `filed` |
| `ca_ai_inspection_status` | 0..4 (synapselinksynapsetablecreationstate) | `pending` / `creating` / `created` / `failed` / `unknown` |
| `ca_ai` (status) | 0 / 1 | `inactive` / `active` |
| `ca_authority` | 1 / 2 | `admin` / `operator` |

---

## 1. `ca_aflac_address_masters.csv` → `aflac_address_master`

**行数**: 66 件 + ヘッダ
**FK**: なし

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_aflac_address_masterid` | ➡ | `id` | UUID | そのまま (Dataverse GUID 流用) |
| 2 | `ca_id` | ➡ | `legacy_id` | VARCHAR(850) | そのまま |
| 3 | `ca_address_code` | ➡ | `address_code` | VARCHAR(100) | そのまま |
| 4 | `ca_new_address_code` | ➡ | `new_address_code` | VARCHAR(100) | そのまま |
| 5 | `ca_postal_code` | ➡ | `postal_code` | VARCHAR(100) | そのまま |
| 6 | `ca_prefecture_name` | ➡ | `prefecture_name` | VARCHAR(100) | そのまま |
| 7 | `ca_prefecture_name_kana` | ➡ | `prefecture_name_kana` | VARCHAR(100) | そのまま |
| 8 | `ca_municipality_name` | ➡ | `municipality_name` | VARCHAR(100) | そのまま |
| 9 | `ca_municipality_name_kana` | ➡ | `municipality_name_kana` | VARCHAR(100) | そのまま |
| 10 | `ca_oaza_common_name` | ➡ | `oaza_common_name` | VARCHAR(100) | そのまま |
| 11 | `ca_oaza_common_name_kana` | ➡ | `oaza_common_name_kana` | VARCHAR(100) | そのまま |
| 12 | `ca_oaza_flag` | 🔄 | `oaza_flag` | BOOLEAN | `True/False` → `TRUE/FALSE` |
| 13 | `ca_aza_cho_name` | ➡ | `aza_cho_name` | VARCHAR(100) | そのまま |
| 14 | `ca_aza_cho_name_kana` | ➡ | `aza_cho_name_kana` | VARCHAR(100) | そのまま |
| 15 | `ca_aza_flag` | 🔄 | `aza_flag` | BOOLEAN | 同上 |
| 16 | `ca_customer_barcode` | ➡ | `customer_barcode` | VARCHAR(100) | そのまま |
| 17 | `ca_effective_year_month` | ➡ | `effective_year_month` | VARCHAR(100) | そのまま (YYYYMM 文字列) |
| 18 | `ca_abolished_year_month` | ➡ | `abolished_year_month` | VARCHAR(100) | そのまま |
| 19 | `ca_search_f` | 🔄 | `search_flag` | VARCHAR(100) | カラム名のみ変更 (`_f` → `_flag`) |
| メタ | `utcconversiontimezonecode` 等 | ❌ | — | — | 無視 |

---

## 2. `ca_ai_prompts.csv` → `ai_prompts`

**行数**: 5300 行(カラム内改行を含むため、論理レコード数は約 30〜50)
**FK**: `document_type_id` → `document_types(id)` (今回の取込では document_types に対応データが無いため **NULL に設定**)

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_ai_promptid` | ➡ | `id` | UUID | そのまま |
| 2 | `ca_name` | ➡ | `prompt_code` | VARCHAR(850) | そのまま (PrimaryName) |
| 3 | `ca_id` | ➡ | `prompt_name` | VARCHAR(100) | そのまま |
| 4 | `ca_processing_order` | ➡ | `processing_order` | INTEGER | INT キャスト |
| 5 | `ca_knowledge` | 🔄 | `use_knowledge` | BOOLEAN | `True/False` → `TRUE/FALSE` |
| 6 | `ca_ai` | 🔄 | `status` | VARCHAR(20) | picklist (0/1) → `inactive`/`active` |
| 7 | `ca_condition` | 🔄 | `condition_field` | VARCHAR(100) | カラム名変更 |
| 8 | `ca_documentid` | 🔄 | `document_type_id` | UUID | **NULL 固定**(参照先 document_types が空のため) |
| 9 | `ca_prompt`, `ca_prompt2`..`ca_prompt8` | 🔄 | `prompts` | TEXT[] | **空でないものだけを順序保ったまま配列化** |
| 10 | `ca_sample_data` | ➡ | `sample_data` | TEXT | そのまま |
| メタ | `utcconversiontimezonecode` 等 | ❌ | — | — | 無視 |

注: 旧 `ca_prompt` は配列の **先頭(index 1, PostgreSQL は 1-origin)**、`ca_prompt2`〜`ca_prompt8` がそれ以降。空欄はスキップして詰める。

---

## 2.5 `ca_error_list_item_masters.csv` → `error_list_item_master`

**行数**: 79 件 + ヘッダ
**FK**: なし (`error_list_items.field_master_id` から参照される側)
**用途**: 二次チェック画面で `error_type` (漢字/住所) × `attribute` (契約者/被保険者/受取人/指定代理請求人) のグルーピング表示に使用。

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_error_list_item_masterid` | ➡ | `id` | UUID | そのまま |
| 2 | `ca_field_id` | 🔄 | `field_code` | VARCHAR(850) NOT NULL UNIQUE | `01_xxx` 形式の項目コード |
| 3 | `ca_field_name` | 🔄 | `field_name` | VARCHAR(100) NOT NULL | 項目表示名 |
| 4 | `ca_error_type` | ➡ | `error_type` | VARCHAR(100) NOT NULL | 「漢字」「住所」など業務種別 |
| 5 | `ca_group` | 🔄 | `field_group` | VARCHAR(100) | 79 件中 18 件のみ値あり |
| 6 | `ca_attribute` | ➡ | `attribute` | VARCHAR(100) | **二次チェックのグルーピングキー** (契約者/被保険者/受取人/指定代理請求人) |
| メタ | `utcconversiontimezonecode` 等 | ❌ | — | — | 無視 |

**実データの分布** (2026-04-27 時点):
- error_type: 漢字 (48 件) / 住所 (13 件) ※残りは attribute=NULL の共通項目
- attribute: 受取人 17 / 指定代理請求人 7 / 被保険者 4+3 / 契約者 3+3 / NULL 42 (= 共通項目)

**注**: Dataverse 設計書では `ca_group` (グループ) が分類軸の想定だったが、実データではほぼ未投入で、代わりに `ca_attribute` がグルーピング情報を担っている。二次チェック画面の集計クエリは **`attribute` を group key にする** 想定で設計する。

---

## 3. `ca_corporate_type_masters.csv` → `corporate_type_master` 【新規テーブル】

**行数**: 42 件 + ヘッダ
**FK**: なし
**備考**: 元の `sample_table/` には設計書なし。Dataverse 実データを取込むために新設したマスタ。

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_corporate_type_masterid` | ➡ | `id` | UUID | そのまま |
| 2 | `ca_corporate_type` | ➡ | `corporate_type` | VARCHAR(200) | そのまま (法人種類名 漢字) |
| 3 | `ca_short_name` | ➡ | `short_name` | VARCHAR(100) | そのまま (略称 主にカナ) |
| メタ | `utcconversiontimezonecode` 等 | ❌ | — | — | 無視 |

---

## 4. `ca_document_imports.csv` → `error_lists`

**行数**: 182 件 + ヘッダ
**FK**: `document_type_id` → `document_types(id)` (NULL 許可)
**備考**: 業務最上位エンティティ。子テーブル `error_list_items` から参照される **id を Dataverse の `ca_document_importid` から流用**。

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_document_importid` | ➡ | `id` | UUID | そのまま (Dataverse GUID 流用) |
| 2 | `ca_formid` | ➡ | `form_code` | VARCHAR(850) | そのまま |
| 3 | `ca_id` | ➡ | `display_code` | VARCHAR(100) | そのまま |
| 4 | `ca_policy_number` | ➡ | `policy_number` | VARCHAR(100) | そのまま |
| 5 | `ca_batch_number` | ➡ | `batch_number` | VARCHAR(100) | そのまま |
| 6 | `ca_error_type` | ➡ | `error_type` | VARCHAR(100) | そのまま |
| 7 | `ca_vouchertype` | 🔄 | `voucher_type` | VARCHAR(30) | **picklist → 文字列** (1=`error_list`, 2=`application`, 3=`intent_confirmation`, 4=`corporate_confirmation`, 5=`bank_transfer_request`) |
| 8 | `ca_is_degimo` | 🔄 | `is_degimo` | BOOLEAN | `True/False` → `TRUE/FALSE`、空欄は `FALSE` |
| 9 | `ca_reportstatus` | 🔄 | `report_status` | VARCHAR(20) | **picklist → 文字列** (0=`ocr_running`, 1=`new`, 2=`corrected`, 3=`inputting`, 4=`filed`) |
| 10 | `ca_status_updated_datetime` | 🔄 | `status_updated_at` | TIMESTAMPTZ | `2026-04-13 04:10:45.0000000` → ISO 形式 |
| 11 | `ca_main_document_url` | ➡ | `main_document_url` | TEXT | そのまま (JSON 文字列含む) |
| 12 | `ca_import_date` | 🔄 | `imported_on` | DATE | 時刻部分破棄 |
| 13 | `ca_from_name` | 🔄 | `import_file_name` | VARCHAR(100) | カラム名変更 |
| 14 | `ca_document_url` | ➡ | `document_url` | VARCHAR(4000) | そのまま |
| 15 | `ca_sub_document_url` | ➡ | `sub_document_url` | TEXT | そのまま |
| 16 | `ca_fulltext` | ➡ | `full_text` | TEXT | カラム名変更 |
| 17 | `ca_document_id` | 🔄 | `document_type_id` | UUID | 空文字なら NULL |
| 18 | `ca_contactperson.azureactivedirectoryobjectid` | 🔄 | `contact_person_entra_oid` | VARCHAR(255) | systemuser → Entra OID |
| 19 | `ca_inquery_datetime` | 🔄 | `inquiry_at` | TIMESTAMPTZ | typo 修正 (`inquery` → `inquiry`) |
| 20 | `ca_inquiry_category` | ➡ | `inquiry_category` | VARCHAR(100) | そのまま |
| 21 | `ca_inquiry_content` | ➡ | `inquiry_content` | VARCHAR(100) | そのまま |
| 22 | `ca_processing_status` | ➡ | `processing_status` | VARCHAR(100) | そのまま |
| 23 | `ca_2nd_check_owner` | 🔄 | `second_check_owner_name` | VARCHAR(100) | カラム名変更 |
| 24 | `ca_2nd_check_reviewer` | 🔄 | `second_check_reviewer_name` | VARCHAR(100) | カラム名変更 |
| 25 | `ca_2nd_check_result` | 🔄 | `second_check_ng` | BOOLEAN | カラム名変更(意味は同じ NG=true) |
| 26 | `ca_2nd_check_completed_datetime` | 🔄 | `second_check_completed_at` | TIMESTAMPTZ | 命名統一 (`_at`) |
| 27 | `ca_3rd_check_owner` | 🔄 | `third_check_owner_name` | 同上 | 同上 |
| 28 | `ca_3rd_check_reviewer` | 🔄 | `third_check_reviewer_name` | 同上 | 同上 |
| 29 | `ca_3rd_check_result` | 🔄 | `third_check_ng` | BOOLEAN | 同上 |
| 30 | `ca_3rd_check_completed_datetime` | 🔄 | `third_check_completed_at` | 同上 | 同上 |
| 31 | `ca_appid` | ➡ | `app_id` | VARCHAR(100) | そのまま |
| 32 | `ca_input_token_sum` | ➡ | `input_token_sum` | NUMERIC(18,4) | 空文字なら 0 |
| 33 | `ca_output_token_sum` | ➡ | `output_token_sum` | NUMERIC(18,4) | 空文字なら 0 |
| 34 | `ca_ai_usage_amount` | 🔄 | `ai_usage_amount_jpy` | NUMERIC(18,4) | カラム名明示 (単位:円) |
| 35 | `cre00_total_page_count` | 🔄 | `total_page_count` | INTEGER | カラム名から `cre00_` 除去 |
| 無視 | `ca_workflow_status` | ❌ | — | — | 未使用 picklist |
| 無視 | `ca_input_token_sum_date`/`_state` | ❌ | — | — | rollup 内部値、未使用 |
| 無視 | `ca_output_token_sum_date`/`_state` | ❌ | — | — | 同上 |
| 無視 | `ca_input_token_sum_date`等 | ❌ | — | — | 計算カラムの内部メタ |
| 無視 | `processid`, `statecode` 等 | ❌ | — | — | Dataverse メタ |

---

## 5. `ca_document_items.csv` → `error_list_items`

**行数**: ヘッダ込み 5537 行(マルチライン値あり、論理レコード数はやや少ない)
**FK**:
- `error_list_id` → `error_lists(id)` **(NOT NULL)** ⇒ `error_lists` を先に投入
- `field_master_id` → `error_list_item_master(id)` (NULL 許可、当該マスタ未投入のため NULL)

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_document_itemid` | ➡ | `id` | UUID | そのまま |
| 2 | `ca_document_item_id` | ➡ | `item_code` | VARCHAR(850) | そのまま (I-XXXX) |
| 3 | `ca_policy_number` | ➡ | `policy_number` | VARCHAR(100) | そのまま |
| 4 | `ca_document_id` | 🔄 | `error_list_id` | UUID | **そのまま (error_lists の id と一致)** |
| 5 | `ca_field_id` | 🔄 | `field_master_id` | UUID | `error_list_item_master.id` を直接参照 (master 投入後)。master に無い UUID は NULL |
| 6 | `ca_document_id_ai` | 🔄 | `ai_document_code` | VARCHAR(200) | カラム名変更 |
| 7 | `ca_document_item` | 🔄 | `item_label` | VARCHAR(100) | カラム名変更 |
| 8 | `ca_document_value` | 🔄 | `item_value` | TEXT | カラム名変更 |
| 9 | `ca_error_flag` | 🔄 | `error_flag` | BOOLEAN | `True/False` → bool、空欄は FALSE |
| 10 | `ca_ai_inspection_status` | 🔄 | `ai_inspection_status` | VARCHAR(30) | picklist (0..4) → `pending`/`creating`/`created`/`failed`/`unknown` |
| 11 | `ca_confidence` | 🔄 | `confidence_score` | VARCHAR(100) | カラム名変更 |
| 12 | `ca_reportstatus` | 🔄 | `report_status` | VARCHAR(20) | picklist (1..4) → `new`/`corrected`/`inputting`/`filed` (`ocr_running` は対象外) |
| 13 | `ca_status_updated_datetime` | 🔄 | `status_updated_at` | TIMESTAMPTZ | 同上 |
| 14 | `ca_processing_status` | ➡ | `processing_status` | VARCHAR(100) | そのまま |
| 15 | `ca_1st_check_result` | 🔄 | `first_check_ng` | BOOLEAN | カラム名変更 |
| 16 | `ca_1st_check_recovery_value` | 🔄 | `first_check_recovery_value` | VARCHAR(1000) | `1st` → `first` |
| 17 | `ca_1st_check_recovery_reason` | 🔄 | `first_check_recovery_reason` | VARCHAR(1000) | 同上 |
| 18 | `ca_2nd_check_recovery_value` | 🔄 | `second_check_recovery_value` | VARCHAR(1000) | `2nd` → `second` |
| 19 | `ca_2nd_check_recovery_reason` | 🔄 | `second_check_recovery_reason` | VARCHAR(100) | 同上 |
| 20 | `ca_left` | 🔄 | `ocr_bbox_left` | VARCHAR(100) | プレフィクス追加 |
| 21 | `ca_top` | 🔄 | `ocr_bbox_top` | 同上 | 同上 |
| 22 | `ca_width` | 🔄 | `ocr_bbox_width` | 同上 | 同上 |
| 23 | `ca_height` | 🔄 | `ocr_bbox_height` | 同上 | 同上 |
| 24 | `cre00_manual_fix_value` | 🔄 | `manual_fix_value` | TEXT | `cre00_` 除去 |
| 25 | `cre00_page_count` | 🔄 | `page_count` | INTEGER | 同上 |
| 26 | `cre00_sort` | 🔄 | `sort_order` | INTEGER | カラム名変更 |
| 派生 | (なし) | ⊕ | `workflow_state` | VARCHAR(30) | **`pending` 固定** (BPF データ未取込) |
| 派生 | (なし) | ⊕ | `workflow_entered_at` | TIMESTAMPTZ | **NOW() 固定** |
| 無視 | メタ系全部 | ❌ | — | — | 無視 |

---

## 6. `ca_existing_contract_datas.csv` → `atlas_existing_contracts`

**行数**: 138 件 + ヘッダ
**FK**: なし

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_existing_contract_dataid` | ➡ | `id` | UUID | そのまま |
| 2 | `ca_policy_number` | ➡ | `policy_number` | VARCHAR(100) UNIQUE | そのまま |
| 3 | `ca_effective_date` | 🔄 | `effective_date` | DATE | 時刻部分破棄 |
| 4 | `ca_policyholder_name_kanji` | ➡ | `policyholder_name_kanji` | VARCHAR(100) | そのまま |
| 5 | `ca_policyholder_name_kana` | ➡ | `policyholder_name_kana` | VARCHAR(100) | そのまま |
| 6 | `ca_policyholder_birthday` | 🔄 | `policyholder_birthday` | DATE | 時刻部分破棄 |
| 7 | `ca_policyholder_postal_code` | ➡ | `policyholder_postal_code` | VARCHAR(100) | そのまま |
| 8 | `ca_policyholder_address_kana` | ➡ | `policyholder_address_kana` | VARCHAR(1000) | そのまま |
| 9 | `ca_policyholder_address_kanji` | ➡ | `policyholder_address_kanji` | VARCHAR(1000) | そのまま |
| 10〜15 | 被保険者 (insured_*) | ➡ | 同名 | 同上 | 上記と同パターン |
| 16 | `ca_sts` | ➡ | `sts` | VARCHAR(100) | そのまま |
| 無視 | `ca_postal_code` | ❌ | — | — | 「使用しない」と明記の旧 PrimaryName |
| 無視 | メタ系 | ❌ | — | — | 無視 |

---

## 7. `ca_registered_datas.csv` → `atlas_registered_contracts`

**行数**: 147 件 + ヘッダ
**FK**: なし
**備考**: スキーマは `atlas_existing_contracts` とほぼ同じ。マッピングルールも同一。

| # | 旧カラム | → | 新カラム | 型 | 変換 |
|---|---|---|---|---|---|
| 1 | `ca_registered_dataid` | ➡ | `id` | UUID | そのまま |
| 2〜16 | 上記 #6 と同パターン | ➡ | 同名 | 同上 | 同上 |
| 無視 | `ca_postal_code` | ❌ | — | — | 「使用しない」 |
| 無視 | メタ系 | ❌ | — | — | 無視 |

---

## 投入順 (FK 制約に従う)

```
1.   corporate_type_master      (FK なし)
1.5. error_list_item_master     (FK なし、items から参照される)
2.   aflac_address_master       (FK なし)
3.   atlas_existing_contracts   (FK なし)
4.   atlas_registered_contracts (FK なし)
5.   ai_prompts                 (FK -> document_types: NULL 固定)
6.   error_lists                (FK -> document_types: NULL 固定) ★ 子の error_list_items より先
7.   error_list_items           (FK -> error_lists: 必須, FK -> error_list_item_master: master に存在する UUID のみ)
```

---

## ロード時の注意

1. **id は Dataverse GUID をそのまま使う** (`gen_random_uuid()` を発行しない)。これにより `error_list_items.error_list_id` が `error_lists.id` と整合する。
2. **空文字 `""` を NULL に** 変換する (NULLIF を使う)。
3. **picklist の数値文字列を CHECK 制約に合致する英数 snake_case 文字列に** 変換する (CASE WHEN または専用関数)。
4. **Date/Datetime のフォーマット** は `2026-04-13 04:10:45.0000000` の `0000000` を許容するキャストを使う (`::TIMESTAMPTZ` で受けられる)。
5. **Boolean** は `True` / `False` (Pythonic) なので `LOWER(...)::BOOLEAN` でキャスト可能。
6. **prompt の配列化** は CASE で 8 列をフィルタしながら `array_agg` する。

---

## 投入結果 (2026-04-27)

| テーブル | CSV 行数 | 実投入件数 | 備考 |
|---|---|---|---|
| corporate_type_master | 42 | **42** | 全件成功 |
| error_list_item_master | 79 | **79** | 全件成功。`error_list_items` 全 4973 件と FK で JOIN 可能 (orphan 0) |
| aflac_address_master | 66 | **66** | 全件成功 |
| atlas_existing_contracts | 138 | **138** | 全件成功 |
| atlas_registered_contracts | 147 | **147** | 全件成功 |
| ai_prompts | 5300 (raw lines) | **25** | マルチラインの prompt 内容で raw 行数が膨らむ。論理レコードは 25 |
| error_lists | 182 | **182** | 全件成功 |
| error_list_items | 5537 | **4973** | 564 行は `ca_document_id` (親 error_list FK) が**空文字**のため除外 (orphan: 0、empty: 564) |
| japan_post_address_master | — | **124,508** | KEN_ALL 別ロードで併存 (本ドキュメント対象外) |

### 取り込みデータ品質メモ

- **`error_list_items` の親欠落 564 行**: Dataverse 側でも親紐付けされていない行(`ca_document_id` が空)。FK 違反になるためロード時に除外している。商用移行時に「孤児データの扱い」を業務確認する必要あり。
- **`voucher_type`**: 全 182 件が `error_list` に変換 (CSV 内すべて `1`)。picklist 変換が他カテゴリで動作するかは将来の実データで再検証する。
- **`report_status`** (error_lists): `new` 166 / `filed` 16 — picklist 1/4 変換が正常。
- **`ai_inspection_status`** (error_list_items): `pending` 4686 / `created` 239 / `failed` 42 / `creating` 6 — picklist 0/1/2/3 すべて出現。

---

## 投入時に判明したスキーマ修正 (要追記)

実データ投入で **本来の制約・型では入らない値** が見つかったため、以下を変更済み。
本ドキュメントと `migration-from-dataverse.md` も同時に更新した。

| テーブル | カラム | 旧 | 新 | 理由 |
|---|---|---|---|---|
| `aflac_address_master` | `legacy_id` | `VARCHAR(850) NOT NULL UNIQUE` | `VARCHAR(850)` | 旧 ca_id (Dataverse PrimaryName) は実データに重複(例 `14`/`9`/`8` が各 3 件)・空欄(20 件)が混在 |
| `ai_prompts` | `prompt_code` | `VARCHAR(850) NOT NULL UNIQUE` | `VARCHAR(850) NOT NULL` | 旧 ca_name は同一プロンプトコードを複数文書種別で再利用しているため非ユニーク |
| `error_list_items` | `first_check_recovery_value` 他 3 列 | `VARCHAR(1000)` / `VARCHAR(100)` | `TEXT` | AI の生成説明文等で 1000 文字を超える行あり |
