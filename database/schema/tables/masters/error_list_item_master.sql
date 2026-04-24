-- error_list_item_master
-- Source: sample_table/table_05_ca_error_list_item_master.md (ca_error_list_item_master)
-- Purpose: エラーリストの項目定義マスタ。error_list_items から参照される。
-- 慣用に合わせ単数形 (xxx_master) を採用。

CREATE TABLE error_list_item_master (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifiers
    field_code      VARCHAR(850) NOT NULL UNIQUE,           -- ca_field_id (PrimaryName)
    field_name      VARCHAR(100) NOT NULL,                  -- ca_field_name
    error_type      VARCHAR(100) NOT NULL,                  -- ca_error_type
    field_group     VARCHAR(100),                           -- ca_group
    attribute       VARCHAR(100),                           -- ca_attribute

    -- Audit
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_error_list_item_master_error_type ON error_list_item_master (error_type);
CREATE INDEX ix_error_list_item_master_group      ON error_list_item_master (field_group);

COMMENT ON TABLE  error_list_item_master IS 'エラーリスト項目マスタ';
COMMENT ON COLUMN error_list_item_master.field_code IS '項目ID (旧 ca_field_id, Dataverse PrimaryName)';
