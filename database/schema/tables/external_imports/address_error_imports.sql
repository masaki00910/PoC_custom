-- address_error_imports
-- Source: sample_table/table_10_new_a_address_error_list.md (new_a_address_error_list)
-- Purpose: 外部システムから取り込んだ住所エラーリストの格納先。
-- 論理キー: policy_number (error_lists.policy_number と結合)

CREATE TABLE address_error_imports (
    id                              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    policy_number                   VARCHAR(850) NOT NULL,                  -- new_a_policy_number (PrimaryName)
    batch_number                    VARCHAR(100) NOT NULL,                  -- new_a_batch_number
    agency_code                     VARCHAR(100),                           -- new_a_agency_code
    document_code                   VARCHAR(100),                           -- new_a_document_code
    group_code                      VARCHAR(100),                           -- new_a_group_code

    policyholder_name_kana          VARCHAR(100),                           -- new_a_policyholder_name_kana
    policyholder_postal_code        VARCHAR(100),                           -- new_a_policyholder_postal_code
    policyholder_address_kana       VARCHAR(1000),                          -- new_a_policyholder_address_kana

    insured_name_kana               VARCHAR(100),                           -- new_a_insured_name_kana
    insured_postal_code             VARCHAR(100),                           -- new_a_insured_postal_code
    insured_address_kana            VARCHAR(1000),                          -- new_a_insured_address_kana

    message                         VARCHAR(850) NOT NULL,                  -- new_a_msg
    sts                             VARCHAR(100),                           -- new_a_sts

    imported_at                     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_address_error_imports_policy_number ON address_error_imports (policy_number);
CREATE INDEX ix_address_error_imports_batch_number  ON address_error_imports (batch_number);
CREATE INDEX ix_address_error_imports_imported_at   ON address_error_imports (imported_at DESC);

COMMENT ON TABLE address_error_imports IS '外部取込: 住所エラーリスト';
