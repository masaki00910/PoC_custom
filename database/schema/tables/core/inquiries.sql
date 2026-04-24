-- inquiries
-- Source: sample_table/table_04_ca_inquiry.md (ca_inquiry)
-- Purpose: 二次チェック以降の問い合わせ記録。
-- 変更点: ca_formid (未使用 PrimaryName) は移行しない。

CREATE TABLE inquiries (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    error_list_id       UUID NOT NULL
                        REFERENCES error_lists (id) ON DELETE CASCADE,      -- ca_error_list_management_id

    inquired_at         TIMESTAMPTZ,                                        -- ca_inquiry_datetime
    category            VARCHAR(100),                                       -- ca_inquiry_category
    content             VARCHAR(100),                                       -- ca_inquiry_content
    processing_status   VARCHAR(100),                                       -- ca_processing_status
    status_updated_at   TIMESTAMPTZ,                                        -- ca_status_updated_datetime

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_inquiries_error_list    ON inquiries (error_list_id);
CREATE INDEX ix_inquiries_inquired_at   ON inquiries (inquired_at DESC);

COMMENT ON TABLE inquiries IS '問い合わせ管理 (エラーリスト単位)';
