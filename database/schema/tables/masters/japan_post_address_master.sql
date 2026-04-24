-- japan_post_address_master
-- Source: sample_table/table_07_ca_japan_post_address_master.md
-- Purpose: 日本郵便の公式住所マスタ (UAT用データのみ)。
-- 照合キーは postal_code。商用時は全国データ取込のため COPY 前提。

CREATE TABLE japan_post_address_master (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    postal_code                 VARCHAR(850) NOT NULL,      -- ca_postal_code (PrimaryName)
    postal_code_first3          VARCHAR(100),               -- ca_postal_code_first3 (範囲検索用)
    area_code                   VARCHAR(100),               -- ca_area_code
    prefecture_name             VARCHAR(100),               -- ca_prefecture_name
    prefecture_name_kana        VARCHAR(100),               -- ca_prefecture_name_kana
    municipality_name           VARCHAR(100),               -- ca_municipality_name
    municipality_name_kana      VARCHAR(100),               -- ca_municipality_name_kana
    town_name                   VARCHAR(100),               -- ca_town_name
    town_name_kana              VARCHAR(100),               -- ca_town_name_kana

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 郵便番号は重複しうる (複数町域) ため UNIQUE にはしない
CREATE INDEX ix_jpaddr_postal_code        ON japan_post_address_master (postal_code);
CREATE INDEX ix_jpaddr_postal_code_first3 ON japan_post_address_master (postal_code_first3);
CREATE INDEX ix_jpaddr_prefecture         ON japan_post_address_master (prefecture_name);

COMMENT ON TABLE japan_post_address_master IS '日本郵便住所マスタ。住所照合の正規化キー';
