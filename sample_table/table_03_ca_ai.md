# テーブル定義書: ca_ai（点検結果）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_ai |
| テーブル表示名 | 点検結果 |
| エンティティセット名 | ca_ais |
| 説明 | AI点検の実行結果を管理するテーブル。どのエラーのどの項目に対して、どのプロンプトで点検を行い、その結果と使用トークン数を記録する。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_aiid | AI点検結果 | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_inspection_id | 点検項目ID | nvarchar | 850 | — | — | 自動採番: `CHK-{SEQNUM:9}` / PrimaryName |
| 3 | ca_id | 帳票ID | lookup | — | — | — | FK → ca_document_import |
| 4 | ca_document_id | 書類ID | lookup | — | — | — | FK → ca_document_selection |
| 5 | ca_document_item_id | 項目ID | lookup | — | — | — | FK → ca_document_item |
| 6 | ca_document_item | 帳票項目 | nvarchar | 100 | — | — | |
| 7 | ca_prompt_id | プロンプトID | lookup | — | — | — | FK → ca_ai_prompt |
| 8 | ca_modelname | AIモデル名 | nvarchar | 100 | — | — | |
| 9 | ca_operationstatus | ステータス | nvarchar | 100 | — | — | |
| 10 | ca_inspection_details | 点検内容 | ntext | 10000 | — | — | |
| 11 | ca_ai_inspection_details | 点検結果 | ntext | 100000 | — | — | |
| 12 | ca_prompttokens | AI入力トークン | int | — | — | — | |
| 13 | ca_completiontokens | AI出力トークン | int | — | — | — | |
| 14 | ca_totaltokens | AI処理全体トークン | int | — | — | — | |
| 15 | ca_imagescount | AI入力画像枚数 | int | — | — | — | |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | ca_id | ca_document_import | 多:1 | エラーリスト管理への参照 |
| 2 | ca_document_id | ca_document_selection | 多:1 | 書類選択への参照 |
| 3 | ca_document_item_id | ca_document_item | 多:1 | 詳細データ管理への参照 |
| 4 | ca_prompt_id | ca_ai_prompt | 多:1 | AIプロンプトへの参照 |
