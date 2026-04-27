-- corporate_type_master
-- Source: sample_data/ca_corporate_type_masters.csv (Dataverse からのエクスポート)
-- Note: 元の sample_table/ には設計書がない。Dataverse 実データ取込時に追加した法人種類マスタ。
-- Purpose: 申込書の法人確認チェックで参照する法人種類 (例「文部省組員福祉協会」「モンブショウ」など) を保持。

CREATE TABLE corporate_type_master (
    id                          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),

    corporate_type              VARCHAR(200) NOT NULL,                -- ca_corporate_type (法人種類名、漢字)
    short_name                  VARCHAR(100),                         -- ca_short_name (略称、カナ)

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_corporate_type_master_short_name ON corporate_type_master (short_name);

COMMENT ON TABLE  corporate_type_master IS '法人種類マスタ (sample_table の設計書には記載なし、実データから新規追加)';
COMMENT ON COLUMN corporate_type_master.corporate_type IS '法人種類の正式名 (漢字)';
COMMENT ON COLUMN corporate_type_master.short_name IS '略称 (主に半角/全角カナ)';
