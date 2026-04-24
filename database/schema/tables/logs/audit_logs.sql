-- audit_logs
-- Source: 設計書には無いが database/CLAUDE.md §3 で必須とされる監査ログテーブル。
-- Purpose: 保険業法の記録保存義務 (7年) に対応。INSERT only。
-- 運用: 個人情報は details に含めない。保存量増に備えパーティショニング可能な構造とする。

CREATE TABLE audit_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    actor_type      VARCHAR(20)  NOT NULL
                    CHECK (actor_type IN ('user', 'system', 'ai')),
    actor_id        VARCHAR(255),                                           -- Entra oid / system name / ai model

    event_type      VARCHAR(50)  NOT NULL,                                  -- 'error_list.created', 'ai_check.started' 等
    target_type     VARCHAR(50),                                            -- 'error_list' / 'error_list_item' / ...
    target_id       VARCHAR(255),                                           -- UUID 文字列など

    details         JSONB        NOT NULL DEFAULT '{}'::JSONB               -- 個人情報は含めない
);

-- occurred_at 降順アクセスが主用途
CREATE INDEX ix_audit_logs_occurred_at  ON audit_logs (occurred_at DESC);
CREATE INDEX ix_audit_logs_event_type   ON audit_logs (event_type);
CREATE INDEX ix_audit_logs_target       ON audit_logs (target_type, target_id);
CREATE INDEX ix_audit_logs_actor        ON audit_logs (actor_type, actor_id);

-- UPDATE/DELETE 禁止のためトリガーで防止する構成を推奨 (本 DDL では定義のみ、運用制御は別途)
COMMENT ON TABLE  audit_logs IS '監査ログ。INSERT only。保存期間 7年 想定';
COMMENT ON COLUMN audit_logs.details IS '構造化詳細 (個人情報を含めない)';
