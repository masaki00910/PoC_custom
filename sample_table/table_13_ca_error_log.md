# テーブル定義書: ca_error_log（エラーログ管理）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_error_log |
| テーブル表示名 | エラーログ管理 |
| エンティティセット名 | ca_error_logs |
| 説明 | システム実行時のエラー情報を記録するテーブル。Power Automate・Copilot Studio等のシステム種別ごとにエラーコード、メッセージ、スタックトレースを保持する。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_error_logid | エラーログ管理 | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_log_id | ログID | nvarchar | 850 | 必須 | — | PrimaryName フィールド |
| 3 | ca_system_type | システム種別 | picklist | — | 必須 | — | 1=PowerAutomate, 2=CopilotStudio, 99=その他 |
| 4 | ca_error_location | エラー発生個所 | nvarchar | 100 | 必須 | — | |
| 5 | ca_error_massage | エラーメッセージ | ntext | 2000 | 必須 | — | ※カラム名のtypo: massage → message |
| 6 | ca_execution_id | 実行ID/会話ID | nvarchar | 100 | 必須 | — | |
| 7 | ca_execution_user | 実行ユーザー | nvarchar | 100 | 必須 | — | |
| 8 | ca_input_parameters | 入力パラメータ | ntext | 2000 | 必須 | — | |
| 9 | ca_stacktrace | スタックトレース | ntext | 2000 | 必須 | — | |
| 10 | ca_error_code | エラーコード | nvarchar | 100 | — | — | |
| 11 | ca_check_name | チェック内容 | nvarchar | 100 | — | — | |
| 12 | ca_business_type | 業務種別 | picklist | — | — | — | 1=漢字, 2=住所 |
| 13 | ca_policy_number | 証券番号 | nvarchar | 100 | — | — | |
| 14 | ca_item | 項目 | nvarchar | 100 | — | — | |

## picklist 値定義

### ca_system_type（システム種別）

| 値 | ラベル |
|---|---|
| 1 | PowerAutomate |
| 2 | CopilotStudio |
| 99 | その他 |

### ca_business_type（業務種別）

| 値 | ラベル |
|---|---|
| 1 | 漢字 |
| 2 | 住所 |
