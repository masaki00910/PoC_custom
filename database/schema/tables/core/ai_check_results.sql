-- ai_check_results
-- Source: sample_table/table_03_ca_ai.md (ca_ai)
-- Purpose: AI点検の実行結果。どの項目にどのプロンプトでチェックを行ったか、トークン消費量を記録。
-- 監査性要件: backend/CLAUDE.md §7「同じ入力で再実行して検証できる仕組み」を満たすため
--   プロンプトバージョン・モデル名を結果側にも保存する。

CREATE TABLE ai_check_results (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifier
    inspection_code             VARCHAR(850) UNIQUE,                        -- ca_inspection_id (CHK-XXXXXXXXX, PrimaryName)

    -- References
    error_list_id               UUID NOT NULL
                                REFERENCES error_lists (id) ON DELETE CASCADE, -- ca_id (lookup)
    document_type_id            UUID
                                REFERENCES document_types (id) ON DELETE RESTRICT, -- ca_document_id (lookup)
    error_list_item_id          UUID
                                REFERENCES error_list_items (id) ON DELETE CASCADE, -- ca_document_item_id (lookup)
    ai_prompt_id                UUID
                                REFERENCES ai_prompts (id) ON DELETE RESTRICT, -- ca_prompt_id (lookup)

    item_label                  VARCHAR(100),                               -- ca_document_item
    model_name                  VARCHAR(100),                               -- ca_modelname
    operation_status            VARCHAR(100),                               -- ca_operationstatus

    inspection_details          TEXT,                                       -- ca_inspection_details (ntext 10000)
    ai_response                 TEXT,                                       -- ca_ai_inspection_details (ntext 100000)

    prompt_tokens               INTEGER,                                    -- ca_prompttokens
    completion_tokens           INTEGER,                                    -- ca_completiontokens
    total_tokens                INTEGER,                                    -- ca_totaltokens
    images_count                INTEGER,                                    -- ca_imagescount

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_ai_check_results_error_list         ON ai_check_results (error_list_id);
CREATE INDEX ix_ai_check_results_error_list_item    ON ai_check_results (error_list_item_id);
CREATE INDEX ix_ai_check_results_ai_prompt          ON ai_check_results (ai_prompt_id);
CREATE INDEX ix_ai_check_results_created_at         ON ai_check_results (created_at DESC);

COMMENT ON TABLE  ai_check_results IS 'AI点検結果 (プロンプト×項目の実行単位)';
COMMENT ON COLUMN ai_check_results.ai_response IS 'AIの生レスポンス。再現性検証のため保持 (個人情報含みうる)';
