-- users
-- Source: sample_table/table_18_new_a_user_master.md (new_a_user_master)
-- Purpose: 業務ユーザー (管理者・オペレータ)。チェック担当者の割り当てに使用。
-- 認証は Entra ID に統一するため entra_oid を保持。旧 statecode/statuscode は未移行 (論理削除不使用)。

CREATE TABLE users (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifiers
    user_code           VARCHAR(850) NOT NULL UNIQUE,       -- new_a_user_id (PrimaryName: 業務ユーザーID)
    user_name           VARCHAR(100) NOT NULL,              -- new_a_user_name (旧 systemuser 相当の論理結合キー)

    -- Authority (picklist -> enum string)
    authority           VARCHAR(20) NOT NULL
                        CHECK (authority IN ('admin', 'operator')),  -- new_a_authority (1=admin, 2=operator)

    -- Flags
    assignment_target   BOOLEAN     NOT NULL DEFAULT FALSE, -- ca_flag (差配対象フラグ)

    -- Entra ID (backend/CLAUDE.md §6: oid で識別)
    entra_oid           VARCHAR(255),

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX ux_users_entra_oid ON users (entra_oid) WHERE entra_oid IS NOT NULL;
CREATE INDEX ix_users_user_name ON users (user_name);
CREATE INDEX ix_users_assignment ON users (assignment_target) WHERE assignment_target = TRUE;

COMMENT ON TABLE  users IS '業務ユーザーマスタ (管理者・オペレータ)';
COMMENT ON COLUMN users.user_code       IS '業務ユーザーID (旧 new_a_user_id)';
COMMENT ON COLUMN users.user_name       IS 'ユーザー名。旧 ca_document_import.ca_2nd_check_owner 等と論理結合';
COMMENT ON COLUMN users.entra_oid       IS 'Entra ID Object ID (商用時の認証キー)';
COMMENT ON COLUMN users.assignment_target IS 'S-01 ラウンドロビン差配の対象フラグ';
