# テーブル定義書: ca_code_management（コード管理）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_code_management |
| テーブル表示名 | コード管理 |
| エンティティセット名 | ca_code_managements |
| 説明 | コードカテゴリ（大分類・中分類）を管理するマスタテーブル。書類選択や処理管理のコード値参照先として使用される。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_code_managementid | コード管理 | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_display_name | 表示名 | nvarchar | 850 | 必須 | — | PrimaryName フィールド |
| 3 | ca_code_category | 大分類 | nvarchar | 100 | — | — | |
| 4 | ca_code_value | 大分類コード | nvarchar | 100 | — | — | |
| 5 | ca_middle_code | 中分類コード | int | — | — | — | 範囲: −2,147,483,648 〜 2,147,483,647 |
| 6 | ca_middle_code_name | 中分類 | nvarchar | 1000 | — | — | |
| 7 | ca_key | KEY | nvarchar | 100 | — | — | |
| 8 | ca_value | VALUE | nvarchar | 4000 | — | — | |
| 9 | ca_display_order | 表示順 | nvarchar | 100 | — | — | |
| 10 | ca_contents | コンテンツ | ntext | 10000 | — | — | |
| 11 | ca_additionalinfo | Additional Info | ntext | 2000 | — | — | |
| 12 | cre00_flowai | AIフロー | nvarchar | 100 | — | — | |

## 外部キー（参照元）

このテーブルは他テーブルから参照されるマスタテーブルです。

| 参照元テーブル | 参照元カラム | 関係 |
|---|---|---|
| ca_document_selection | ca_document | 多:1 |
| ca_document_selection | ca_aiconfig | 多:1 |
| ca_processmanagement | ca_processtype | 多:1 |
| ca_processmanagement | ca_process_status | 多:1 |
