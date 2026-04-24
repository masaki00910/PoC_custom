# テーブル定義書: ca_document_item（詳細データ管理）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_document_item |
| テーブル表示名 | 詳細データ管理 |
| エンティティセット名 | ca_document_items |
| 説明 | エラーリストの各項目単位のデータを管理するテーブル。値やAI点検ステータス、各チェック段階の判定結果を保持する。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_document_itemid | ドキュメント項目管理 | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_document_item_id | 帳票項目ID | nvarchar | 850 | — | — | 自動採番: `I-{SEQNUM:4}` / PrimaryName |
| 3 | ca_policy_number | 証券番号 | nvarchar | 100 | 必須 | — | |
| 4 | ca_document_id | 帳票ID | lookup | — | — | — | FK → ca_document_import |
| 5 | ca_document_id_ai | 帳票ID_AI | nvarchar | 200 | — | — | |
| 6 | ca_document_item | 帳票項目 | nvarchar | 100 | — | — | |
| 7 | ca_document_value | 項目値 | ntext | 50000 | — | — | |
| 8 | ca_field_id | 項目ID | lookup | — | — | — | FK → ca_error_list_item_master |
| 9 | ca_error_flag | エラーフラグ | bit | — | 必須 | — | 1=エラーあり, 0=エラーなし |
| 10 | ca_ai_inspection_status | AI点検ステータス | picklist | — | — | — | OptionSet: synapselinksynapsetablecreationstate |
| 11 | ca_confidence | 信頼度スコア | nvarchar | 100 | — | — | |
| 12 | ca_reportstatus | ステータス | picklist | — | — | — | 1=新規作成, 2=補正済, 3=入力中, 4=起票済 (既定値: 1) |
| 13 | ca_status_updated_datetime | ステータス更新日時 | datetime | — | 必須 | — | Behavior: UserLocal |
| 14 | ca_processing_status | 処理ステータス | nvarchar | 100 | — | — | |
| 15 | ca_1st_check_result | 一次チェック判定 | bit | — | — | — | 1=NG, 0=OK |
| 16 | ca_1st_check_recovery_value | 一次チェック回復 | nvarchar | 1000 | — | — | |
| 17 | ca_1st_check_recovery_reason | 一次チェック回復根拠 | nvarchar | 1000 | — | — | |
| 18 | ca_2nd_check_recovery_value | 二次チェック再回復 | nvarchar | 1000 | — | — | |
| 19 | ca_2nd_check_recovery_reason | 二次チェック再回復根拠 | nvarchar | 100 | — | — | |
| 20 | ca_left | 座標Left | nvarchar | 100 | — | — | OCRバウンディングボックス |
| 21 | ca_top | 座標Top | nvarchar | 100 | — | — | OCRバウンディングボックス |
| 22 | ca_width | 座標Width | nvarchar | 100 | — | — | OCRバウンディングボックス |
| 23 | ca_height | 座標height | nvarchar | 100 | — | — | OCRバウンディングボックス |
| 24 | cre00_manual_fix_value | 帳票項目_手動補正 | ntext | 50000 | — | — | |
| 25 | cre00_page_count | 帳票ページ数 | int | — | — | — | |
| 26 | cre00_sort | ソート順 | int | — | — | — | |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | ca_document_id | ca_document_import | 多:1 | エラーリスト管理への参照 |
| 2 | ca_field_id | ca_error_list_item_master | 多:1 | エラーリスト項目マスタへの参照 |

## 外部キー（参照元）

| 参照元テーブル | 参照元カラム | 関係 |
|---|---|---|
| ca_ai | ca_document_item_id | 多:1 |
| ca_reportprocessingstatus | bpf_ca_document_itemid | 多:1 |

## picklist 値定義

### ca_reportstatus（ステータス）

| 値 | ラベル |
|---|---|
| 1 | 新規作成 |
| 2 | 補正済 |
| 3 | 入力中 |
| 4 | 起票済 |
