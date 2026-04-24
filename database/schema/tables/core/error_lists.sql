-- error_lists
-- Source: sample_table/table_01_ca_document_import.md (ca_document_import)
-- Purpose: エラーリスト管理。業務の最上位エンティティ。証券番号単位で取り込まれた帳票処理を管理。
-- 変更点:
--   * ca_contactperson (systemuser Lookup) → contact_person_entra_oid (VARCHAR)
--   * ca_workflow_status (picklist, 未使用) → 移行しない
--   * ca_vouchertype / ca_reportstatus: 数値 picklist → 意味のある文字列 + CHECK
--   * rollup / calculated columns: 通常カラムとして保持 (トリガー or アプリで更新)

CREATE TABLE error_lists (
    id                              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifiers
    form_code                       VARCHAR(850) UNIQUE,                    -- ca_formid (F-XXXX, PrimaryName)
    display_code                    VARCHAR(100),                           -- ca_id (XXXX, 読み取り専用)
    policy_number                   VARCHAR(100) NOT NULL,                  -- ca_policy_number
    batch_number                    VARCHAR(100) NOT NULL,                  -- ca_batch_number
    error_type                      VARCHAR(100) NOT NULL,                  -- ca_error_type

    -- Enumerations (picklist → CHECK constrained string)
    voucher_type                    VARCHAR(30)  NOT NULL
                                    CHECK (voucher_type IN (
                                        'error_list', 'application',
                                        'intent_confirmation', 'corporate_confirmation',
                                        'bank_transfer_request'
                                    )),                                     -- ca_vouchertype
    is_degimo                       BOOLEAN      NOT NULL,                  -- ca_is_degimo
    report_status                   VARCHAR(20)  NOT NULL
                                    CHECK (report_status IN (
                                        'ocr_running', 'new', 'corrected',
                                        'inputting', 'filed'
                                    )),                                     -- ca_reportstatus
    status_updated_at               TIMESTAMPTZ  NOT NULL,                  -- ca_status_updated_datetime

    -- Documents (large text / URL)
    main_document_url               TEXT         NOT NULL,                  -- ca_main_document_url (ntext 20000)
    imported_on                     DATE,                                   -- ca_import_date (DateOnly)
    import_file_name                VARCHAR(100),                           -- ca_from_name
    document_url                    VARCHAR(4000),                          -- ca_document_url
    sub_document_url                TEXT,                                   -- ca_sub_document_url
    full_text                       TEXT,                                   -- ca_fulltext (ntext 1048576)

    -- References
    document_type_id                UUID
                                    REFERENCES document_types (id)
                                    ON DELETE RESTRICT,                     -- ca_document_id
    contact_person_entra_oid        VARCHAR(255),                           -- ca_contactperson (systemuser → Entra oid)

    -- Inquiry (一次情報。本格的な問い合わせは inquiries テーブルに正規化)
    inquiry_at                      TIMESTAMPTZ,                            -- ca_inquery_datetime
    inquiry_category                VARCHAR(100),                           -- ca_inquiry_category
    inquiry_content                 VARCHAR(100),                           -- ca_inquiry_content
    processing_status               VARCHAR(100),                           -- ca_processing_status

    -- 2nd / 3rd check assignment (論理結合: users.user_name)
    second_check_owner_name         VARCHAR(100),                           -- ca_2nd_check_owner
    second_check_reviewer_name      VARCHAR(100),                           -- ca_2nd_check_reviewer
    second_check_ng                 BOOLEAN,                                -- ca_2nd_check_result (true=NG)
    second_check_completed_at       TIMESTAMPTZ,                            -- ca_2nd_check_completed_datetime

    third_check_owner_name          VARCHAR(100),                           -- ca_3rd_check_owner
    third_check_reviewer_name       VARCHAR(100),                           -- ca_3rd_check_reviewer
    third_check_ng                  BOOLEAN,                                -- ca_3rd_check_result
    third_check_completed_at        TIMESTAMPTZ,                            -- ca_3rd_check_completed_datetime

    -- AI usage metrics (rollup/calc field → aggregated column; 更新はアプリ責務)
    app_id                          VARCHAR(100),                           -- ca_appid
    input_token_sum                 NUMERIC(18,4) NOT NULL DEFAULT 0,       -- ca_input_token_sum
    output_token_sum                NUMERIC(18,4) NOT NULL DEFAULT 0,       -- ca_output_token_sum
    ai_usage_amount_jpy             NUMERIC(18,4) NOT NULL DEFAULT 0,       -- ca_ai_usage_amount
    total_page_count                INTEGER,                                -- cre00_total_page_count

    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_error_lists_policy_number         ON error_lists (policy_number);
CREATE INDEX ix_error_lists_batch_number          ON error_lists (batch_number);
CREATE INDEX ix_error_lists_report_status         ON error_lists (report_status);
CREATE INDEX ix_error_lists_document_type         ON error_lists (document_type_id);
CREATE INDEX ix_error_lists_status_updated_at     ON error_lists (status_updated_at DESC);
CREATE INDEX ix_error_lists_imported_on           ON error_lists (imported_on);
CREATE INDEX ix_error_lists_contact_entra_oid     ON error_lists (contact_person_entra_oid);

COMMENT ON TABLE  error_lists IS 'エラーリスト管理 (業務最上位エンティティ)';
COMMENT ON COLUMN error_lists.contact_person_entra_oid IS '担当者 Entra ID OID (旧 ca_contactperson systemuser Lookup の置換)';
COMMENT ON COLUMN error_lists.ai_usage_amount_jpy IS 'AI利用金額(円)。アプリ側で集計 (旧 rollup/calc field)';
