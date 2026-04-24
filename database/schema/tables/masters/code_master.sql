-- code_master
-- Source: sample_table/table_14_ca_code_management.md (ca_code_management)
-- Purpose: 大分類・中分類のコード定義。document_types や process_executions の参照元として使用される汎用コードマスタ。

CREATE TABLE code_master (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifiers
    display_name        VARCHAR(850) NOT NULL,              -- ca_display_name (PrimaryName)
    category_name       VARCHAR(100),                       -- ca_code_category (大分類名)
    category_code       VARCHAR(100),                       -- ca_code_value (大分類コード)
    middle_code         INTEGER,                            -- ca_middle_code (中分類コード)
    middle_name         VARCHAR(1000),                      -- ca_middle_code_name (中分類名)
    code_key            VARCHAR(100),                       -- ca_key
    code_value          VARCHAR(4000),                      -- ca_value
    display_order       VARCHAR(100),                       -- ca_display_order (nvarchar 原文踏襲)
    contents            TEXT,                               -- ca_contents
    additional_info     TEXT,                               -- ca_additionalinfo
    flow_ai             VARCHAR(100),                       -- cre00_flowai

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX ux_code_master_category_middle
    ON code_master (category_code, middle_code)
    WHERE category_code IS NOT NULL AND middle_code IS NOT NULL;

CREATE INDEX ix_code_master_category_code ON code_master (category_code);

COMMENT ON TABLE  code_master IS '汎用コードマスタ。大分類・中分類のコード体系を保持';
COMMENT ON COLUMN code_master.display_name   IS '表示名 (旧 ca_display_name, Dataverse PrimaryName)';
COMMENT ON COLUMN code_master.category_code  IS '大分類コード (旧 ca_code_value)';
COMMENT ON COLUMN code_master.middle_code    IS '中分類コード (旧 ca_middle_code)';
