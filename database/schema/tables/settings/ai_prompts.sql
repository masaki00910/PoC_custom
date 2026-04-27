-- ai_prompts
-- Source: sample_table/table_06_ca_ai_prompt.md (ca_ai_prompt)
-- Purpose: AI点検で使用するプロンプト定義。
-- 重要: ca_prompt, ca_prompt2..ca_prompt8 は配列 (prompts TEXT[]) に正規化 (計画書 R4)。
--       業務上の順序保証があるため配列でインデックス位置がそのまま実行順となる。
-- Note: ca_name (PrimaryName, 論理名「プロンプトID」) と ca_id (論理名「プロンプト名前」) は
--       Dataverse 定義書の命名が直感と逆転しているため、新スキーマでは意味に沿って割り当て直した。

CREATE TABLE ai_prompts (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business identifiers (実データに重複・空欄混在のため UNIQUE 制約は外す)
    prompt_code         VARCHAR(850) NOT NULL,              -- ca_name (PrimaryName, 論理名はプロンプトID)
    prompt_name         VARCHAR(100) NOT NULL,              -- ca_id (論理名はプロンプト名前)
    processing_order    INTEGER      NOT NULL,              -- ca_processing_order
    use_knowledge       BOOLEAN      NOT NULL DEFAULT FALSE,-- ca_knowledge

    -- Status (picklist: documenttemplate_status)
    status              VARCHAR(20) NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'inactive')), -- ca_ai

    condition_field     VARCHAR(100),                       -- ca_condition (条件項目)

    -- Lookup → FK
    document_type_id    UUID
                        REFERENCES document_types (id) ON DELETE RESTRICT, -- ca_documentid

    -- Prompt bodies (ca_prompt, ca_prompt2..ca_prompt8 を配列に正規化)
    prompts             TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],

    sample_data         TEXT,                               -- ca_sample_data

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_ai_prompts_max_slots CHECK (array_length(prompts, 1) IS NULL OR array_length(prompts, 1) <= 8)
);

CREATE INDEX ix_ai_prompts_document_type    ON ai_prompts (document_type_id);
CREATE INDEX ix_ai_prompts_order            ON ai_prompts (document_type_id, processing_order);
CREATE INDEX ix_ai_prompts_status           ON ai_prompts (status);

COMMENT ON TABLE  ai_prompts IS 'AIプロンプト定義';
COMMENT ON COLUMN ai_prompts.prompts IS '旧 ca_prompt / ca_prompt2..ca_prompt8 を配列化。最大8スロット';
COMMENT ON COLUMN ai_prompts.prompt_code IS '業務プロンプトID (旧 ca_name, Dataverse PrimaryName)';
