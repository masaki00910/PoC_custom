-- process_executions
-- Source: sample_table/table_16_ca_processmanagement.md (ca_processmanagement)
-- Purpose: バッチ処理・フロー実行の実行状況管理。
-- 変更点: ca_requester (systemuser Lookup) → requester_entra_oid (VARCHAR)

CREATE TABLE process_executions (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    process_name            VARCHAR(850) NOT NULL,                          -- ca_process_name (PrimaryName)

    -- Lookups to code_master
    process_type_id         UUID
                            REFERENCES code_master (id) ON DELETE RESTRICT, -- ca_processtype
    process_status_id       UUID
                            REFERENCES code_master (id) ON DELETE RESTRICT, -- ca_process_status

    -- Requester: systemuser → Entra oid
    requester_entra_oid     VARCHAR(255),                                   -- ca_requester

    requested_at            TIMESTAMPTZ,                                    -- ca_requestdatetime
    completed_at            TIMESTAMPTZ,                                    -- ca_completedatetime
    description             VARCHAR(100),                                   -- ca_description
    parent_flow_run_id      VARCHAR(1000),                                  -- ca_parentflow_runid
    execution_log_url       VARCHAR(2000),                                  -- ca_executionloglink (URL)
    result_message          TEXT,                                           -- ca_resultmessage

    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_process_executions_process_type     ON process_executions (process_type_id);
CREATE INDEX ix_process_executions_process_status   ON process_executions (process_status_id);
CREATE INDEX ix_process_executions_requester        ON process_executions (requester_entra_oid);
CREATE INDEX ix_process_executions_requested_at     ON process_executions (requested_at DESC);

COMMENT ON TABLE process_executions IS 'バッチ・フロー実行の状況ログ (旧 ca_processmanagement)';
