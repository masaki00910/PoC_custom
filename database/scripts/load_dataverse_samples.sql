-- Load Dataverse-exported sample data (sample_data/*.csv) into PostgreSQL.
-- Strategy: TEMP staging tables (all columns TEXT) -> \COPY -> INSERT...SELECT with transformation.
-- Mapping reference: docs/dataverse-csv-import.md
-- Run order respects FK dependencies.
-- Run with: psql -U postgres -d aflac_poc_test -f scripts/load_dataverse_samples.sql

\set ON_ERROR_STOP on
\set SAMPLE_DIR 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data'

-- ============================================================================
-- STEP 0: clean target tables (idempotent reload)
-- ============================================================================
\echo ''
\echo '=== Step 0: TRUNCATE target tables ==='
TRUNCATE TABLE
    error_list_items,
    error_lists,
    ai_prompts,
    atlas_registered_contracts,
    atlas_existing_contracts,
    aflac_address_master,
    corporate_type_master,
    error_list_item_master
RESTART IDENTITY CASCADE;

BEGIN;

-- ============================================================================
-- STEP 1: corporate_type_master
-- ============================================================================
\echo ''
\echo '=== Step 1: corporate_type_master ==='

CREATE TEMP TABLE staging_corporate_type (
    utcconversiontimezonecode    TEXT,
    importsequencenumber         TEXT,
    statuscode                   TEXT,
    timezoneruleversionnumber    TEXT,
    versionnumber                TEXT,
    ca_corporate_type            TEXT,
    ca_corporate_type_masterid   TEXT,
    statecode                    TEXT,
    ca_short_name                TEXT,
    owningbusinessunit           TEXT
) ON COMMIT DROP;

\COPY staging_corporate_type FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_corporate_type_masters.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

INSERT INTO corporate_type_master (id, corporate_type, short_name)
SELECT
    NULLIF(ca_corporate_type_masterid, '')::UUID,
    ca_corporate_type,
    NULLIF(ca_short_name, '')
FROM staging_corporate_type;

SELECT COUNT(*) AS corporate_type_master_loaded FROM corporate_type_master;

-- ============================================================================
-- STEP 1.5: error_list_item_master (error_list_items の FK 参照先)
-- ============================================================================
\echo ''
\echo '=== Step 1.5: error_list_item_master ==='

CREATE TEMP TABLE staging_error_item_master (
    utcconversiontimezonecode    TEXT,
    importsequencenumber         TEXT,
    ca_error_list_item_masterid  TEXT,
    ca_error_type                TEXT,
    ca_group                     TEXT,
    statuscode                   TEXT,
    timezoneruleversionnumber    TEXT,
    versionnumber                TEXT,
    ca_attribute                 TEXT,
    statecode                    TEXT,
    ca_field_id                  TEXT,
    ca_field_name                TEXT,
    owningbusinessunit           TEXT
) ON COMMIT DROP;

\COPY staging_error_item_master FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_error_list_item_masters.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

INSERT INTO error_list_item_master (
    id, field_code, field_name, error_type, field_group, attribute
)
SELECT
    NULLIF(ca_error_list_item_masterid, '')::UUID,
    ca_field_id,
    ca_field_name,
    ca_error_type,
    NULLIF(ca_group, ''),
    NULLIF(ca_attribute, '')
FROM staging_error_item_master;

SELECT COUNT(*) AS error_list_item_master_loaded FROM error_list_item_master;

-- ============================================================================
-- STEP 2: aflac_address_master
-- ============================================================================
\echo ''
\echo '=== Step 2: aflac_address_master ==='

CREATE TEMP TABLE staging_aflac_addr (
    ca_aflac_address_masterid    TEXT,
    ca_id                        TEXT,
    utcconversiontimezonecode    TEXT,
    importsequencenumber         TEXT,
    ca_customer_barcode          TEXT,
    statuscode                   TEXT,
    timezoneruleversionnumber    TEXT,
    versionnumber                TEXT,
    ca_address_code              TEXT,
    ca_oaza_common_name          TEXT,
    ca_oaza_common_name_kana     TEXT,
    ca_oaza_flag                 TEXT,
    ca_aza_cho_name_kana         TEXT,
    ca_aza_cho_name              TEXT,
    ca_aza_flag                  TEXT,
    ca_municipality_name         TEXT,
    ca_municipality_name_kana    TEXT,
    ca_abolished_year_month      TEXT,
    ca_new_address_code          TEXT,
    ca_effective_year_month      TEXT,
    ca_search_f                  TEXT,
    statecode                    TEXT,
    ca_prefecture_name           TEXT,
    ca_prefecture_name_kana      TEXT,
    ca_postal_code               TEXT,
    owningbusinessunit           TEXT
) ON COMMIT DROP;

\COPY staging_aflac_addr FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_aflac_address_masters.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

INSERT INTO aflac_address_master (
    id, legacy_id, address_code, new_address_code, postal_code,
    prefecture_name, prefecture_name_kana, municipality_name, municipality_name_kana,
    oaza_common_name, oaza_common_name_kana, oaza_flag,
    aza_cho_name, aza_cho_name_kana, aza_flag,
    customer_barcode, effective_year_month, abolished_year_month, search_flag
)
SELECT
    NULLIF(ca_aflac_address_masterid, '')::UUID,
    NULLIF(ca_id, ''),  -- legacy_id: 重複・空欄を許容 (Dataverse PrimaryName)
    NULLIF(ca_address_code, ''),
    NULLIF(ca_new_address_code, ''),
    NULLIF(ca_postal_code, ''),
    NULLIF(ca_prefecture_name, ''),
    NULLIF(ca_prefecture_name_kana, ''),
    NULLIF(ca_municipality_name, ''),
    NULLIF(ca_municipality_name_kana, ''),
    NULLIF(ca_oaza_common_name, ''),
    NULLIF(ca_oaza_common_name_kana, ''),
    NULLIF(ca_oaza_flag, '')::BOOLEAN,
    NULLIF(ca_aza_cho_name, ''),
    NULLIF(ca_aza_cho_name_kana, ''),
    NULLIF(ca_aza_flag, '')::BOOLEAN,
    NULLIF(ca_customer_barcode, ''),
    NULLIF(ca_effective_year_month, ''),
    NULLIF(ca_abolished_year_month, ''),
    NULLIF(ca_search_f, '')
FROM staging_aflac_addr;

SELECT COUNT(*) AS aflac_address_master_loaded FROM aflac_address_master;

-- ============================================================================
-- STEP 3: atlas_existing_contracts
-- ============================================================================
\echo ''
\echo '=== Step 3: atlas_existing_contracts ==='

CREATE TEMP TABLE staging_existing (
    ca_postal_code                  TEXT,
    ca_existing_contract_dataid     TEXT,
    ca_sts                          TEXT,
    utcconversiontimezonecode       TEXT,
    importsequencenumber            TEXT,
    statuscode                      TEXT,
    timezoneruleversionnumber       TEXT,
    versionnumber                   TEXT,
    ca_effective_date               TEXT,
    ca_policyholder_address_kana    TEXT,
    ca_policyholder_address_kanji   TEXT,
    ca_policyholder_birthday        TEXT,
    ca_policyholder_postal_code     TEXT,
    ca_policyholder_name_kana       TEXT,
    ca_policyholder_name_kanji      TEXT,
    statecode                       TEXT,
    ca_insured_address_kana         TEXT,
    ca_insured_address_kanji        TEXT,
    ca_insured_birthday             TEXT,
    ca_insured_postal_code          TEXT,
    ca_insured_name_kana            TEXT,
    ca_insured_name_kanji           TEXT,
    ca_policy_number                TEXT,
    owningbusinessunit              TEXT
) ON COMMIT DROP;

\COPY staging_existing FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_existing_contract_datas.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

INSERT INTO atlas_existing_contracts (
    id, policy_number, effective_date, sts,
    policyholder_name_kanji, policyholder_name_kana, policyholder_birthday,
    policyholder_postal_code, policyholder_address_kana, policyholder_address_kanji,
    insured_name_kanji, insured_name_kana, insured_birthday,
    insured_postal_code, insured_address_kana, insured_address_kanji
)
SELECT
    NULLIF(ca_existing_contract_dataid, '')::UUID,
    ca_policy_number,
    NULLIF(ca_effective_date, '')::DATE,
    NULLIF(ca_sts, ''),
    NULLIF(ca_policyholder_name_kanji, ''),
    NULLIF(ca_policyholder_name_kana, ''),
    NULLIF(ca_policyholder_birthday, '')::DATE,
    NULLIF(ca_policyholder_postal_code, ''),
    NULLIF(ca_policyholder_address_kana, ''),
    NULLIF(ca_policyholder_address_kanji, ''),
    NULLIF(ca_insured_name_kanji, ''),
    NULLIF(ca_insured_name_kana, ''),
    NULLIF(ca_insured_birthday, '')::DATE,
    NULLIF(ca_insured_postal_code, ''),
    NULLIF(ca_insured_address_kana, ''),
    NULLIF(ca_insured_address_kanji, '')
FROM staging_existing;

SELECT COUNT(*) AS atlas_existing_contracts_loaded FROM atlas_existing_contracts;

-- ============================================================================
-- STEP 4: atlas_registered_contracts (same shape as existing)
-- ============================================================================
\echo ''
\echo '=== Step 4: atlas_registered_contracts ==='

CREATE TEMP TABLE staging_registered (
    ca_postal_code                  TEXT,
    ca_registered_dataid            TEXT,
    ca_sts                          TEXT,
    utcconversiontimezonecode       TEXT,
    importsequencenumber            TEXT,
    statuscode                      TEXT,
    timezoneruleversionnumber       TEXT,
    versionnumber                   TEXT,
    ca_effective_date               TEXT,
    ca_policyholder_address_kana    TEXT,
    ca_policyholder_address_kanji   TEXT,
    ca_policyholder_birthday        TEXT,
    ca_policyholder_postal_code     TEXT,
    ca_policyholder_name_kana       TEXT,
    ca_policyholder_name_kanji      TEXT,
    statecode                       TEXT,
    ca_insured_address_kana         TEXT,
    ca_insured_address_kanji        TEXT,
    ca_insured_birthday             TEXT,
    ca_insured_postal_code          TEXT,
    ca_insured_name_kana            TEXT,
    ca_insured_name_kanji           TEXT,
    ca_policy_number                TEXT,
    owningbusinessunit              TEXT
) ON COMMIT DROP;

\COPY staging_registered FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_registered_datas.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

INSERT INTO atlas_registered_contracts (
    id, policy_number, effective_date, sts,
    policyholder_name_kanji, policyholder_name_kana, policyholder_birthday,
    policyholder_postal_code, policyholder_address_kana, policyholder_address_kanji,
    insured_name_kanji, insured_name_kana, insured_birthday,
    insured_postal_code, insured_address_kana, insured_address_kanji
)
SELECT
    NULLIF(ca_registered_dataid, '')::UUID,
    ca_policy_number,
    NULLIF(ca_effective_date, '')::DATE,
    NULLIF(ca_sts, ''),
    NULLIF(ca_policyholder_name_kanji, ''),
    NULLIF(ca_policyholder_name_kana, ''),
    NULLIF(ca_policyholder_birthday, '')::DATE,
    NULLIF(ca_policyholder_postal_code, ''),
    NULLIF(ca_policyholder_address_kana, ''),
    NULLIF(ca_policyholder_address_kanji, ''),
    NULLIF(ca_insured_name_kanji, ''),
    NULLIF(ca_insured_name_kana, ''),
    NULLIF(ca_insured_birthday, '')::DATE,
    NULLIF(ca_insured_postal_code, ''),
    NULLIF(ca_insured_address_kana, ''),
    NULLIF(ca_insured_address_kanji, '')
FROM staging_registered;

SELECT COUNT(*) AS atlas_registered_contracts_loaded FROM atlas_registered_contracts;

-- ============================================================================
-- STEP 5: ai_prompts (prompts -> TEXT[] array)
-- ============================================================================
\echo ''
\echo '=== Step 5: ai_prompts ==='

CREATE TEMP TABLE staging_ai_prompts (
    ca_ai                       TEXT,
    ca_ai_promptid              TEXT,
    utcconversiontimezonecode   TEXT,
    importsequencenumber        TEXT,
    statuscode                  TEXT,
    timezoneruleversionnumber   TEXT,
    ca_knowledge                TEXT,
    versionnumber               TEXT,
    ca_prompt                   TEXT,
    ca_prompt2                  TEXT,
    ca_prompt3                  TEXT,
    ca_prompt4                  TEXT,
    ca_prompt5                  TEXT,
    ca_prompt6                  TEXT,
    ca_prompt7                  TEXT,
    ca_prompt8                  TEXT,
    ca_name                     TEXT,
    ca_id                       TEXT,
    ca_processing_order         TEXT,
    ca_condition                TEXT,
    ca_sample_data              TEXT,
    statecode                   TEXT,
    owningbusinessunit          TEXT,
    ca_documentid               TEXT
) ON COMMIT DROP;

\COPY staging_ai_prompts FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_ai_prompts.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

-- ca_prompt..ca_prompt8 を空除外して TEXT[] に詰め込む
-- ca_ai picklist (0=inactive, 1=active)
-- ca_processing_order: NOT NULL なので 0 デフォルト
-- prompt_name (ca_id) は NOT NULL なので NULL なら ca_name を流用
INSERT INTO ai_prompts (
    id, prompt_code, prompt_name, processing_order, use_knowledge,
    status, condition_field, document_type_id, prompts, sample_data
)
SELECT
    NULLIF(ca_ai_promptid, '')::UUID,
    ca_name,
    COALESCE(NULLIF(ca_id, ''), ca_name),
    COALESCE(NULLIF(ca_processing_order, '')::INTEGER, 0),
    COALESCE(NULLIF(ca_knowledge, '')::BOOLEAN, FALSE),
    CASE NULLIF(ca_ai, '')
        WHEN '0' THEN 'inactive'
        WHEN '1' THEN 'active'
        ELSE 'active'
    END,
    NULLIF(ca_condition, ''),
    NULL::UUID,  -- document_type_id: 参照先 document_types が空のため NULL 固定
    ARRAY(
        SELECT p FROM (VALUES
            (1, NULLIF(ca_prompt,  '')),
            (2, NULLIF(ca_prompt2, '')),
            (3, NULLIF(ca_prompt3, '')),
            (4, NULLIF(ca_prompt4, '')),
            (5, NULLIF(ca_prompt5, '')),
            (6, NULLIF(ca_prompt6, '')),
            (7, NULLIF(ca_prompt7, '')),
            (8, NULLIF(ca_prompt8, ''))
        ) AS x(idx, p)
        WHERE p IS NOT NULL
        ORDER BY idx
    ),
    NULLIF(ca_sample_data, '')
FROM staging_ai_prompts;

SELECT COUNT(*) AS ai_prompts_loaded, AVG(array_length(prompts, 1))::NUMERIC(5,2) AS avg_prompt_count FROM ai_prompts;

-- ============================================================================
-- STEP 6: error_lists (parent of error_list_items)
-- ============================================================================
\echo ''
\echo '=== Step 6: error_lists ==='

CREATE TEMP TABLE staging_error_lists (
    ca_workflow_status              TEXT,
    ca_ai_usage_amount              TEXT,
    ca_appid                        TEXT,
    ca_id                           TEXT,
    utcconversiontimezonecode       TEXT,
    importsequencenumber            TEXT,
    ca_error_type                   TEXT,
    ca_formid                       TEXT,
    ca_sub_document_url             TEXT,
    statuscode                      TEXT,
    ca_status_updated_datetime      TEXT,
    timezoneruleversionnumber       TEXT,
    ca_is_degimo                    TEXT,
    ca_document_importid            TEXT,
    versionnumber                   TEXT,
    ca_batch_number                 TEXT,
    processid                       TEXT,
    ca_main_document_url            TEXT,
    ca_3rd_check_result             TEXT,
    ca_3rd_check_completed_datetime TEXT,
    ca_3rd_check_owner              TEXT,
    ca_3rd_check_reviewer           TEXT,
    ca_2nd_check_result             TEXT,
    ca_2nd_check_completed_datetime TEXT,
    ca_2nd_check_owner              TEXT,
    ca_2nd_check_reviewer           TEXT,
    ca_input_token_sum              TEXT,
    ca_input_token_sum_date         TEXT,
    ca_input_token_sum_state        TEXT,
    ca_processing_status            TEXT,
    ca_output_token_sum             TEXT,
    ca_output_token_sum_date        TEXT,
    ca_output_token_sum_state       TEXT,
    ca_from_name                    TEXT,
    ca_import_date                  TEXT,
    ca_inquiry_category             TEXT,
    ca_inquiry_content              TEXT,
    ca_inquery_datetime             TEXT,
    ca_fulltext                     TEXT,
    ca_reportstatus                 TEXT,
    ca_vouchertype                  TEXT,
    ca_document_url                 TEXT,
    statecode                       TEXT,
    cre00_total_page_count          TEXT,
    ca_policy_number                TEXT,
    owningbusinessunit              TEXT,
    ca_document_id                  TEXT,
    "ca_contactperson.azureactivedirectoryobjectid" TEXT
) ON COMMIT DROP;

\COPY staging_error_lists FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_document_imports.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

INSERT INTO error_lists (
    id, form_code, display_code, policy_number, batch_number, error_type,
    voucher_type, is_degimo, report_status, status_updated_at,
    main_document_url, imported_on, import_file_name, document_url, sub_document_url, full_text,
    document_type_id, contact_person_entra_oid,
    inquiry_at, inquiry_category, inquiry_content, processing_status,
    second_check_owner_name, second_check_reviewer_name, second_check_ng, second_check_completed_at,
    third_check_owner_name, third_check_reviewer_name, third_check_ng, third_check_completed_at,
    app_id, input_token_sum, output_token_sum, ai_usage_amount_jpy, total_page_count
)
SELECT
    NULLIF(ca_document_importid, '')::UUID,
    NULLIF(ca_formid, ''),
    NULLIF(ca_id, ''),
    ca_policy_number,
    ca_batch_number,
    ca_error_type,
    -- voucher_type: picklist 1..5 -> string
    CASE NULLIF(ca_vouchertype, '')
        WHEN '1' THEN 'error_list'
        WHEN '2' THEN 'application'
        WHEN '3' THEN 'intent_confirmation'
        WHEN '4' THEN 'corporate_confirmation'
        WHEN '5' THEN 'bank_transfer_request'
        ELSE 'error_list'
    END,
    COALESCE(NULLIF(ca_is_degimo, '')::BOOLEAN, FALSE),
    -- report_status: picklist 0..4 -> string
    CASE NULLIF(ca_reportstatus, '')
        WHEN '0' THEN 'ocr_running'
        WHEN '1' THEN 'new'
        WHEN '2' THEN 'corrected'
        WHEN '3' THEN 'inputting'
        WHEN '4' THEN 'filed'
        ELSE 'new'
    END,
    NULLIF(ca_status_updated_datetime, '')::TIMESTAMPTZ,
    COALESCE(ca_main_document_url, ''),  -- NOT NULL
    NULLIF(ca_import_date, '')::DATE,
    NULLIF(ca_from_name, ''),
    NULLIF(ca_document_url, ''),
    NULLIF(ca_sub_document_url, ''),
    NULLIF(ca_fulltext, ''),
    NULL::UUID,  -- document_type_id: 参照先 document_types 未投入のため NULL 固定 (FK 違反回避)
    NULLIF("ca_contactperson.azureactivedirectoryobjectid", ''),
    NULLIF(ca_inquery_datetime, '')::TIMESTAMPTZ,
    NULLIF(ca_inquiry_category, ''),
    NULLIF(ca_inquiry_content, ''),
    NULLIF(ca_processing_status, ''),
    NULLIF(ca_2nd_check_owner, ''),
    NULLIF(ca_2nd_check_reviewer, ''),
    NULLIF(ca_2nd_check_result, '')::BOOLEAN,
    NULLIF(ca_2nd_check_completed_datetime, '')::TIMESTAMPTZ,
    NULLIF(ca_3rd_check_owner, ''),
    NULLIF(ca_3rd_check_reviewer, ''),
    NULLIF(ca_3rd_check_result, '')::BOOLEAN,
    NULLIF(ca_3rd_check_completed_datetime, '')::TIMESTAMPTZ,
    NULLIF(ca_appid, ''),
    COALESCE(NULLIF(ca_input_token_sum, '')::NUMERIC, 0),
    COALESCE(NULLIF(ca_output_token_sum, '')::NUMERIC, 0),
    COALESCE(NULLIF(ca_ai_usage_amount, '')::NUMERIC, 0),
    NULLIF(cre00_total_page_count, '')::INTEGER
FROM staging_error_lists;

SELECT COUNT(*) AS error_lists_loaded FROM error_lists;

-- ============================================================================
-- STEP 7: error_list_items (FK -> error_lists)
-- ============================================================================
\echo ''
\echo '=== Step 7: error_list_items ==='

CREATE TEMP TABLE staging_error_items (
    ca_ai_inspection_status         TEXT,
    utcconversiontimezonecode       TEXT,
    importsequencenumber            TEXT,
    ca_error_flag                   TEXT,
    ca_reportstatus                 TEXT,
    statuscode                      TEXT,
    ca_status_updated_datetime      TEXT,
    cre00_sort                      TEXT,
    timezoneruleversionnumber       TEXT,
    ca_document_itemid              TEXT,
    versionnumber                   TEXT,
    processid                       TEXT,
    ca_1st_check_result             TEXT,
    ca_1st_check_recovery_value     TEXT,
    ca_1st_check_recovery_reason    TEXT,
    ca_2nd_check_recovery_value     TEXT,
    ca_2nd_check_recovery_reason    TEXT,
    ca_confidence                   TEXT,
    ca_processing_status            TEXT,
    ca_document_id_ai               TEXT,
    cre00_page_count                TEXT,
    ca_document_item                TEXT,
    cre00_manual_fix_value          TEXT,
    ca_document_item_id             TEXT,
    ca_height                       TEXT,
    ca_left                         TEXT,
    ca_top                          TEXT,
    ca_width                        TEXT,
    statecode                       TEXT,
    ca_policy_number                TEXT,
    ca_document_value               TEXT,
    ca_document_id                  TEXT,
    owningbusinessunit              TEXT,
    ca_field_id                     TEXT
) ON COMMIT DROP;

\COPY staging_error_items FROM 'C:/work/2026/03_Aflac/20260423_PoC_custom/sample_data/ca_document_items.csv' WITH (FORMAT csv, HEADER, ENCODING 'UTF8')

INSERT INTO error_list_items (
    id, item_code, policy_number, error_list_id, field_master_id,
    ai_document_code, item_label, item_value, error_flag,
    ai_inspection_status, confidence_score, report_status, status_updated_at, processing_status,
    first_check_ng, first_check_recovery_value, first_check_recovery_reason,
    second_check_recovery_value, second_check_recovery_reason,
    ocr_bbox_left, ocr_bbox_top, ocr_bbox_width, ocr_bbox_height,
    manual_fix_value, page_count, sort_order
)
SELECT
    NULLIF(ca_document_itemid, '')::UUID,
    NULLIF(ca_document_item_id, ''),
    ca_policy_number,
    NULLIF(ca_document_id, '')::UUID,
    -- field_master_id: master が投入されたので CSV の ca_field_id を参照。master に無い UUID は NULL に落とす
    CASE
        WHEN NULLIF(ca_field_id, '')::UUID IN (SELECT id FROM error_list_item_master) THEN NULLIF(ca_field_id, '')::UUID
        ELSE NULL
    END,
    NULLIF(ca_document_id_ai, ''),
    NULLIF(ca_document_item, ''),
    NULLIF(ca_document_value, ''),
    COALESCE(NULLIF(ca_error_flag, '')::BOOLEAN, FALSE),
    -- ai_inspection_status: synapselinksynapsetablecreationstate 0..4
    CASE NULLIF(ca_ai_inspection_status, '')
        WHEN '0' THEN 'pending'
        WHEN '1' THEN 'creating'
        WHEN '2' THEN 'created'
        WHEN '3' THEN 'failed'
        WHEN '4' THEN 'unknown'
        ELSE NULL
    END,
    NULLIF(ca_confidence, ''),
    -- report_status: 1..4 ('ocr_running' は item には適用しない)
    CASE NULLIF(ca_reportstatus, '')
        WHEN '1' THEN 'new'
        WHEN '2' THEN 'corrected'
        WHEN '3' THEN 'inputting'
        WHEN '4' THEN 'filed'
        ELSE 'new'
    END,
    NULLIF(ca_status_updated_datetime, '')::TIMESTAMPTZ,
    NULLIF(ca_processing_status, ''),
    NULLIF(ca_1st_check_result, '')::BOOLEAN,
    NULLIF(ca_1st_check_recovery_value, ''),
    NULLIF(ca_1st_check_recovery_reason, ''),
    NULLIF(ca_2nd_check_recovery_value, ''),
    NULLIF(ca_2nd_check_recovery_reason, ''),
    NULLIF(ca_left, ''),
    NULLIF(ca_top, ''),
    NULLIF(ca_width, ''),
    NULLIF(ca_height, ''),
    NULLIF(cre00_manual_fix_value, ''),
    NULLIF(cre00_page_count, '')::INTEGER,
    NULLIF(cre00_sort, '')::INTEGER
FROM staging_error_items
-- 親 error_list が存在する行のみ投入 (FK 制約遵守)
WHERE NULLIF(ca_document_id, '')::UUID IN (SELECT id FROM error_lists);

SELECT COUNT(*) AS error_list_items_loaded FROM error_list_items;

-- ============================================================================
-- COMMIT
-- ============================================================================
COMMIT;

\echo ''
\echo '=== ALL COUNTS ==='
SELECT 'corporate_type_master'         AS tbl, COUNT(*) FROM corporate_type_master
UNION ALL SELECT 'aflac_address_master',          COUNT(*) FROM aflac_address_master
UNION ALL SELECT 'atlas_existing_contracts',      COUNT(*) FROM atlas_existing_contracts
UNION ALL SELECT 'atlas_registered_contracts',    COUNT(*) FROM atlas_registered_contracts
UNION ALL SELECT 'ai_prompts',                    COUNT(*) FROM ai_prompts
UNION ALL SELECT 'error_lists',                   COUNT(*) FROM error_lists
UNION ALL SELECT 'error_list_items',              COUNT(*) FROM error_list_items;
