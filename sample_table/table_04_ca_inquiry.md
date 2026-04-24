# テーブル定義書: ca_inquiry（問い合わせ管理）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_inquiry |
| テーブル表示名 | 問い合わせ管理 |
| エンティティセット名 | ca_inquiries |
| 説明 | 二次チェック以降で、オペレーターが問い合わせ情報を起票した際に情報を管理するテーブル。問い合わせ日時やカテゴリ、内容、処理ステータスを記録する。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_inquiryid | 問い合わせ管理 | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_formid | 【使用しない】 | nvarchar | 850 | — | — | PrimaryName（未使用） |
| 3 | ca_error_list_management_id | 帳票ID | lookup | — | 必須 | — | FK → ca_document_import |
| 4 | ca_inquiry_datetime | 問い合わせ日時 | datetime | — | — | — | Behavior: UserLocal |
| 5 | ca_inquiry_category | 問い合わせカテゴリ | nvarchar | 100 | — | — | |
| 6 | ca_inquiry_content | 問い合わせ内容 | nvarchar | 100 | — | — | |
| 7 | ca_processing_status | 処理ステータス | nvarchar | 100 | — | — | |
| 8 | ca_status_updated_datetime | ステータス更新日時 | datetime | — | — | — | Behavior: UserLocal |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | ca_error_list_management_id | ca_document_import | 多:1 | エラーリスト管理への参照 |
