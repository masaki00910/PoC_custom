-- error_list_items
-- Source: sample_table/table_02_ca_document_item.md (ca_document_item)
-- Purpose: エラーリストの各項目単位のデータ。値・AI点検ステータス・各チェック段階の判定結果を保持。
-- 変更点:
--   * BPF (ca_reportprocessingstatus) の状態を workflow_state / workflow_entered_at で取り込み
--   * ca_ai_inspection_status: picklist (synapselinksynapsetablecreationstate) → 文字列 + CHECK

CREATE TABLE error_list_items (
    id                              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifier
    item_code                       VARCHAR(850) UNIQUE,                    -- ca_document_item_id (I-XXXX, PrimaryName)

    policy_number                   VARCHAR(100) NOT NULL,                  -- ca_policy_number

    -- References
    error_list_id                   UUID NOT NULL
                                    REFERENCES error_lists (id) ON DELETE CASCADE, -- ca_document_id (FK)
    field_master_id                 UUID
                                    REFERENCES error_list_item_master (id) ON DELETE RESTRICT, -- ca_field_id

    ai_document_code                VARCHAR(200),                           -- ca_document_id_ai
    item_label                      VARCHAR(100),                           -- ca_document_item (帳票項目名)
    item_value                      TEXT,                                   -- ca_document_value (ntext 50000)
    error_flag                      BOOLEAN      NOT NULL,                  -- ca_error_flag

    -- AI inspection state (picklist synapselinksynapsetablecreationstate)
    ai_inspection_status            VARCHAR(30)
                                    CHECK (ai_inspection_status IS NULL OR ai_inspection_status IN (
                                        'pending', 'creating', 'created', 'failed', 'unknown'
                                    )),
    confidence_score                VARCHAR(100),                           -- ca_confidence

    report_status                   VARCHAR(20) NOT NULL DEFAULT 'new'
                                    CHECK (report_status IN (
                                        'new', 'corrected', 'inputting', 'filed'
                                    )),                                     -- ca_reportstatus
    status_updated_at               TIMESTAMPTZ NOT NULL,                   -- ca_status_updated_datetime
    processing_status               VARCHAR(100),                           -- ca_processing_status

    -- 1st check
    first_check_ng                  BOOLEAN,                                -- ca_1st_check_result
    first_check_recovery_value      VARCHAR(1000),                          -- ca_1st_check_recovery_value
    first_check_recovery_reason     VARCHAR(1000),                          -- ca_1st_check_recovery_reason

    -- 2nd check recovery
    second_check_recovery_value     VARCHAR(1000),                          -- ca_2nd_check_recovery_value
    second_check_recovery_reason    VARCHAR(100),                           -- ca_2nd_check_recovery_reason

    -- OCR bounding box (原文は nvarchar。数値でなく座標文字列のまま踏襲)
    ocr_bbox_left                   VARCHAR(100),                           -- ca_left
    ocr_bbox_top                    VARCHAR(100),                           -- ca_top
    ocr_bbox_width                  VARCHAR(100),                           -- ca_width
    ocr_bbox_height                 VARCHAR(100),                           -- ca_height

    manual_fix_value                TEXT,                                   -- cre00_manual_fix_value
    page_count                      INTEGER,                                -- cre00_page_count
    sort_order                      INTEGER,                                -- cre00_sort

    -- BPF replacement (旧 ca_reportprocessingstatus を取り込み)
    workflow_state                  VARCHAR(30) NOT NULL DEFAULT 'pending'
                                    CHECK (workflow_state IN (
                                        'pending', 'ai_checking', 'manual_review',
                                        'resolved', 'cancelled'
                                    )),
    workflow_entered_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    workflow_duration_seconds       INTEGER,                                -- BPF: bpf_duration 相当 (分→秒)

    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_error_list_items_error_list       ON error_list_items (error_list_id);
CREATE INDEX ix_error_list_items_field_master     ON error_list_items (field_master_id);
CREATE INDEX ix_error_list_items_policy_number    ON error_list_items (policy_number);
CREATE INDEX ix_error_list_items_workflow_state   ON error_list_items (workflow_state);
CREATE INDEX ix_error_list_items_error_flag       ON error_list_items (error_flag) WHERE error_flag = TRUE;
CREATE INDEX ix_error_list_items_sort_order       ON error_list_items (error_list_id, sort_order);

COMMENT ON TABLE  error_list_items IS 'エラーリスト項目 (帳票の各項目単位)';
COMMENT ON COLUMN error_list_items.workflow_state IS 'ワークフロー状態 (旧 Dataverse BPF ca_reportprocessingstatus の代替)';
COMMENT ON COLUMN error_list_items.error_list_id IS '親エラーリスト。親削除時は CASCADE';
