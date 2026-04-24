-- kanji_error_imports
-- Source: sample_table/table_09_new_a_kanji_error_list.md (new_a_kanji_error_list)
-- Purpose: 外部システムから取り込んだ漢字エラーリストの格納先。
-- 論理キー: policy_number (error_lists.policy_number と結合)
-- 個人情報を含むため backend/CLAUDE.md §6 に従いログ出力禁止・本番接続は別途検討。

CREATE TABLE kanji_error_imports (
    id                                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identifiers
    policy_number                       VARCHAR(850) NOT NULL,              -- new_a_policy_number (PrimaryName)
    batch_number                        VARCHAR(850) NOT NULL,              -- new_a_batch_number
    agency_code                         VARCHAR(100),                       -- new_a_agency_code
    apl_status                          VARCHAR(100),                       -- new_a_apl_status
    application_entry_date              VARCHAR(100),                       -- new_a_application_entry_date
    pol_status                          VARCHAR(100),                       -- new_a_pol_status
    document_code                       VARCHAR(100),                       -- new_a_document_code
    branch_office                       VARCHAR(100),                       -- new_a_branch_office
    group_name                          VARCHAR(100),                       -- new_a_group
    pre_conversion_policy_number        VARCHAR(100),                       -- new_a_pre_conversion_policy_number
    underwriting_required_mark          VARCHAR(100),                       -- new_a_underwriting_required_mark

    -- Policyholder
    policyholder_name_kanji             VARCHAR(100),
    policyholder_name_kana              VARCHAR(100),
    policyholder_error_flag             VARCHAR(100),

    -- Insured
    insured_name_kanji                  VARCHAR(100),
    insured_name_kana                   VARCHAR(100),
    insured_error_flag                  VARCHAR(100),

    -- Spouse
    spouse_name_kanji                   VARCHAR(100),
    spouse_name_kana                    VARCHAR(100),
    spouse_error_flag                   VARCHAR(100),

    -- Children 1..4
    child1_name_kanji                   VARCHAR(100),
    child1_name_kana                    VARCHAR(100),
    child1_error_flag                   VARCHAR(100),
    child2_name_kanji                   VARCHAR(100),
    child2_name_kana                    VARCHAR(100),
    child2_error_flag                   VARCHAR(100),
    child3_name_kanji                   VARCHAR(100),
    child3_name_kana                    VARCHAR(100),
    child3_error_flag                   VARCHAR(100),
    child4_name_kanji                   VARCHAR(100),
    child4_name_kana                    VARCHAR(100),
    child4_error_flag                   VARCHAR(100),

    -- Beneficiary 1..4 (+ secondary slot)
    beneficiary_1_name_kanji            VARCHAR(100),
    beneficiary_1_name_kana             VARCHAR(100),
    beneficiary_1_error_flag            VARCHAR(100),
    beneficiary_1_2_name_kanji          VARCHAR(100),
    beneficiary_2_name_kanji            VARCHAR(100),
    beneficiary_2_name_kana             VARCHAR(100),
    beneficiary_2_error_flag            VARCHAR(100),
    beneficiary_2_2_name_kanji          VARCHAR(100),
    beneficiary_3_name_kanji            VARCHAR(100),
    beneficiary_3_name_kana             VARCHAR(100),
    beneficiary_3_error_flag            VARCHAR(100),
    beneficiary_3_2_name_kanji          VARCHAR(100),
    beneficiary_4_name_kanji            VARCHAR(100),
    beneficiary_4_name_kana             VARCHAR(100),
    beneficiary_4_error_flag            VARCHAR(100),
    beneficiary_4_2_name_kanji          VARCHAR(100),

    -- LTC pension beneficiary 1..2
    ltcpr_beneficiary_1_name_kanji      VARCHAR(100),
    ltcpr_beneficiary_1_name_kana       VARCHAR(100),
    ltcpr_beneficiary_1_error_flag      VARCHAR(100),
    ltcpr_beneficiary_2_name_kanji      VARCHAR(100),
    ltcpr_beneficiary_2_name_kana       VARCHAR(100),
    ltcpr_beneficiary_2_error_flag      VARCHAR(100),

    -- Claim agent 1..2
    claim_agent_1_name_kanji            VARCHAR(100),
    claim_agent_1_name_kana             VARCHAR(100),
    claim_agent_1_error_flag            VARCHAR(100),
    claim_agent_2_name_kanji            VARCHAR(100),
    claim_agent_2_name_kana             VARCHAR(100),
    claim_agent_2_error_flag            VARCHAR(100),

    -- Excluded person
    excluded_person_name_kanji          VARCHAR(100),
    excluded_person_name_kana           VARCHAR(100),
    excluded_person_error_flag          VARCHAR(100),

    imported_at                         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_kanji_error_imports_policy_number ON kanji_error_imports (policy_number);
CREATE INDEX ix_kanji_error_imports_batch_number  ON kanji_error_imports (batch_number);
CREATE INDEX ix_kanji_error_imports_imported_at   ON kanji_error_imports (imported_at DESC);

COMMENT ON TABLE kanji_error_imports IS '外部取込: 漢字エラーリスト。policy_number で error_lists と論理結合';
