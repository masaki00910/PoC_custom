-- document_types
-- Source: sample_table/table_15_ca_document_selection.md (ca_document_selection)
-- Purpose: 処理対象となる書類の種類・プログラムの定義。
-- FK: code_master (document_category_id, ai_config_id)

CREATE TABLE document_types (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifier (旧 ca_document_id: DOC-XXXXXX 形式の業務 ID)
    document_code           VARCHAR(850) UNIQUE,                -- ca_document_id (PrimaryName)

    name                    VARCHAR(200) NOT NULL,              -- ca_name (書類名称)
    program_code            VARCHAR(100),                       -- ca_program_id
    program_name            VARCHAR(100),                       -- ca_program_name

    -- Lookups → FK
    document_category_id    UUID NOT NULL
                            REFERENCES code_master (id) ON DELETE RESTRICT, -- ca_document
    ai_config_id            UUID
                            REFERENCES code_master (id) ON DELETE RESTRICT, -- ca_aiconfig

    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_document_types_document_category ON document_types (document_category_id);
CREATE INDEX ix_document_types_ai_config         ON document_types (ai_config_id);

COMMENT ON TABLE  document_types IS '書類種別。エラーリスト・AIプロンプト・AI点検結果の参照元';
COMMENT ON COLUMN document_types.document_code IS '業務書類ID (旧 ca_document_id, 例: DOC-000001)';
