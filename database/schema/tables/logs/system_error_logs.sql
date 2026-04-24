-- system_error_logs
-- Source: sample_table/table_13_ca_error_log.md (ca_error_log)
-- Purpose: システム実行時のエラー情報を記録。
-- 変更点:
--   * ca_error_massage (typo) → error_message (正しい綴り)
--   * ca_system_type / ca_business_type: picklist → CHECK constrained string

CREATE TABLE system_error_logs (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    log_code            VARCHAR(850) NOT NULL,                              -- ca_log_id (PrimaryName)

    system_type         VARCHAR(20) NOT NULL
                        CHECK (system_type IN ('power_automate', 'copilot_studio', 'other')), -- ca_system_type

    error_location      VARCHAR(100) NOT NULL,                              -- ca_error_location
    error_message       TEXT         NOT NULL,                              -- ca_error_massage (typo fixed)
    execution_id        VARCHAR(100) NOT NULL,                              -- ca_execution_id
    execution_user      VARCHAR(100) NOT NULL,                              -- ca_execution_user
    input_parameters    TEXT         NOT NULL,                              -- ca_input_parameters
    stacktrace          TEXT         NOT NULL,                              -- ca_stacktrace
    error_code          VARCHAR(100),                                       -- ca_error_code
    check_name          VARCHAR(100),                                       -- ca_check_name

    business_type       VARCHAR(20)
                        CHECK (business_type IS NULL OR business_type IN ('kanji', 'address')), -- ca_business_type

    policy_number       VARCHAR(100),                                       -- ca_policy_number
    item                VARCHAR(100),                                       -- ca_item

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_system_error_logs_system_type   ON system_error_logs (system_type);
CREATE INDEX ix_system_error_logs_business_type ON system_error_logs (business_type);
CREATE INDEX ix_system_error_logs_policy_number ON system_error_logs (policy_number);
CREATE INDEX ix_system_error_logs_created_at    ON system_error_logs (created_at DESC);

COMMENT ON TABLE  system_error_logs IS 'システム実行時エラーログ';
COMMENT ON COLUMN system_error_logs.error_message IS '旧 ca_error_massage (typo) を error_message に修正';
