# テーブル定義書: ca_reportprocessingstatus（帳票処理ステータス / BPF）

## 基本情報

| 項目 | 値 |
|---|---|
| テーブル論理名 | ca_reportprocessingstatus |
| テーブル表示名 | 帳票処理ステータス |
| エンティティセット名 | ca_reportprocessingstatuses |
| 説明 | Business Process Flow (BPF) インスタンスエンティティ。ca_document_item のワークフロー進捗を管理し、各ステージの遷移状況を追跡する。 |

## カラム定義

| No | 論理名 | 表示名 | データ型 | 最大長 | 必須 | 主キー | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | businessprocessflowinstanceid | 帳票処理ステータス | uniqueidentifier | — | システム必須 | PK | GUID |
| 2 | bpf_name | Name | nvarchar | 100 | 必須 | — | PrimaryName フィールド |
| 3 | activestageid | Active Stage | lookup | — | — | — | FK → processstage（現在のBPFステージ） |
| 4 | activestagestartedon | Active Stage Started On | datetime | — | — | — | Behavior: UserLocal |
| 5 | bpf_ca_document_itemid | Ca_Document_Item | lookup | — | — | — | FK → ca_document_item（追跡対象） |
| 6 | bpf_duration | Duration | int (duration) | — | — | — | 計算フィールド。BPF所要時間（分） |
| 7 | completedon | Completed On | datetime | — | — | — | Behavior: UserLocal |
| 8 | traversedpath | Traversed Path | nvarchar | 1250 | — | — | 通過済みステージIDのカンマ区切り |

## 外部キー（参照先）

| No | カラム論理名 | 参照先テーブル | 関係 | 説明 |
|---|---|---|---|---|
| 1 | activestageid | processstage | 多:1 | 現在のBPFステージ |
| 2 | bpf_ca_document_itemid | ca_document_item | 多:1 | BPF追跡対象エンティティ |
