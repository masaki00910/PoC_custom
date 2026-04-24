# テーブル定義書: ca_ai_prompt（AIプロンプト）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_ai_prompt |
| テーブル表示名 | AIプロンプト |
| エンティティセット名 | ca_ai_prompts |
| 説明 | AI点検で使用するプロンプト定義を管理するテーブル。一次チェックのトリガーとなる項目にチェックに使用するプロンプトがセットされる。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_ai_promptid | AIプロンプト | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_name | プロンプトID | nvarchar | 850 | 必須 | — | PrimaryName フィールド |
| 3 | ca_id | プロンプト名前 | nvarchar | 100 | 必須 | — | |
| 4 | ca_processing_order | 処理順番 | int | — | 必須 | — | 範囲: −2,147,483,648 〜 2,147,483,647 |
| 5 | ca_knowledge | ナレッジ機能有効 | bit | — | 必須 | — | 1=はい, 0=いいえ。有効化によりトークン消費・コスト増加 |
| 6 | ca_ai | AIアクティブ | picklist | — | 必須 | — | OptionSet: documenttemplate_status |
| 7 | ca_condition | 条件項目 | nvarchar | 100 | — | — | |
| 8 | ca_documentid | 書類ID | lookup | — | — | — | FK → ca_document_selection |
| 9 | ca_prompt | プロンプト | ntext | 30000 | — | — | |
| 10 | ca_prompt2 | プロンプト2 | ntext | 30000 | — | — | |
| 11 | ca_prompt3 | プロンプト3 | ntext | 30000 | — | — | |
| 12 | ca_prompt4 | プロンプト4 | ntext | 30000 | — | — | |
| 13 | ca_prompt5 | プロンプト5 | ntext | 30000 | — | — | |
| 14 | ca_prompt6 | プロンプト6 | ntext | 30000 | — | — | |
| 15 | ca_prompt7 | プロンプト7 | ntext | 30000 | — | — | |
| 16 | ca_prompt8 | プロンプト8 | ntext | 30000 | — | — | |
| 17 | ca_sample_data | 点検内容 | ntext | 20000 | — | — | |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | ca_documentid | ca_document_selection | 多:1 | 書類選択への参照 |

## 外部キー（参照元）

| 参照元テーブル | 参照元カラム | 関係 |
|---|---|---|
| ca_ai | ca_prompt_id | 多:1 |
