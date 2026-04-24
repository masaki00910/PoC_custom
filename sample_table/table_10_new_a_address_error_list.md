# テーブル定義書: new_a_address_error_list（住所エラーリスト）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | new_a_address_error_list |
| テーブル表示名 | 住所エラーリスト |
| エンティティセット名 | new_a_address_error_lists |
| 説明 | 住所エラーリストのデータを格納するテーブル。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | new_a_address_error_listid | 住所エラーリスト | primarykey (GUID) | — | システム必須 | PK | |
| 2 | new_a_policy_number | 証券番号 | nvarchar | 850 | 必須 | — | PrimaryName |
| 3 | new_a_batch_number | バッチ番号 | nvarchar | 100 | 必須 | — | |
| 4 | new_a_agency_code | 代理店コード | nvarchar | 100 | — | — | |
| 5 | new_a_document_code | 帳票コード | nvarchar | 100 | — | — | |
| 6 | new_a_group_code | 集団コード | nvarchar | 100 | — | — | |
| 7 | new_a_policyholder_name_kana | 契約者名 | nvarchar | 100 | — | — | カナ名 |
| 8 | new_a_policyholder_postal_code | 契〒 | nvarchar | 100 | — | — | 契約者郵便番号 |
| 9 | new_a_policyholder_address_kana | 契住所 | nvarchar | 1000 | — | — | 契約者住所（カナ） |
| 10 | new_a_insured_name_kana | 第一被名 | nvarchar | 100 | — | — | 第一被保険者名（カナ） |
| 11 | new_a_insured_postal_code | 被〒 | nvarchar | 100 | — | — | 被保険者郵便番号 |
| 12 | new_a_insured_address_kana | 被住所 | nvarchar | 1000 | — | — | 被保険者住所（カナ） |
| 13 | new_a_msg | MSG | nvarchar | 850 | 必須 | — | エラーメッセージ |
| 14 | new_a_sts | STS | nvarchar | 100 | — | — | ステータス文字列 |

## 外部キー

明示的な Lookup カラムは存在しない。`new_a_policy_number`（証券番号）を論理キーとして他テーブルと結合する。
