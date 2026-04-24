# テーブル定義書: ca_document_selection（書類選択）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_document_selection |
| テーブル表示名 | 書類選択 |
| エンティティセット名 | ca_document_selections |
| 説明 | 処理対象となる書類の種類・プログラムを管理する設定テーブル。書類IDを自動採番で付与し、AI設定とも紐づく。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_document_selectionid | 書類選択 | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_document_id | 書類ID | nvarchar | 850 | — | — | 自動採番: `DOC-{SEQNUM:6}` / PrimaryName |
| 3 | ca_name | 書類名称 | nvarchar | 200 | 必須 | — | 書類の名称 |
| 4 | ca_program_id | プログラムID | nvarchar | 100 | — | — | |
| 5 | ca_program_name | プログラム名 | nvarchar | 100 | — | — | |
| 6 | ca_document | 書類 | lookup | — | 必須 | — | FK → ca_code_management |
| 7 | ca_aiconfig | AIConfig | lookup | — | — | — | FK → ca_code_management |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | ca_document | ca_code_management | 多:1 | 書類コード参照 |
| 2 | ca_aiconfig | ca_code_management | 多:1 | AI設定コード参照 |

## 外部キー（参照元）

| 参照元テーブル | 参照元カラム | 関係 |
|---|---|---|
| ca_ai_prompt | ca_documentid | 多:1 |
| ca_document_import | ca_document_id | 多:1 |
| ca_ai | ca_document_id | 多:1 |
