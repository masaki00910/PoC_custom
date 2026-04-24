# テーブル定義書: ca_processmanagement（処理管理）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_processmanagement |
| テーブル表示名 | 処理管理 |
| エンティティセット名 | ca_processmanagements |
| 説明 | バッチ処理やフロー実行などの処理実行状況を管理するテーブル。処理種別・ステータスはコード管理を参照し、依頼者や依頼/完了日時を記録する。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | ca_processmanagementid | 処理管理 | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | ca_process_name | 処理名 | nvarchar | 850 | 必須 | — | PrimaryName フィールド |
| 3 | ca_process_status | 処理ステータス | lookup | — | — | — | FK → ca_code_management |
| 4 | ca_processtype | 処理種別 | lookup | — | — | — | FK → ca_code_management |
| 5 | ca_requester | 依頼者 | lookup | — | — | — | FK → systemuser |
| 6 | ca_requestdatetime | 依頼日時 | datetime | — | — | — | Behavior: UserLocal |
| 7 | ca_completedatetime | 完了日時 | datetime | — | — | — | Behavior: UserLocal |
| 8 | ca_description | 処理概要 | nvarchar | 100 | — | — | |
| 9 | ca_parentflow_runid | 親処理 | nvarchar | 1000 | — | — | |
| 10 | ca_executionloglink | 実行ログリンク | nvarchar | 100 | — | — | Format: URL |
| 11 | ca_resultmessage | 結果メッセージ | ntext | 2000 | — | — | |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | ca_processtype | ca_code_management | 多:1 | 処理種別コード参照 |
| 2 | ca_process_status | ca_code_management | 多:1 | 処理ステータスコード参照 |
| 3 | ca_requester | systemuser | 多:1 | 依頼者への参照 |
