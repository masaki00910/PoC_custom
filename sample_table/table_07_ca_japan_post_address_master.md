# テーブル定義書: ca_japan_post_address_master（郵政住所マスタ）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_japan_post_address_master |
| テーブル表示名 | 郵政住所マスタ |
| エンティティセット名 | ca_japan_post_address_masters |
| 説明 | 日本郵便の公式住所データを格納するマスタテーブル。ただし、UATで使用するデータのみ格納。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_japan_post_address_masterid | 郵政住所マスタ | primarykey (GUID) | — | システム必須 | PK | |
| 2 | ca_postal_code | 郵便番号 | nvarchar | 850 | 必須 | — | PrimaryName |
| 3 | ca_postal_code_first3 | 郵便番号上3桁 | nvarchar | 100 | — | — | 範囲検索用 |
| 4 | ca_area_code | 地域コード | nvarchar | 100 | — | — | |
| 5 | ca_prefecture_name | 都道府県名 | nvarchar | 100 | — | — | |
| 6 | ca_prefecture_name_kana | 都道府県名カナ | nvarchar | 100 | — | — | |
| 7 | ca_municipality_name | 市区町村名 | nvarchar | 100 | — | — | |
| 8 | ca_municipality_name_kana | 市区町村名カナ | nvarchar | 100 | — | — | |
| 9 | ca_town_name | 町域名 | nvarchar | 100 | — | — | |
| 10 | ca_town_name_kana | 町域名カナ | nvarchar | 100 | — | — | |

## 外部キー

他テーブルからの参照専用マスタテーブル。明示的な Lookup 定義はないが、`ca_postal_code`（郵便番号）を結合キーとして住所照合に使用される。
