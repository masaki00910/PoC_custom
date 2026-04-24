-- atlas_registered_contracts
-- Source: sample_table/table_12_ca_registered_data.md (ca_registered_data)
-- Purpose: ATLAS登録済みデータのモック格納先。補正処理後の登録結果。照合先。
-- 廃止カラム: ca_postal_code (【使用しない】と明記された PrimaryName) は移行しない。
-- 構造は atlas_existing_contracts と同一 (ca_policy_number で 1:1 対応する設計)。

CREATE TABLE atlas_registered_contracts (
    id                              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    policy_number                   VARCHAR(100) NOT NULL UNIQUE,           -- ca_policy_number
    effective_date                  DATE,                                   -- ca_effective_date

    policyholder_name_kanji         VARCHAR(100),
    policyholder_name_kana          VARCHAR(100),
    policyholder_birthday           DATE,
    policyholder_postal_code        VARCHAR(100),
    policyholder_address_kana       VARCHAR(1000),
    policyholder_address_kanji      VARCHAR(1000),

    insured_name_kanji              VARCHAR(100),
    insured_name_kana               VARCHAR(100),
    insured_birthday                DATE,
    insured_postal_code             VARCHAR(100),
    insured_address_kana            VARCHAR(1000),
    insured_address_kanji           VARCHAR(1000),

    sts                             VARCHAR(100),

    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE atlas_registered_contracts IS 'ATLAS登録データ (PoC モック)。atlas_existing_contracts の補正後';
