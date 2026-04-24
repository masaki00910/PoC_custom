# テーブル定義書: ca_document_import（エラーリスト管理）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_document_import |
| テーブル表示名 | エラーリスト管理 |
| エンティティセット名 | ca_document_imports |
| 説明 | エラーリストの業務＋証券番号単位の管理テーブル。帳票処理ステータスや二次/三次チェックの担当者を管理する。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_document_importid | ドキュメントインポート | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_formid | エラー管理ID | nvarchar | 850 | — | — | 自動採番: `F-{SEQNUM:4}` / PrimaryName |
| 3 | ca_id | ID | nvarchar | 100 | — | — | 自動採番: `{SEQNUM:4}` / 読み取り専用 |
| 4 | ca_policy_number | 証券番号 | nvarchar | 100 | 必須 | — | |
| 5 | ca_batch_number | バッチ番号 | nvarchar | 100 | 必須 | — | |
| 6 | ca_error_type | エラー種別 | nvarchar | 100 | 必須 | — | |
| 7 | ca_vouchertype | 帳票種別 | picklist | — | 必須 | — | 1=エラーリスト, 2=契約申込書, 3=意向確認書, 4=法人確認書, 5=口座振替依頼書 |
| 8 | ca_is_degimo | デジモフラグ | bit | — | 必須 | — | 1=デジモ, 0=デジモ以外 |
| 9 | ca_reportstatus | 帳票処理ステータス | picklist | — | 必須 | — | 0=OCR実行中, 1=新規作成, 2=補正済, 3=入力中, 4=起票済 |
| 10 | ca_status_updated_datetime | ステータス更新日時 | datetime | — | 必須 | — | Behavior: UserLocal |
| 11 | ca_main_document_url | メイン書類 | ntext | 20000 | 必須 | — | |
| 12 | ca_import_date | 取込み日付 | datetime | — | — | — | Behavior: DateOnly |
| 13 | ca_from_name | 取り込みファイル名 | nvarchar | 100 | — | — | |
| 14 | ca_document_url | 書類URL | nvarchar | 4000 | — | — | |
| 15 | ca_sub_document_url | サブ書類 | ntext | 20000 | — | — | |
| 16 | ca_fulltext | 帳票内容 | ntext | 1048576 | — | — | |
| 17 | ca_document_id | 書類ID | lookup | — | — | — | FK → ca_document_selection |
| 18 | ca_contactperson | 担当者 | lookup | — | — | — | FK → systemuser |
| 19 | ca_inquery_datetime | 問い合わせ日時 | datetime | — | — | — | Behavior: UserLocal |
| 20 | ca_inquiry_category | 問い合わせカテゴリ | nvarchar | 100 | — | — | |
| 21 | ca_inquiry_content | 問い合わせ内容 | nvarchar | 100 | — | — | |
| 22 | ca_processing_status | 処理ステータス | nvarchar | 100 | — | — | |
| 23 | ca_workflow_status | 【未使用】処理ステータス | picklist | — | — | — | 1=新規取込, 2=OCR処理中, 3=データ点検中・AI, 4=データ点検中・目視, 5=完了 |
| 24 | ca_2nd_check_owner | 二次チェック担当者 | nvarchar | 100 | — | — | |
| 25 | ca_2nd_check_reviewer | 二次チェック確認者 | nvarchar | 100 | — | — | |
| 26 | ca_2nd_check_result | 二次チェック判定 | bit | — | — | — | 1=NG, 0=OK |
| 27 | ca_2nd_check_completed_datetime | 二次チェック完了日時 | datetime | — | — | — | Behavior: UserLocal |
| 28 | ca_3rd_check_owner | 三次チェック担当者 | nvarchar | 100 | — | — | |
| 29 | ca_3rd_check_reviewer | 三次チェック確認者 | nvarchar | 100 | — | — | |
| 30 | ca_3rd_check_result | 三次チェック判定 | bit | — | — | — | 1=NG, 0=OK |
| 31 | ca_3rd_check_completed_datetime | 三次チェック完了日時 | datetime | — | — | — | Behavior: UserLocal |
| 32 | ca_appid | appid | nvarchar | 100 | — | — | |
| 33 | ca_input_token_sum | 入力トークン合計 | decimal | — | — | — | 計算/ロールアップフィールド |
| 34 | ca_output_token_sum | 出力トークン合計 | decimal | — | — | — | 計算/ロールアップフィールド |
| 35 | ca_ai_usage_amount | AI利用金額JPY | decimal | — | — | — | 計算フィールド (SourceType=1) |
| 36 | cre00_total_page_count | 総ページ数 | int | — | — | — | |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | ca_document_id | ca_document_selection | 多:1 | 書類選択への参照 |
| 2 | ca_contactperson | systemuser | 多:1 | 担当者への参照 |

## 外部キー（参照元）

| 参照元テーブル | 参照元カラム | 関係 |
|---|---|---|
| ca_document_item | ca_document_id | 多:1 |
| ca_ai | ca_id | 多:1 |
| ca_inquiry | ca_error_list_management_id | 多:1 |

## picklist 値定義

### ca_vouchertype（帳票種別）

| 値 | ラベル |
|---|---|
| 1 | エラーリスト |
| 2 | 契約申込書 |
| 3 | 意向確認書 |
| 4 | 法人確認書 |
| 5 | 口座振替依頼書 |

### ca_reportstatus（帳票処理ステータス）

| 値 | ラベル |
|---|---|
| 0 | OCR実行中 |
| 1 | 新規作成 |
| 2 | 補正済 |
| 3 | 入力中 |
| 4 | 起票済 |

### ca_workflow_status（【未使用】処理ステータス）

| 値 | ラベル |
|---|---|
| 1 | 新規取込 |
| 2 | OCR処理中 |
| 3 | データ点検中・AI |
| 4 | データ点検中・目視 |
| 5 | 完了 |
