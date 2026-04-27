"""initial schema (Dataverse → PostgreSQL 初回移行)

Revision ID: 0001
Revises:
Create Date: 2026-04-24

変換元: sample_table/ の PowerPlatform (Dataverse) テーブル定義 18 本。
このマイグレーションで作成するテーブル数: 18
  masters          : code_master, users, error_list_item_master,
                     japan_post_address_master, aflac_address_master
  settings         : document_types, ai_prompts
  core             : error_lists, error_list_items, ai_check_results, inquiries
  external_imports : kanji_error_imports, address_error_imports,
                     atlas_existing_contracts, atlas_registered_contracts
  logs             : system_error_logs, process_executions, audit_logs

詳細は schema/tables/ 配下の SQL を参照。
対応表は docs/migration-from-dataverse.md 参照。
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


# 依存順 (作成順 = 後方依存なし順)。downgrade は逆順。
_CREATE_ORDER: tuple[str, ...] = (
    # masters (no FK)
    "code_master",
    "users",
    "error_list_item_master",
    "japan_post_address_master",
    "aflac_address_master",
    "corporate_type_master",
    # settings (FK -> masters)
    "document_types",
    "ai_prompts",
    # core (FK -> settings / masters)
    "error_lists",
    "error_list_items",
    "ai_check_results",
    "inquiries",
    # external imports (no FK, logical join by policy_number)
    "kanji_error_imports",
    "address_error_imports",
    "atlas_existing_contracts",
    "atlas_registered_contracts",
    # logs (FK -> code_master for process_executions)
    "system_error_logs",
    "process_executions",
    "audit_logs",
)


def upgrade() -> None:
    # 拡張: gen_random_uuid() (PG 13+ で built-in だが pgcrypto があれば確実)
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # -------- masters --------
    op.create_table(
        "code_master",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("display_name", sa.String(850), nullable=False),
        sa.Column("category_name", sa.String(100)),
        sa.Column("category_code", sa.String(100)),
        sa.Column("middle_code", sa.Integer),
        sa.Column("middle_name", sa.String(1000)),
        sa.Column("code_key", sa.String(100)),
        sa.Column("code_value", sa.String(4000)),
        sa.Column("display_order", sa.String(100)),
        sa.Column("contents", sa.Text),
        sa.Column("additional_info", sa.Text),
        sa.Column("flow_ai", sa.String(100)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute(
        "CREATE UNIQUE INDEX ux_code_master_category_middle "
        "ON code_master (category_code, middle_code) "
        "WHERE category_code IS NOT NULL AND middle_code IS NOT NULL"
    )
    op.create_index("ix_code_master_category_code", "code_master", ["category_code"])

    op.create_table(
        "users",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_code", sa.String(850), nullable=False, unique=True),
        sa.Column("user_name", sa.String(100), nullable=False),
        sa.Column("authority", sa.String(20), nullable=False),
        sa.Column("assignment_target", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("entra_oid", sa.String(255)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("authority IN ('admin', 'operator')", name="ck_users_authority"),
    )
    op.execute("CREATE UNIQUE INDEX ux_users_entra_oid ON users (entra_oid) WHERE entra_oid IS NOT NULL")
    op.create_index("ix_users_user_name", "users", ["user_name"])
    op.execute("CREATE INDEX ix_users_assignment ON users (assignment_target) WHERE assignment_target = TRUE")

    op.create_table(
        "error_list_item_master",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("field_code", sa.String(850), nullable=False, unique=True),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("error_type", sa.String(100), nullable=False),
        sa.Column("field_group", sa.String(100)),
        sa.Column("attribute", sa.String(100)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_error_list_item_master_error_type", "error_list_item_master", ["error_type"])
    op.create_index("ix_error_list_item_master_group", "error_list_item_master", ["field_group"])

    # KEN_ALL.CSV (utf_ken_all) の公式 15 カラム構成に準拠。
    # https://www.post.japanpost.jp/zipcode/dl/utf-zip.html
    op.create_table(
        "japan_post_address_master",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # KEN_ALL #1〜#9: 識別コードと住所名称
        sa.Column("local_government_code", sa.String(5)),       # #1 全国地方公共団体コード
        sa.Column("old_postal_code", sa.String(5)),             # #2 (旧)郵便番号 5桁
        sa.Column("postal_code", sa.String(7), nullable=False), # #3 郵便番号 7桁
        sa.Column("prefecture_name_kana", sa.String(200)),      # #4 都道府県名カナ (半角)
        sa.Column("municipality_name_kana", sa.String(200)),    # #5 市区町村名カナ
        sa.Column("town_name_kana", sa.Text()),                 # #6 町域名カナ (KEN_ALL は括弧内サブ町域列挙で 400+ 文字になる行あり)
        sa.Column("prefecture_name", sa.String(20)),            # #7 都道府県名 (漢字)
        sa.Column("municipality_name", sa.String(100)),         # #8 市区町村名
        sa.Column("town_name", sa.Text()),                      # #9 町域名 (#6 と同じ理由で TEXT)
        # KEN_ALL #10〜#13: フラグ
        sa.Column("multiple_postal_codes_flag", sa.SmallInteger()),  # #10
        sa.Column("koaza_banchi_flag", sa.SmallInteger()),           # #11
        sa.Column("chome_flag", sa.SmallInteger()),                  # #12
        sa.Column("multiple_towns_flag", sa.SmallInteger()),         # #13
        # KEN_ALL #14〜#15: 更新メタ
        sa.Column("update_status", sa.SmallInteger()),               # #14 0/1/2
        sa.Column("change_reason", sa.SmallInteger()),               # #15 0-6
        # 派生カラム (KEN_ALL外、範囲検索用)
        sa.Column("postal_code_first3", sa.String(3),
                  sa.Computed("LEFT(postal_code, 3)", persisted=True)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "multiple_postal_codes_flag IS NULL OR multiple_postal_codes_flag IN (0, 1)",
            name="chk_jpaddr_multi_postal_codes"),
        sa.CheckConstraint(
            "koaza_banchi_flag IS NULL OR koaza_banchi_flag IN (0, 1)",
            name="chk_jpaddr_koaza_banchi"),
        sa.CheckConstraint(
            "chome_flag IS NULL OR chome_flag IN (0, 1)",
            name="chk_jpaddr_chome"),
        sa.CheckConstraint(
            "multiple_towns_flag IS NULL OR multiple_towns_flag IN (0, 1)",
            name="chk_jpaddr_multi_towns"),
        sa.CheckConstraint(
            "update_status IS NULL OR update_status IN (0, 1, 2)",
            name="chk_jpaddr_update_status"),
        sa.CheckConstraint(
            "change_reason IS NULL OR change_reason BETWEEN 0 AND 6",
            name="chk_jpaddr_change_reason"),
    )
    op.create_index("ix_jpaddr_postal_code", "japan_post_address_master", ["postal_code"])
    op.create_index("ix_jpaddr_postal_code_first3", "japan_post_address_master", ["postal_code_first3"])
    op.create_index("ix_jpaddr_prefecture", "japan_post_address_master", ["prefecture_name"])
    op.create_index("ix_jpaddr_local_govt_code", "japan_post_address_master", ["local_government_code"])

    op.create_table(
        "aflac_address_master",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # legacy_id (旧 ca_id): Dataverse PrimaryName だが実データに重複・空欄混在のため NOT NULL/UNIQUE は付けない
        sa.Column("legacy_id", sa.String(850)),
        sa.Column("address_code", sa.String(100)),
        sa.Column("new_address_code", sa.String(100)),
        sa.Column("postal_code", sa.String(100)),
        sa.Column("prefecture_name", sa.String(100)),
        sa.Column("prefecture_name_kana", sa.String(100)),
        sa.Column("municipality_name", sa.String(100)),
        sa.Column("municipality_name_kana", sa.String(100)),
        sa.Column("oaza_common_name", sa.String(100)),
        sa.Column("oaza_common_name_kana", sa.String(100)),
        sa.Column("oaza_flag", sa.Boolean),
        sa.Column("aza_cho_name", sa.String(100)),
        sa.Column("aza_cho_name_kana", sa.String(100)),
        sa.Column("aza_flag", sa.Boolean),
        sa.Column("customer_barcode", sa.String(100)),
        sa.Column("effective_year_month", sa.String(100)),
        sa.Column("abolished_year_month", sa.String(100)),
        sa.Column("search_flag", sa.String(100)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_aflacaddr_postal_code", "aflac_address_master", ["postal_code"])
    op.create_index("ix_aflacaddr_address_code", "aflac_address_master", ["address_code"])
    op.create_index("ix_aflacaddr_new_address_code", "aflac_address_master", ["new_address_code"])
    op.create_index("ix_aflacaddr_prefecture", "aflac_address_master", ["prefecture_name"])

    # corporate_type_master: sample_table の設計書に無いが Dataverse 実データから新規追加
    op.create_table(
        "corporate_type_master",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("corporate_type", sa.String(200), nullable=False),
        sa.Column("short_name", sa.String(100)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_corporate_type_master_short_name", "corporate_type_master", ["short_name"])

    # -------- settings --------
    op.create_table(
        "document_types",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_code", sa.String(850), unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("program_code", sa.String(100)),
        sa.Column("program_name", sa.String(100)),
        sa.Column("document_category_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ai_config_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["document_category_id"], ["code_master.id"], ondelete="RESTRICT",
                                name="fk_document_types_document_category"),
        sa.ForeignKeyConstraint(["ai_config_id"], ["code_master.id"], ondelete="RESTRICT",
                                name="fk_document_types_ai_config"),
    )
    op.create_index("ix_document_types_document_category", "document_types", ["document_category_id"])
    op.create_index("ix_document_types_ai_config", "document_types", ["ai_config_id"])

    op.create_table(
        "ai_prompts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # prompt_code: 実データに重複あり (例「被保険者住所既契約突合チェック」) のため UNIQUE は付けない
        sa.Column("prompt_code", sa.String(850), nullable=False),
        sa.Column("prompt_name", sa.String(100), nullable=False),
        sa.Column("processing_order", sa.Integer, nullable=False),
        sa.Column("use_knowledge", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("condition_field", sa.String(100)),
        sa.Column("document_type_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("prompts", sa.dialects.postgresql.ARRAY(sa.Text), nullable=False,
                  server_default=sa.text("ARRAY[]::TEXT[]")),
        sa.Column("sample_data", sa.Text),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("status IN ('active', 'inactive')", name="ck_ai_prompts_status"),
        sa.CheckConstraint(
            "array_length(prompts, 1) IS NULL OR array_length(prompts, 1) <= 8",
            name="ck_ai_prompts_max_slots",
        ),
        sa.ForeignKeyConstraint(["document_type_id"], ["document_types.id"], ondelete="RESTRICT",
                                name="fk_ai_prompts_document_type"),
    )
    op.create_index("ix_ai_prompts_document_type", "ai_prompts", ["document_type_id"])
    op.create_index("ix_ai_prompts_order", "ai_prompts", ["document_type_id", "processing_order"])
    op.create_index("ix_ai_prompts_status", "ai_prompts", ["status"])

    # -------- core --------
    op.create_table(
        "error_lists",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("form_code", sa.String(850), unique=True),
        sa.Column("display_code", sa.String(100)),
        sa.Column("policy_number", sa.String(100), nullable=False),
        sa.Column("batch_number", sa.String(100), nullable=False),
        sa.Column("error_type", sa.String(100), nullable=False),
        sa.Column("voucher_type", sa.String(30), nullable=False),
        sa.Column("is_degimo", sa.Boolean, nullable=False),
        sa.Column("report_status", sa.String(20), nullable=False),
        sa.Column("status_updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("main_document_url", sa.Text, nullable=False),
        sa.Column("imported_on", sa.Date),
        sa.Column("import_file_name", sa.String(100)),
        sa.Column("document_url", sa.String(4000)),
        sa.Column("sub_document_url", sa.Text),
        sa.Column("full_text", sa.Text),
        sa.Column("document_type_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("contact_person_entra_oid", sa.String(255)),
        sa.Column("inquiry_at", sa.dialects.postgresql.TIMESTAMP(timezone=True)),
        sa.Column("inquiry_category", sa.String(100)),
        sa.Column("inquiry_content", sa.String(100)),
        sa.Column("processing_status", sa.String(100)),
        sa.Column("second_check_owner_name", sa.String(100)),
        sa.Column("second_check_reviewer_name", sa.String(100)),
        sa.Column("second_check_ng", sa.Boolean),
        sa.Column("second_check_completed_at", sa.dialects.postgresql.TIMESTAMP(timezone=True)),
        sa.Column("third_check_owner_name", sa.String(100)),
        sa.Column("third_check_reviewer_name", sa.String(100)),
        sa.Column("third_check_ng", sa.Boolean),
        sa.Column("third_check_completed_at", sa.dialects.postgresql.TIMESTAMP(timezone=True)),
        sa.Column("app_id", sa.String(100)),
        sa.Column("input_token_sum", sa.Numeric(18, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("output_token_sum", sa.Numeric(18, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("ai_usage_amount_jpy", sa.Numeric(18, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("total_page_count", sa.Integer),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "voucher_type IN ('error_list','application','intent_confirmation',"
            "'corporate_confirmation','bank_transfer_request')",
            name="ck_error_lists_voucher_type",
        ),
        sa.CheckConstraint(
            "report_status IN ('ocr_running','new','corrected','inputting','filed')",
            name="ck_error_lists_report_status",
        ),
        sa.ForeignKeyConstraint(["document_type_id"], ["document_types.id"], ondelete="RESTRICT",
                                name="fk_error_lists_document_type"),
    )
    op.create_index("ix_error_lists_policy_number", "error_lists", ["policy_number"])
    op.create_index("ix_error_lists_batch_number", "error_lists", ["batch_number"])
    op.create_index("ix_error_lists_report_status", "error_lists", ["report_status"])
    op.create_index("ix_error_lists_document_type", "error_lists", ["document_type_id"])
    op.execute("CREATE INDEX ix_error_lists_status_updated_at ON error_lists (status_updated_at DESC)")
    op.create_index("ix_error_lists_imported_on", "error_lists", ["imported_on"])
    op.create_index("ix_error_lists_contact_entra_oid", "error_lists", ["contact_person_entra_oid"])

    op.create_table(
        "error_list_items",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("item_code", sa.String(850), unique=True),
        sa.Column("policy_number", sa.String(100), nullable=False),
        sa.Column("error_list_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_master_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("ai_document_code", sa.String(200)),
        sa.Column("item_label", sa.String(100)),
        sa.Column("item_value", sa.Text),
        sa.Column("error_flag", sa.Boolean, nullable=False),
        sa.Column("ai_inspection_status", sa.String(30)),
        sa.Column("confidence_score", sa.String(100)),
        sa.Column("report_status", sa.String(20), nullable=False, server_default=sa.text("'new'")),
        sa.Column("status_updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("processing_status", sa.String(100)),
        sa.Column("first_check_ng", sa.Boolean),
        # recovery 系: 実データに長文混入 (1000 文字超過行あり) のため TEXT
        sa.Column("first_check_recovery_value", sa.Text),
        sa.Column("first_check_recovery_reason", sa.Text),
        sa.Column("second_check_recovery_value", sa.Text),
        sa.Column("second_check_recovery_reason", sa.Text),
        sa.Column("ocr_bbox_left", sa.String(100)),
        sa.Column("ocr_bbox_top", sa.String(100)),
        sa.Column("ocr_bbox_width", sa.String(100)),
        sa.Column("ocr_bbox_height", sa.String(100)),
        sa.Column("manual_fix_value", sa.Text),
        sa.Column("page_count", sa.Integer),
        sa.Column("sort_order", sa.Integer),
        sa.Column("workflow_state", sa.String(30), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("workflow_entered_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("workflow_duration_seconds", sa.Integer),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "ai_inspection_status IS NULL OR ai_inspection_status IN "
            "('pending','creating','created','failed','unknown')",
            name="ck_error_list_items_ai_inspection_status",
        ),
        sa.CheckConstraint(
            "report_status IN ('new','corrected','inputting','filed')",
            name="ck_error_list_items_report_status",
        ),
        sa.CheckConstraint(
            "workflow_state IN ('pending','ai_checking','manual_review','resolved','cancelled')",
            name="ck_error_list_items_workflow_state",
        ),
        sa.ForeignKeyConstraint(["error_list_id"], ["error_lists.id"], ondelete="CASCADE",
                                name="fk_error_list_items_error_list"),
        sa.ForeignKeyConstraint(["field_master_id"], ["error_list_item_master.id"], ondelete="RESTRICT",
                                name="fk_error_list_items_field_master"),
    )
    op.create_index("ix_error_list_items_error_list", "error_list_items", ["error_list_id"])
    op.create_index("ix_error_list_items_field_master", "error_list_items", ["field_master_id"])
    op.create_index("ix_error_list_items_policy_number", "error_list_items", ["policy_number"])
    op.create_index("ix_error_list_items_workflow_state", "error_list_items", ["workflow_state"])
    op.execute("CREATE INDEX ix_error_list_items_error_flag ON error_list_items (error_flag) WHERE error_flag = TRUE")
    op.create_index("ix_error_list_items_sort_order", "error_list_items", ["error_list_id", "sort_order"])

    op.create_table(
        "ai_check_results",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("inspection_code", sa.String(850), unique=True),
        sa.Column("error_list_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_type_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("error_list_item_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("ai_prompt_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("item_label", sa.String(100)),
        sa.Column("model_name", sa.String(100)),
        sa.Column("operation_status", sa.String(100)),
        sa.Column("inspection_details", sa.Text),
        sa.Column("ai_response", sa.Text),
        sa.Column("prompt_tokens", sa.Integer),
        sa.Column("completion_tokens", sa.Integer),
        sa.Column("total_tokens", sa.Integer),
        sa.Column("images_count", sa.Integer),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["error_list_id"], ["error_lists.id"], ondelete="CASCADE",
                                name="fk_ai_check_results_error_list"),
        sa.ForeignKeyConstraint(["document_type_id"], ["document_types.id"], ondelete="RESTRICT",
                                name="fk_ai_check_results_document_type"),
        sa.ForeignKeyConstraint(["error_list_item_id"], ["error_list_items.id"], ondelete="CASCADE",
                                name="fk_ai_check_results_error_list_item"),
        sa.ForeignKeyConstraint(["ai_prompt_id"], ["ai_prompts.id"], ondelete="RESTRICT",
                                name="fk_ai_check_results_ai_prompt"),
    )
    op.create_index("ix_ai_check_results_error_list", "ai_check_results", ["error_list_id"])
    op.create_index("ix_ai_check_results_error_list_item", "ai_check_results", ["error_list_item_id"])
    op.create_index("ix_ai_check_results_ai_prompt", "ai_check_results", ["ai_prompt_id"])
    op.execute("CREATE INDEX ix_ai_check_results_created_at ON ai_check_results (created_at DESC)")

    op.create_table(
        "inquiries",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("error_list_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inquired_at", sa.dialects.postgresql.TIMESTAMP(timezone=True)),
        sa.Column("category", sa.String(100)),
        sa.Column("content", sa.String(100)),
        sa.Column("processing_status", sa.String(100)),
        sa.Column("status_updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["error_list_id"], ["error_lists.id"], ondelete="CASCADE",
                                name="fk_inquiries_error_list"),
    )
    op.create_index("ix_inquiries_error_list", "inquiries", ["error_list_id"])
    op.execute("CREATE INDEX ix_inquiries_inquired_at ON inquiries (inquired_at DESC)")

    # -------- external_imports --------
    op.create_table(
        "kanji_error_imports",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("policy_number", sa.String(850), nullable=False),
        sa.Column("batch_number", sa.String(850), nullable=False),
        sa.Column("agency_code", sa.String(100)),
        sa.Column("apl_status", sa.String(100)),
        sa.Column("application_entry_date", sa.String(100)),
        sa.Column("pol_status", sa.String(100)),
        sa.Column("document_code", sa.String(100)),
        sa.Column("branch_office", sa.String(100)),
        sa.Column("group_name", sa.String(100)),
        sa.Column("pre_conversion_policy_number", sa.String(100)),
        sa.Column("underwriting_required_mark", sa.String(100)),
        sa.Column("policyholder_name_kanji", sa.String(100)),
        sa.Column("policyholder_name_kana", sa.String(100)),
        sa.Column("policyholder_error_flag", sa.String(100)),
        sa.Column("insured_name_kanji", sa.String(100)),
        sa.Column("insured_name_kana", sa.String(100)),
        sa.Column("insured_error_flag", sa.String(100)),
        sa.Column("spouse_name_kanji", sa.String(100)),
        sa.Column("spouse_name_kana", sa.String(100)),
        sa.Column("spouse_error_flag", sa.String(100)),
        *[sa.Column(f"child{i}_name_kanji", sa.String(100)) for i in range(1, 5)],
        *[sa.Column(f"child{i}_name_kana", sa.String(100)) for i in range(1, 5)],
        *[sa.Column(f"child{i}_error_flag", sa.String(100)) for i in range(1, 5)],
        sa.Column("beneficiary_1_name_kanji", sa.String(100)),
        sa.Column("beneficiary_1_name_kana", sa.String(100)),
        sa.Column("beneficiary_1_error_flag", sa.String(100)),
        sa.Column("beneficiary_1_2_name_kanji", sa.String(100)),
        sa.Column("beneficiary_2_name_kanji", sa.String(100)),
        sa.Column("beneficiary_2_name_kana", sa.String(100)),
        sa.Column("beneficiary_2_error_flag", sa.String(100)),
        sa.Column("beneficiary_2_2_name_kanji", sa.String(100)),
        sa.Column("beneficiary_3_name_kanji", sa.String(100)),
        sa.Column("beneficiary_3_name_kana", sa.String(100)),
        sa.Column("beneficiary_3_error_flag", sa.String(100)),
        sa.Column("beneficiary_3_2_name_kanji", sa.String(100)),
        sa.Column("beneficiary_4_name_kanji", sa.String(100)),
        sa.Column("beneficiary_4_name_kana", sa.String(100)),
        sa.Column("beneficiary_4_error_flag", sa.String(100)),
        sa.Column("beneficiary_4_2_name_kanji", sa.String(100)),
        sa.Column("ltcpr_beneficiary_1_name_kanji", sa.String(100)),
        sa.Column("ltcpr_beneficiary_1_name_kana", sa.String(100)),
        sa.Column("ltcpr_beneficiary_1_error_flag", sa.String(100)),
        sa.Column("ltcpr_beneficiary_2_name_kanji", sa.String(100)),
        sa.Column("ltcpr_beneficiary_2_name_kana", sa.String(100)),
        sa.Column("ltcpr_beneficiary_2_error_flag", sa.String(100)),
        sa.Column("claim_agent_1_name_kanji", sa.String(100)),
        sa.Column("claim_agent_1_name_kana", sa.String(100)),
        sa.Column("claim_agent_1_error_flag", sa.String(100)),
        sa.Column("claim_agent_2_name_kanji", sa.String(100)),
        sa.Column("claim_agent_2_name_kana", sa.String(100)),
        sa.Column("claim_agent_2_error_flag", sa.String(100)),
        sa.Column("excluded_person_name_kanji", sa.String(100)),
        sa.Column("excluded_person_name_kana", sa.String(100)),
        sa.Column("excluded_person_error_flag", sa.String(100)),
        sa.Column("imported_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_kanji_error_imports_policy_number", "kanji_error_imports", ["policy_number"])
    op.create_index("ix_kanji_error_imports_batch_number", "kanji_error_imports", ["batch_number"])
    op.execute("CREATE INDEX ix_kanji_error_imports_imported_at ON kanji_error_imports (imported_at DESC)")

    op.create_table(
        "address_error_imports",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("policy_number", sa.String(850), nullable=False),
        sa.Column("batch_number", sa.String(100), nullable=False),
        sa.Column("agency_code", sa.String(100)),
        sa.Column("document_code", sa.String(100)),
        sa.Column("group_code", sa.String(100)),
        sa.Column("policyholder_name_kana", sa.String(100)),
        sa.Column("policyholder_postal_code", sa.String(100)),
        sa.Column("policyholder_address_kana", sa.String(1000)),
        sa.Column("insured_name_kana", sa.String(100)),
        sa.Column("insured_postal_code", sa.String(100)),
        sa.Column("insured_address_kana", sa.String(1000)),
        sa.Column("message", sa.String(850), nullable=False),
        sa.Column("sts", sa.String(100)),
        sa.Column("imported_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_address_error_imports_policy_number", "address_error_imports", ["policy_number"])
    op.create_index("ix_address_error_imports_batch_number", "address_error_imports", ["batch_number"])
    op.execute("CREATE INDEX ix_address_error_imports_imported_at ON address_error_imports (imported_at DESC)")

    for atlas_table in ("atlas_existing_contracts", "atlas_registered_contracts"):
        op.create_table(
            atlas_table,
            sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                      server_default=sa.text("gen_random_uuid()")),
            sa.Column("policy_number", sa.String(100), nullable=False, unique=True),
            sa.Column("effective_date", sa.Date),
            sa.Column("policyholder_name_kanji", sa.String(100)),
            sa.Column("policyholder_name_kana", sa.String(100)),
            sa.Column("policyholder_birthday", sa.Date),
            sa.Column("policyholder_postal_code", sa.String(100)),
            sa.Column("policyholder_address_kana", sa.String(1000)),
            sa.Column("policyholder_address_kanji", sa.String(1000)),
            sa.Column("insured_name_kanji", sa.String(100)),
            sa.Column("insured_name_kana", sa.String(100)),
            sa.Column("insured_birthday", sa.Date),
            sa.Column("insured_postal_code", sa.String(100)),
            sa.Column("insured_address_kana", sa.String(1000)),
            sa.Column("insured_address_kanji", sa.String(1000)),
            sa.Column("sts", sa.String(100)),
            sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                      nullable=False, server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                      nullable=False, server_default=sa.text("NOW()")),
        )

    # -------- logs --------
    op.create_table(
        "system_error_logs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("log_code", sa.String(850), nullable=False),
        sa.Column("system_type", sa.String(20), nullable=False),
        sa.Column("error_location", sa.String(100), nullable=False),
        sa.Column("error_message", sa.Text, nullable=False),
        sa.Column("execution_id", sa.String(100), nullable=False),
        sa.Column("execution_user", sa.String(100), nullable=False),
        sa.Column("input_parameters", sa.Text, nullable=False),
        sa.Column("stacktrace", sa.Text, nullable=False),
        sa.Column("error_code", sa.String(100)),
        sa.Column("check_name", sa.String(100)),
        sa.Column("business_type", sa.String(20)),
        sa.Column("policy_number", sa.String(100)),
        sa.Column("item", sa.String(100)),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "system_type IN ('power_automate','copilot_studio','other')",
            name="ck_system_error_logs_system_type",
        ),
        sa.CheckConstraint(
            "business_type IS NULL OR business_type IN ('kanji','address')",
            name="ck_system_error_logs_business_type",
        ),
    )
    op.create_index("ix_system_error_logs_system_type", "system_error_logs", ["system_type"])
    op.create_index("ix_system_error_logs_business_type", "system_error_logs", ["business_type"])
    op.create_index("ix_system_error_logs_policy_number", "system_error_logs", ["policy_number"])
    op.execute("CREATE INDEX ix_system_error_logs_created_at ON system_error_logs (created_at DESC)")

    op.create_table(
        "process_executions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("process_name", sa.String(850), nullable=False),
        sa.Column("process_type_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("process_status_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("requester_entra_oid", sa.String(255)),
        sa.Column("requested_at", sa.dialects.postgresql.TIMESTAMP(timezone=True)),
        sa.Column("completed_at", sa.dialects.postgresql.TIMESTAMP(timezone=True)),
        sa.Column("description", sa.String(100)),
        sa.Column("parent_flow_run_id", sa.String(1000)),
        sa.Column("execution_log_url", sa.String(2000)),
        sa.Column("result_message", sa.Text),
        sa.Column("created_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["process_type_id"], ["code_master.id"], ondelete="RESTRICT",
                                name="fk_process_executions_process_type"),
        sa.ForeignKeyConstraint(["process_status_id"], ["code_master.id"], ondelete="RESTRICT",
                                name="fk_process_executions_process_status"),
    )
    op.create_index("ix_process_executions_process_type", "process_executions", ["process_type_id"])
    op.create_index("ix_process_executions_process_status", "process_executions", ["process_status_id"])
    op.create_index("ix_process_executions_requester", "process_executions", ["requester_entra_oid"])
    op.execute("CREATE INDEX ix_process_executions_requested_at ON process_executions (requested_at DESC)")

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("occurred_at", sa.dialects.postgresql.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("actor_id", sa.String(255)),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50)),
        sa.Column("target_id", sa.String(255)),
        sa.Column("details", sa.dialects.postgresql.JSONB,
                  nullable=False, server_default=sa.text("'{}'::JSONB")),
        sa.CheckConstraint(
            "actor_type IN ('user','system','ai')",
            name="ck_audit_logs_actor_type",
        ),
    )
    op.execute("CREATE INDEX ix_audit_logs_occurred_at ON audit_logs (occurred_at DESC)")
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"])
    op.create_index("ix_audit_logs_target", "audit_logs", ["target_type", "target_id"])
    op.create_index("ix_audit_logs_actor", "audit_logs", ["actor_type", "actor_id"])


def downgrade() -> None:
    # IF EXISTS をつけて、テーブル追加の途中状態でも downgrade できるようにする
    for table in reversed(_CREATE_ORDER):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    # pgcrypto は他用途で使用している可能性があるため DROP EXTENSION は行わない
