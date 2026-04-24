-- aflac_address_master
-- Source: sample_table/table_08_ca_aflac_address_master.md
-- Purpose: Aflac独自の住所マスタ。郵政住所より詳細な階層 (大字・字・丁) と新旧コードマッピング、有効期間を保持。

CREATE TABLE aflac_address_master (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifier (surrogate, Dataverse PrimaryName)
    legacy_id                   VARCHAR(850) NOT NULL UNIQUE, -- ca_id

    address_code                VARCHAR(100),               -- ca_address_code
    new_address_code            VARCHAR(100),               -- ca_new_address_code
    postal_code                 VARCHAR(100),               -- ca_postal_code

    prefecture_name             VARCHAR(100),               -- ca_prefecture_name
    prefecture_name_kana        VARCHAR(100),               -- ca_prefecture_name_kana
    municipality_name           VARCHAR(100),               -- ca_municipality_name (郡含む)
    municipality_name_kana      VARCHAR(100),               -- ca_municipality_name_kana

    oaza_common_name            VARCHAR(100),               -- ca_oaza_common_name (大字・通称名)
    oaza_common_name_kana       VARCHAR(100),               -- ca_oaza_common_name_kana
    oaza_flag                   BOOLEAN,                    -- ca_oaza_flag

    aza_cho_name                VARCHAR(100),               -- ca_aza_cho_name (字・丁名)
    aza_cho_name_kana           VARCHAR(100),               -- ca_aza_cho_name_kana
    aza_flag                    BOOLEAN,                    -- ca_aza_flag

    customer_barcode            VARCHAR(100),               -- ca_customer_barcode
    effective_year_month        VARCHAR(100),               -- ca_effective_year_month (YYYYMM 想定)
    abolished_year_month        VARCHAR(100),               -- ca_abolished_year_month (YYYYMM 想定)
    search_flag                 VARCHAR(100),               -- ca_search_f

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_aflacaddr_postal_code      ON aflac_address_master (postal_code);
CREATE INDEX ix_aflacaddr_address_code     ON aflac_address_master (address_code);
CREATE INDEX ix_aflacaddr_new_address_code ON aflac_address_master (new_address_code);
CREATE INDEX ix_aflacaddr_prefecture       ON aflac_address_master (prefecture_name);

COMMENT ON TABLE aflac_address_master IS 'Aflac独自住所マスタ。大字・字・丁の階層と新旧コード、有効期間を保持';
COMMENT ON COLUMN aflac_address_master.legacy_id IS '旧 ca_id (サロゲートID)。Dataverse からの移植時のキー';
