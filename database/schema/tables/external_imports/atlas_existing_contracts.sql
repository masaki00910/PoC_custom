-- atlas_existing_contracts
-- Source: sample_table/table_11_ca_existing_contract_data.md (ca_existing_contract_data)
-- Purpose: ATLAS既契約データのモック格納先。AI点検時の回復判定の照合元。
-- 廃止カラム: ca_postal_code (【使用しない】と明記された PrimaryName) は移行しない。
-- 商用移行時はこのテーブルを削除し、backend の ContractStore 抽象実装に置き換える前提 (計画書 R2)。

CREATE TABLE atlas_existing_contracts (
    id                              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    policy_number                   VARCHAR(100) NOT NULL UNIQUE,           -- ca_policy_number (実質検索キー)
    effective_date                  DATE,                                   -- ca_effective_date (DateOnly)

    policyholder_name_kanji         VARCHAR(100),                           -- ca_policyholder_name_kanji
    policyholder_name_kana          VARCHAR(100),                           -- ca_policyholder_name_kana
    policyholder_birthday           DATE,                                   -- ca_policyholder_birthday (DateOnly)
    policyholder_postal_code        VARCHAR(100),                           -- ca_policyholder_postal_code
    policyholder_address_kana       VARCHAR(1000),                          -- ca_policyholder_address_kana
    policyholder_address_kanji      VARCHAR(1000),                          -- ca_policyholder_address_kanji

    insured_name_kanji              VARCHAR(100),                           -- ca_insured_name_kanji
    insured_name_kana               VARCHAR(100),                           -- ca_insured_name_kana
    insured_birthday                DATE,                                   -- ca_insured_birthday (DateOnly)
    insured_postal_code             VARCHAR(100),                           -- ca_insured_postal_code
    insured_address_kana            VARCHAR(1000),                          -- ca_insured_address_kana
    insured_address_kanji           VARCHAR(1000),                          -- ca_insured_address_kanji

    sts                             VARCHAR(100),                           -- ca_sts

    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 既に UNIQUE 制約で索引が貼られるので policy_number は重複インデックス不要

COMMENT ON TABLE  atlas_existing_contracts IS 'ATLAS既契約データ (PoC モック)。商用時は外部接続に差し替え';
COMMENT ON COLUMN atlas_existing_contracts.policy_number IS '実質的な検索キー (旧 ca_postal_code の PrimaryName は移行せず)';
