# テーブル定義書: ca_aflac_address_master（Aflac住所マスタ）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_aflac_address_master |
| テーブル表示名 | Aflac住所マスタ |
| エンティティセット名 | ca_aflac_address_masters |
| 説明 | Aflac独自の住所マスタテーブル。郵政住所マスタよりも詳細な住所階層（大字・字・丁名まで）を持ち、住所コードの新旧マッピング、有効期間、カスタマバーコードを管理する。UATで使用するデータのみ格納。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_aflac_address_masterid | Aflac住所マスタ | primarykey (GUID) | — | システム必須 | PK | |
| 2 | ca_id | id | nvarchar | 850 | 必須 | — | PrimaryName（サロゲートID） |
| 3 | ca_address_code | 住所コード | nvarchar | 100 | — | — | |
| 4 | ca_new_address_code | 新住所コード | nvarchar | 100 | — | — | 住所コード移行用 |
| 5 | ca_postal_code | 郵便番号 | nvarchar | 100 | — | — | |
| 6 | ca_prefecture_name | 県名 | nvarchar | 100 | — | — | |
| 7 | ca_prefecture_name_kana | 県名カナ | nvarchar | 100 | — | — | |
| 8 | ca_municipality_name | 市区郡町村名 | nvarchar | 100 | — | — | 「郡」を含む |
| 9 | ca_municipality_name_kana | 市区郡町村名カナ | nvarchar | 100 | — | — | |
| 10 | ca_oaza_common_name | 大字・通称名 | nvarchar | 100 | — | — | |
| 11 | ca_oaza_common_name_kana | 大字・通称名カナ | nvarchar | 100 | — | — | |
| 12 | ca_oaza_flag | 大字フラグ | bit | — | — | — | 1=はい, 0=いいえ |
| 13 | ca_aza_cho_name | 字・丁名 | nvarchar | 100 | — | — | |
| 14 | ca_aza_cho_name_kana | 字・丁カナ | nvarchar | 100 | — | — | |
| 15 | ca_aza_flag | 字フラグ | bit | — | — | — | 1=はい, 0=いいえ |
| 16 | ca_customer_barcode | カスタマバーコード | nvarchar | 100 | — | — | 日本郵便カスタマバーコード |
| 17 | ca_effective_year_month | 施行年月 | nvarchar | 100 | — | — | 住所の有効開始年月 |
| 18 | ca_abolished_year_month | 廃止年月 | nvarchar | 100 | — | — | 住所の廃止年月 |
| 19 | ca_search_f | 検索F | nvarchar | 100 | — | — | 検索用フラグ |

## 郵政住所マスタとの比較

| 項目 | 郵政住所マスタ | Aflac住所マスタ |
|---|---|---|
| PrimaryName | 郵便番号 | サロゲートID (ca_id) |
| 住所階層 | 都道府県 → 市区町村 → 町域 | 県 → 市区郡町村 → 大字・通称 → 字・丁 |
| 住所コード | なし | 住所コード + 新住所コード |
| 有効期間 | なし | 施行年月 / 廃止年月 |
| バーコード | なし | カスタマバーコード |
| フラグ | なし | 大字フラグ / 字フラグ |

## 外部キー

他テーブルからの参照専用マスタテーブル。明示的な Lookup 定義はないが、`ca_postal_code`（郵便番号）や `ca_address_code`（住所コード）を結合キーとして住所照合に使用される。
