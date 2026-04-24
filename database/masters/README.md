# masters/ — マスタCSV Source of Truth

`database/CLAUDE.md` §5 に従い、マスタデータの **Source of Truth は本ディレクトリの CSV**。
DB への投入は `scripts/load_masters.py` で冪等に行う（スクリプト本体は別タスクで実装予定）。

---

## 対象テーブル

| CSV | テーブル | 件数想定 | 備考 |
|---|---|---|---|
| `code_master.csv` | `code_master` | 数十行 | 書類種別・処理ステータスなどの共通コード |
| `users.csv` | `users` | 数十行 | 業務ユーザー。PoC では手動管理 |
| `error_list_item_master.csv` | `error_list_item_master` | 百〜数百行 | エラーリストの項目定義 |
| `japan_post_address_master.csv` | `japan_post_address_master` | 全国数百万行想定 | UAT では数千行のサブセット。商用はバルクロード必須 (COPY) |
| `aflac_address_master.csv` | `aflac_address_master` | 同上 | 詳細階層を持つ独自マスタ |
| `document_types.csv` | `document_types` | 数十行 | `document_category_code` / `ai_config_code` は `code_master.category_code + middle_code` 等で解決してから挿入 |
| `ai_prompts.csv` | `ai_prompts` | 数十行 | `prompt_1..8` は DB 投入時に `prompts TEXT[]` へ束ねる |

---

## フォーマット規約（CLAUDE.md §5 準拠）

- **文字コード**: UTF-8（BOM なし）
- **改行コード**: LF（CRLF 禁止。Windows エディタ使用時は注意）
- **先頭行**: ヘッダ必須（本テンプレートのままのカラム名を使用）
- **区切り**: カンマ
- **値にカンマ・改行・ダブルクォートを含む場合**: ダブルクォート `"..."` で囲み、内部のダブルクォートは `""` でエスケープ
- **空値**: 空文字 `,,` で表現。NULL を明示したい場合も空文字とする（数値・bool も同様）
- **真偽値 (`assignment_target`, `use_knowledge` など)**: `true` / `false`（小文字）
- **日付**: `YYYY-MM-DD`
- **日時**: `YYYY-MM-DDTHH:MM:SS+09:00`（JST ISO8601）

---

## バージョン管理

- CSV ファイルは git 管理下に置き、**業務ルール変更の履歴をコミット履歴で追えるようにする**
- 1 PR = 1 業務目的の変更にする（マスタ全入れ替えは避け、差分で管理）
- PR 時のコミットメッセージに **「件数・追加・更新・削除」** を明記する

### 例
```
masters: code_master に書類種別「法人確認書」を追加

- +1 row (category_code=voucher_type, middle_code=4)
- 既存 3 行は変更なし
```

---

## DB 投入ルール

- 投入スクリプト (`scripts/load_masters.py`, 未実装) は以下を満たす前提:
  - **冪等**: 何度実行しても同じ結果（UPSERT または TRUNCATE + INSERT）
  - **トランザクション**: 全行成功 or 全ロールバック
  - **dry-run**: 差分レポート（追加・更新・削除の件数）を先に出力
  - **ID 解決**: FK 参照カラム（例: `document_types.document_category_code`）は
    スクリプト内で `code_master` をルックアップして UUID に変換

- `ai_prompts.csv` の `prompt_1..8` は投入時に `prompts TEXT[]` に集約。
  空欄はスキップし、連続埋めした配列を生成する。

---

## 大規模データの扱い

`japan_post_address_master` / `aflac_address_master` は商用時に全国データ（数百万行）を扱う。

- Git には **UAT サブセット（数千行）のみ**をコミット
- 商用データは別管理（Cloud Storage など）とし、CI でチェックサム検証
- DB 投入は `\COPY FROM` または `COPY FROM PROGRAM` で高速化
- PII は含まれないが、取り扱い方針は個別に決定する

---

## 監査

マスタ変更は **業務ルールの変更そのもの**。以下を監査対象とする:

- 誰が（git commit の author）
- いつ（commit datetime）
- 何を変更したか（diff）
- 本番反映日時（`audit_logs` テーブルへの自動記録）

本番適用は承認フロー（GitHub Actions の手動承認 workflow）を通す。
