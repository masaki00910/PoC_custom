# ER 図

Mermaid で記述。GitHub / VS Code Markdown プレビューで描画可能。
外部キーと論理結合を区別する。

---

## 主要リレーション (core + settings + masters)

```mermaid
erDiagram
    code_master ||--o{ document_types : "document_category_id"
    code_master ||--o{ document_types : "ai_config_id"
    code_master ||--o{ process_executions : "process_type_id"
    code_master ||--o{ process_executions : "process_status_id"

    document_types ||--o{ ai_prompts : "document_type_id"
    document_types ||--o{ error_lists : "document_type_id"
    document_types ||--o{ ai_check_results : "document_type_id"

    error_lists ||--o{ error_list_items : "error_list_id (CASCADE)"
    error_lists ||--o{ ai_check_results : "error_list_id (CASCADE)"
    error_lists ||--o{ inquiries : "error_list_id (CASCADE)"

    error_list_items ||--o{ ai_check_results : "error_list_item_id (CASCADE)"
    error_list_item_master ||--o{ error_list_items : "field_master_id"
    ai_prompts ||--o{ ai_check_results : "ai_prompt_id"

    code_master {
        UUID id PK
        VARCHAR display_name
        VARCHAR category_code
        INTEGER middle_code
    }
    document_types {
        UUID id PK
        VARCHAR document_code UK
        VARCHAR name
        UUID document_category_id FK
        UUID ai_config_id FK
    }
    ai_prompts {
        UUID id PK
        VARCHAR prompt_code UK
        INTEGER processing_order
        TEXT_array prompts
        UUID document_type_id FK
    }
    error_lists {
        UUID id PK
        VARCHAR form_code UK
        VARCHAR policy_number
        VARCHAR voucher_type
        VARCHAR report_status
        UUID document_type_id FK
        VARCHAR contact_person_entra_oid
    }
    error_list_items {
        UUID id PK
        VARCHAR item_code UK
        VARCHAR policy_number
        UUID error_list_id FK
        UUID field_master_id FK
        VARCHAR workflow_state
    }
    ai_check_results {
        UUID id PK
        VARCHAR inspection_code UK
        UUID error_list_id FK
        UUID error_list_item_id FK
        UUID ai_prompt_id FK
    }
    inquiries {
        UUID id PK
        UUID error_list_id FK
    }
    error_list_item_master {
        UUID id PK
        VARCHAR field_code UK
    }
```

---

## 論理結合 (FK なし、policy_number ベース)

```mermaid
erDiagram
    error_lists ||..o{ kanji_error_imports : "policy_number"
    error_lists ||..o{ address_error_imports : "policy_number"
    error_lists ||..o{ atlas_existing_contracts : "policy_number"
    error_lists ||..o{ atlas_registered_contracts : "policy_number"

    error_lists {
        UUID id PK
        VARCHAR policy_number
    }
    kanji_error_imports {
        UUID id PK
        VARCHAR policy_number
    }
    address_error_imports {
        UUID id PK
        VARCHAR policy_number
    }
    atlas_existing_contracts {
        UUID id PK
        VARCHAR policy_number UK
    }
    atlas_registered_contracts {
        UUID id PK
        VARCHAR policy_number UK
    }
```

注: FK を張らないのは外部取込データが一時的なものであり、本体 (`error_lists`) のライフサイクルとは独立しているため。

---

## ユーザー論理結合

```mermaid
erDiagram
    users ||..o{ error_lists : "user_name ↔ 2nd/3rd_check_owner"
    users {
        UUID id PK
        VARCHAR user_code UK
        VARCHAR user_name
        VARCHAR entra_oid
    }
    error_lists {
        UUID id PK
        VARCHAR second_check_owner_name
        VARCHAR third_check_owner_name
    }
```

`error_lists.{second|third}_check_owner_name` は `users.user_name` と論理結合する (Dataverse のラウンドロビン割り当て仕様踏襲)。
商用時は `users.entra_oid` ベースの FK 化を検討。

---

## 独立テーブル (参照元・先なし)

- `japan_post_address_master` — 住所照合用 (`postal_code` 結合)
- `aflac_address_master` — 住所照合用 (`postal_code` / `address_code` 結合)
- `system_error_logs` — エラーログ
- `audit_logs` — 監査ログ
