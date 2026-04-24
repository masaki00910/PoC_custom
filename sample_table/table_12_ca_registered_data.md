# テーブル定義書: ca_registered_data（ATLAS登録データ）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_registered_data |
| テーブル表示名 | ATLAS登録データ |
| エンティティセット名 | ca_registered_datas |
| 説明 | ATLAS登録済みのデータを格納するテーブル（モック）。補正処理後に登録された契約者・被保険者の情報を保持し、ATLAS既契約データとの差分を確認するための参照先として使用される。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_registered_dataid | ATLAS登録データ | primarykey (GUID) | — | システム必須 | PK | |
| 2 | ca_policy_number | 証券番号 | nvarchar | 100 | 必須 | — | 実質的な検索キー |
| 3 | ca_postal_code | 【使用しない】 | nvarchar | 850 | — | — | PrimaryName（レガシー。使用しないこと） |
| 4 | ca_effective_date | 契約日 | datetime | — | — | — | DateOnly / Behavior: UserLocal |
| 5 | ca_policyholder_name_kanji | 契約者氏名漢字 | nvarchar | 100 | — | — | |
| 6 | ca_policyholder_name_kana | 契約者氏名フリガナ | nvarchar | 100 | — | — | |
| 7 | ca_policyholder_birthday | 契約者_生年月日 | datetime | — | — | — | DateOnly / Behavior: UserLocal |
| 8 | ca_policyholder_postal_code | 契約者_郵便番号 | nvarchar | 100 | — | — | |
| 9 | ca_policyholder_address_kana | 契約者_住所フリガナ | nvarchar | 1000 | — | — | |
| 10 | ca_policyholder_address_kanji | 契約者_住所漢字 | nvarchar | 1000 | — | — | |
| 11 | ca_insured_name_kanji | 被保険者氏名漢字 | nvarchar | 100 | — | — | |
| 12 | ca_insured_name_kana | 被保険者氏名フリガナ | nvarchar | 100 | — | — | |
| 13 | ca_insured_birthday | 被保険者_生年月日 | datetime | — | — | — | DateOnly / Behavior: UserLocal |
| 14 | ca_insured_postal_code | 被保険者_郵便番号 | nvarchar | 100 | — | — | |
| 15 | ca_insured_address_kana | 被保険者_住所フリガナ | nvarchar | 1000 | — | — | |
| 16 | ca_insured_address_kanji | 被保険者_住所漢字 | nvarchar | 1000 | — | — | |
| 17 | ca_sts | STS | nvarchar | 100 | — | — | ステータス文字列 |

> **注意:** `ca_postal_code` は PrimaryName フィールドとして定義されているが、表示名が「【使用しない】」となっているレガシーフィールド。実際の検索キーは `ca_policy_number`（証券番号）を使用すること。

## 外部キー

明示的な Lookup カラムは存在しない。`ca_policy_number`（証券番号）を論理キーとして他テーブルと結合する。

## ATLAS既契約データとの関係

| テーブル | 役割 |
|---|---|
| ca_existing_contract_data | 処理前の既契約データ（照合元） |
| ca_registered_data（本テーブル） | 補正処理後の登録データ（照合先） |

両テーブルは同一のカラム構成を持ち、`ca_policy_number` で1:1対応する。
