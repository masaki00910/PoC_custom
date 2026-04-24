# テーブル定義書: new_a_kanji_error_list（漢字エラーリスト）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | new_a_kanji_error_list |
| テーブル表示名 | 漢字エラーリスト |
| エンティティセット名 | new_a_kanji_error_lists |
| 説明 | 漢字のエラーリストデータを格納するテーブル。 |

## カラム定義

### 主キー・識別カラム

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 1 | new_a_kanji_error_listid | 漢字エラーリスト | primarykey (GUID) | — | システム必須 | PK |
| 2 | new_a_policy_number | 証券番号 | nvarchar | 850 | 必須 | PrimaryName |
| 3 | new_a_batch_number | バッチ番号 | nvarchar | 850 | 必須 | |
| 4 | new_a_agency_code | 代理店コード | nvarchar | 100 | — | |
| 5 | new_a_apl_status | ＡＰＬステータス | nvarchar | 100 | — | |
| 6 | new_a_application_entry_date | 申込書入力日・年月日 | nvarchar | 100 | — | |
| 7 | new_a_pol_status | ＰＯＬ登録予約ステータス | nvarchar | 100 | — | |
| 8 | new_a_document_code | 帳票コード | nvarchar | 100 | — | |
| 9 | new_a_branch_office | 課支社 | nvarchar | 100 | — | |
| 10 | new_a_group | 集団 | nvarchar | 100 | — | |
| 11 | new_a_pre_conversion_policy_number | 転換前証券番号 | nvarchar | 100 | — | |
| 12 | new_a_underwriting_required_mark | 有診査マーク | nvarchar | 100 | — | |

### 契約者

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 13 | new_a_policyholder_name_kanji | 契約者名（漢字） | nvarchar | 100 | — | |
| 14 | new_a_policyholder_name_kana | 契約者名 | nvarchar | 100 | — | カナ名 |
| 15 | new_a_policyholder_error_flag | 契約者名.エラーフラグ | nvarchar | 100 | — | |

### 被保険者

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 16 | new_a_insured_name_kanji | 被保険者氏名（漢字） | nvarchar | 100 | — | |
| 17 | new_a_insured_name_kana | 被保険者名.カナ | nvarchar | 100 | — | |
| 18 | new_a_insured_error_flag | 被保険者名.エラーフラグ | nvarchar | 100 | — | |

### 配偶者

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 19 | new_a_spouse_name_kanji | 配偶者氏名（漢字） | nvarchar | 100 | — | |
| 20 | new_a_spouse_name_kana | 配偶者名.カナ | nvarchar | 100 | — | |
| 21 | new_a_spouse_error_flag | 配偶者名.エラーフラグ | nvarchar | 100 | — | |

### 子供1〜4

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 22 | new_a_child1_name_kanji | 子供氏名（漢字）１ | nvarchar | 100 | — | |
| 23 | new_a_child1_name_kana | 子供名１.カナ | nvarchar | 100 | — | |
| 24 | new_a_child1_error_flag | 子供名１.エラーフラグ | nvarchar | 100 | — | |
| 25 | new_a_child2_name_kanji | 子供氏名（漢字）２ | nvarchar | 100 | — | |
| 26 | new_a_child2_name_kana | 子供名２.カナ | nvarchar | 100 | — | |
| 27 | new_a_child2_error_flag | 子供名２.エラーフラグ | nvarchar | 100 | — | |
| 28 | new_a_child3_name_kanji | 子供氏名（漢字）３ | nvarchar | 100 | — | |
| 29 | new_a_child3_name_kana | 子供名３.カナ | nvarchar | 100 | — | |
| 30 | new_a_child3_error_flag | 子供名３.エラーフラグ | nvarchar | 100 | — | |
| 31 | new_a_child4_name_kanji | 子供氏名（漢字）４ | nvarchar | 100 | — | |
| 32 | new_a_child4_name_kana | 子供名４.カナ | nvarchar | 100 | — | |
| 33 | new_a_child4_error_flag | 子供名４.エラーフラグ | nvarchar | 100 | — | |

### 受取人1〜4

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 34 | new_a_beneficiary_1_name_kanji | 受取人氏名（漢字）１ | nvarchar | 100 | — | |
| 35 | new_a_beneficiary_1_name_kana | 受取人名１.カナ | nvarchar | 100 | — | |
| 36 | new_a_beneficiary_1_error_flag | 受取人名１.エラーフラグ | nvarchar | 100 | — | |
| 37 | new_a_beneficiary_1_2_name_kanji | 受取人氏名（漢字）１－２ | nvarchar | 100 | — | |
| 38 | new_a_beneficiary_2_name_kanji | 受取人氏名（漢字）２ | nvarchar | 100 | — | |
| 39 | new_a_beneficiary_2_name_kana | 受取人名２.カナ | nvarchar | 100 | — | |
| 40 | new_a_beneficiary_2_error_flag | 受取人名２.エラーフラグ | nvarchar | 100 | — | |
| 41 | new_a_beneficiary_2_2_name_kanji | 受取人氏名（漢字）２－２ | nvarchar | 100 | — | |
| 42 | new_a_beneficiary_3_name_kanji | 受取人氏名（漢字）３ | nvarchar | 100 | — | |
| 43 | new_a_beneficiary_3_name_kana | 受取人名３.カナ | nvarchar | 100 | — | |
| 44 | new_a_beneficiary_3_error_flag | 受取人名３.エラーフラグ | nvarchar | 100 | — | |
| 45 | new_a_beneficiary_3_2_name_kanji | 受取人氏名（漢字）３－２ | nvarchar | 100 | — | |
| 46 | new_a_beneficiary_4_name_kanji | 受取人氏名（漢字）４ | nvarchar | 100 | — | |
| 47 | new_a_beneficiary_4_name_kana | 受取人名４.カナ | nvarchar | 100 | — | |
| 48 | new_a_beneficiary_4_error_flag | 受取人名４.エラーフラグ | nvarchar | 100 | — | |
| 49 | new_a_beneficiary_4_2_name_kanji | 受取人氏名（漢字）４－２ | nvarchar | 100 | — | |

### 介護年金特約受取人1〜2

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 50 | new_a_ltcpr_beneficiary_1_name_kanji | 介護年金受取人名（漢字）１ | nvarchar | 100 | — | |
| 51 | new_a_ltcpr_beneficiary_1_name_kana | 介護年金特約受取人１.カナ | nvarchar | 100 | — | |
| 52 | new_a_ltcpr_beneficiary_1_error_flag | 介護年金特約受取人１.エラーフラグ | nvarchar | 100 | — | |
| 53 | new_a_ltcpr_beneficiary_2_name_kanji | 介護年金受取人名（漢字）２ | nvarchar | 100 | — | |
| 54 | new_a_ltcpr_beneficiary_2_name_kana | 介護年金特約受取人２.カナ | nvarchar | 100 | — | |
| 55 | new_a_ltcpr_beneficiary_2_error_flag | 介護年金特約受取人２.エラーフラグ | nvarchar | 100 | — | |

### 指定代理請求人1〜2

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 56 | new_a_claim_agent_1_name_kanji | 指定代理請求人名（漢字）１ | nvarchar | 100 | — | |
| 57 | new_a_claim_agent_1_name_kana | 指定代理請求人１.カナ | nvarchar | 100 | — | |
| 58 | new_a_claim_agent_1_error_flag | 指定代理請求人１.エラーフラグ | nvarchar | 100 | — | |
| 59 | new_a_claim_agent_2_name_kanji | 指定代理請求人名（漢字）２ | nvarchar | 100 | — | |
| 60 | new_a_claim_agent_2_name_kana | 指定代理請求人２.カナ | nvarchar | 100 | — | |
| 61 | new_a_claim_agent_2_error_flag | 指定代理請求人２.エラーフラグ | nvarchar | 100 | — | |

### 除外者

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 備考 |
|---|---|---|---|---|---|---|
| 62 | new_a_excluded_person_name_kanji | 除外者氏名（漢字）１ | nvarchar | 100 | — | |
| 63 | new_a_excluded_person_name_kana | 除外者名１.カナ | nvarchar | 100 | — | |
| 64 | new_a_excluded_person_error_flag | 除外者名１.エラーフラグ | nvarchar | 100 | — | |

## 外部キー

明示的な Lookup カラムは存在しない。`new_a_policy_number`（証券番号）を論理キーとして他テーブルと結合する。
