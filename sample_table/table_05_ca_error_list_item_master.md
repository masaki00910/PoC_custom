# テーブル定義書: ca_error_list_item_master（エラーリスト項目マスタ）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_error_list_item_master |
| テーブル表示名 | エラーリスト項目マスタ |
| エンティティセット名 | ca_error_list_item_masters |
| 説明 | エラーリストの項目名・項目IDをマスタ管理するテーブル。詳細データ管理（ca_document_item）の項目定義や各フローから参照される。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_error_list_item_masterid | エラーリスト項目マスタ | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_field_id | 項目ID | nvarchar | 850 | 必須 | — | PrimaryName フィールド |
| 3 | ca_field_name | 項目名 | nvarchar | 100 | 必須 | — | |
| 4 | ca_error_type | エラー種別 | nvarchar | 100 | 必須 | — | |
| 5 | ca_group | グループ | nvarchar | 100 | — | — | |
| 6 | ca_attribute | 属性 | nvarchar | 100 | — | — | |

## 外部キー（参照元）

| 参照元テーブル | 参照元カラム | 関係 |
|---|---|---|
| ca_document_item | ca_field_id | 多:1 |
