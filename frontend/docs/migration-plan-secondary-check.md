# 二次チェック画面 移行計画（Adaptive Card → LLM チャット）

- ステータス: **合意済み（2026-04-24）** — Q1〜Q5 回答反映済み。実装着手可。
- 対象フロー元: `sample_modernflows/` の `S-XX-XX` 系（Copilot Studio の Skills として呼ばれる API 群）
- 移行先: `frontend/`（React）のみ。backend は**触らない**（完全フロントモック）。
- 準拠: `frontend/CLAUDE.md`, `backend/CLAUDE.md`

---

## 1. S-XX フロー全体像

`kind: "Skills"` トリガー = Copilot Studio（旧 Power Virtual Agents）から呼ばれる **バックエンド API 的なフロー**。UI は Power Apps + Copilot Studio の Adaptive Card 側に存在していた。

| フロー | 名前 | 役割 | 主な入力 | 主な出力 |
|---|---|---|---|---|
| S-01-001 | 二次チェック差配 | 2nd/3rd チェック待ちレコードに担当者をラウンドロビン割当 | mode ("2nd"/"3rd"), userMaster, errorList | 成否のみ（副作用: `ca_2nd_check_owner` 更新） |
| S-02-001 | エラーリスト一覧の取得 | 担当者向けの未処理一覧取得（**現状は空スタブ**） | — | 200/空オブジェクト |
| S-03-001 | 詳細データの取得 | 1 件の詳細（申込 + 回復候補 + 画像 URL）を取得 | list, targetNumber, businessType ("漢字"/"住所"), SharePoint URL/lib, errorList table, detailData table | `{ policyNumber, recoveryList[], url, caDocumentImportId, status }` |
| S-04-001 | ステータス更新 | 二次/三次チェックの**最終判定**を記録 | accountName, checkStage, status, caDocumentImportId, checkResult(bool), errorList | `{ message, status }` |
| S-04-002 | 詳細データの更新 | 各フィールドの**再回復値・再回復理由を上書き** | policyNumber, operatorRecoveryList[], detailData table | `{ status }` |
| S-04-003 | 問い合わせ起票 | 判断できない案件を**問い合わせ管理テーブルに起票** | caDocumentImportId, category, contents, 問い合わせ table | `{ status }` |

### S-03-001 の recoveryList スキーマ

業務種別（漢字 / 住所）でフィルタ後、回復対象のフィールドごとに 3〜5 行のエントリを返す:

```jsonc
[
  { "attribute": "...", "section": "original",        "title": "契〒",           "value": "*000",         "error_flag": "true", "check_result": "NG" },
  { "attribute": "...", "section": "first_recovery",  "title": "契〒_回復結果",   "value": "060-0001",    "error_flag": "true", "check_result": "NG" },
  { "attribute": "...", "section": "first_recovery",  "title": "契〒_回復理由",   "value": "既契約より…", "error_flag": "true", "check_result": "NG" },
  { "attribute": "...", "section": "second_recovery", "title": "契〒_再回復結果", "value": "",            "error_flag": "true", "check_result": ""   },
  { "attribute": "...", "section": "second_recovery", "title": "契〒_再回復理由", "value": "",            "error_flag": "true", "check_result": ""   }
]
```

- `original` … 申込書のスキャン読み取り値
- `first_recovery` … 一次チェック（AI エラー回復）結果
- `second_recovery` … 二次チェック担当者が上書きする対象（初期は空）

業務種別ごとの対象フィールド:
- **漢字**: 契約者名（漢字）/ 被保険者氏名（漢字）が回復対象、契約者名・被保険者名.カナ は表示のみ
- **住所**: 契〒 / 契住所 / 被〒 / 被住所 が回復対象、契約者名・第一被名 は表示のみ

---

## 2. 二次チェック担当者の業務フロー（推定）

```
[ログイン]
  ↓
[担当一覧] (S-02-001 相当: 自分に割り当てられた案件一覧)
  ↓ 案件を選択
[詳細画面] (S-03-001 で取得)
  ├─ 申込書スキャン画像を表示 (SharePoint URL から)
  ├─ 一次チェック結果 (original + first_recovery) を項目ごとに表示
  └─ 各フィールドに対して担当者が決定:
       A) 一次チェック結果を承認（そのまま採用）
       B) 値を上書き（値 + 理由を入力）→ S-04-002
       C) 判断できない → 問い合わせ起票 → S-04-003
  ↓ 全フィールド判断後
[最終判定]
  ├─ 承認 (checkResult=true) → S-04-001 で status を次工程へ
  └─ 差し戻し (checkResult=false) → S-04-001 で status を差し戻しへ
```

Power Automate では、この各ステップが **Adaptive Card** として Teams / Power Apps 上に表示され、ボタンや入力欄で判断を受け取っていた。

---

## 3. LLM チャット版の UX 提案

### 3.1 画面構成

現行 `frontend/InsuranceCheckControl/components/ApplicationDetail/ApplicationDetail.tsx` を拡張する方向。3 ペイン構成:

```
┌─────────────────┬──────────────────┬──────────────────┐
│ 1. チャット      │ 2. 判断履歴      │ 3. 申込書画像     │
│ (主操作面)       │ (tool 呼び出し    │ (参考)           │
│                  │  ログのミラー)    │                  │
│                  │                  │                  │
│ AI: 「契〒 が     │ 09:12            │ [スキャン画像]    │
│ *000 です…」     │  契〒            │                  │
│ U: 「060-0001」  │  060-0001        │ [既契約情報]      │
│ AI: 「060-0001   │  (承認)          │                  │
│ で承認します」    │                  │                  │
│                  │ 09:13            │                  │
│                  │  契住所          │                  │
│                  │  ...             │                  │
│                  │                  │                  │
│                  │ [最終: 承認/差戻] │                  │
└─────────────────┴──────────────────┴──────────────────┘
```

- 判断履歴パネルは **チャット中の LLM tool 呼び出しログのミラー**（読み取り専用）。
- 編集は必ずチャット経由 = LLM が tool を呼ぶことで反映。ユーザーが直接フィールドを操作する UI は持たない。
- 粒度（フィールド単位 / 複数一括）は LLM が会話から判断。`FieldDecision` のような固定スキーマは持たない。

### 3.2 LLM のツール（function calling / Skills 相当）

LLM に渡すツール（S-04-xxx の薄いラッパー）。Copilot Studio の Skills と同じく「特定状況で特定の動作」を定義し、LLM が会話から agentic に呼び分ける:

1. `update_recovery_value(field_name, value, reason)` — 担当者が上書き or 明示承認 → S-04-002 相当
   - 一次チェック結果を**そのまま承認**する場合も **一次回復値を value にコピーして呼ぶ**（Q4=B、暫定）
2. `file_inquiry(category, contents)` — 判断保留 → S-04-003 相当
3. `finalize_check(check_result, status)` — 全体の承認/差戻し → S-04-001 相当

`accept_first_recovery` のような「何もしない」tool は設けず、承認も `update_recovery_value` の呼び出しで明示記録する。

### 3.3 LLM との対話パターン

**開始時**: 
フロント側が S-03-001 を叩いて recoveryList を取得 → LLM に system prompt として渡す。LLM が最初のメッセージとして一次チェック結果の要約を提示。

```
AI: 証券番号 SK-2024000017 の二次チェックを始めます。
    一次チェックで以下 3 フィールドにエラーが検出され、回復案が出ています:
    
    1. 契〒: "*000" → 既契約より「060-0001」を候補提示
    2. 契住所: (空) → 既契約より「北海道札幌市中央区…」を候補提示
    3. 被住所: "ﾎｯｶｲﾄﾞｳｻｯﾎﾟﾛ…" (エラーなし、表示のみ)
    
    順に確認していきます。1件目「契〒 → 060-0001」はこれで承認してよろしいですか？
```

**フィールドごとの対話**:
- Yes/承認 → `accept_first_recovery`
- 値修正 → 自然言語から値+理由を抽出 → 確認 → `update_recovery_value`
- 判断保留/問い合わせ → `file_inquiry`
- 「全部まとめて承認」のような一括指示にも対応

**最終判定**:
全フィールドの判断が揃ったら LLM が要約 → 承認/差し戻しを確認 → `finalize_check`

### 3.4 ガードレール

- 個人情報を含むフィールド値は **LLM に常時公開**（業務上必要）。ただし個人情報をログには吐かない（CLAUDE.md §6）
- LLM 誤解による誤上書きを防ぐため、`update_recovery_value` と `finalize_check` は **「これで確定します。よろしいですか？」確認メッセージを挟むことを LLM に強制**（システムプロンプトで指示）
- 監査ログに「LLM が何を根拠にどのツールを呼んだか」を残す（reason 文字列 + raw tool call）

---

## 4. 実装スコープ提案

### 4.1 今回（PoC Phase 1）含める

**frontend/** 内のみ。backend は**触らない**。

1. `components/ApplicationDetail/` を 3 ペイン構成に拡張
   - チャット欄（既存を LLM 応答・tool call 表示対応に改修）
   - 判断履歴パネル（新規 `components/SecondaryCheckPanel/`）
   - 画像ビューア（既存を維持）
2. 新規コンポーネント:
   - `SecondaryCheckPanel/DecisionHistory.tsx` — tool 呼び出しログを時系列表示
   - `SecondaryCheckPanel/FinalDecisionBar.tsx` — 最終判定状態の表示
3. LLM クライアント (`services/llm-client.ts`) — 抽象インターフェース
   - Phase 1: `MockLLMClient`（ルールベースで tool 呼び出しを決定）
   - Phase 2: 実 LLM 実装（別タスク）
4. 状態管理 (`hooks/useSecondaryCheck.ts`):
   - recoveryList の読み込み（モックデータソース）
   - チャット履歴
   - tool 呼び出しログ（field_name, value, reason, timestamp）
   - 最終判定状態
5. 型定義 (`types/secondary-check.ts`):
   - `RecoveryListEntry` / `ToolCall` / `ToolCallLogEntry` / `FinalDecision`
6. 完全フロントモック:
   - `services/secondary-check-mock.ts` — S-03-001 応答（固定サンプル）、S-04-xxx は in-memory state に記録するだけ
7. テスト:
   - `useSecondaryCheck` の状態遷移
   - `MockLLMClient` の tool 呼び出し解釈（主要シナリオ）

### 4.2 保留（別タスク）

- S-01-001 差配（バッチ的処理、担当者画面からは呼ばれない）
- S-02-001 担当一覧（現状フロントの `ApplicationList` のモックをそのまま使用。後で差し替え）
- 三次チェック（S-04-001 の `checkStage="三次チェック"` 分岐）
- 実 LLM 接続
- backend/ 側の FastAPI スタブ・本番 API 実装
- Entra ID 認証経由の本番 API 呼び出し
- SharePoint 実画像取得（現状は `ScanPlaceholder` / `ContractPlaceholder` の SVG モック）
- **DB 設計見直し後、Q4 の方式 A（NULL 解釈）に戻す可能性の反映**

---

## 5. 設計判断（確定、2026-04-24）

| # | 論点 | 決定 | 補足 |
|---|---|---|---|
| Q1 | LLM 誘導の強さ | **LLM 主導（agentic）** | Copilot Studio の Skills と同じく「特定状況で特定の動作」を tool として定義し、LLM が会話から呼び分ける |
| Q2 | LLM の実体 | **Phase 1 = MockLLMClient** | 実 LLM (Anthropic API) 統合は別タスク |
| Q3 | 判断の粒度 | **固定スキーマなし** | `FieldDecision` のような固定構造は作らない。tool 呼び出しを時系列ログとして保持する |
| Q4 | 一次結果承認の記録 | **明示コピー（B）・暫定** | 承認も `update_recovery_value` で一次値 + 「一次チェック結果を承認」理由を書き込む。**DB 設計見直しの可能性あり、その際に A（NULL 解釈）に戻す余地を残す** |
| Q5 | バックエンド | **触らない** | frontend 内で完全モック。S-03-001 応答は固定サンプルデータ、S-04-xxx は in-memory state に tool 呼び出しログを保存するだけ |

---

## 6. ファイル構成（予定）

```
frontend/
├── InsuranceCheckControl/
│   ├── components/
│   │   ├── ApplicationDetail/
│   │   │   └── ApplicationDetail.tsx           ← 改修 (3 ペイン化)
│   │   └── SecondaryCheckPanel/                ← 新規
│   │       ├── DecisionHistory.tsx
│   │       └── FinalDecisionBar.tsx
│   ├── hooks/
│   │   └── useSecondaryCheck.ts                ← 新規
│   ├── services/
│   │   ├── llm-client.ts                       ← 新規 (抽象)
│   │   ├── mock-llm-client.ts                  ← 新規 (Phase 1 実装)
│   │   └── secondary-check-mock.ts             ← 新規 (完全フロントモック)
│   └── types/
│       └── secondary-check.ts                  ← 新規
└── docs/
    └── migration-plan-secondary-check.md       ← このファイル
```

規模感: frontend 7〜10 ファイル、合計 700〜1000 行。

---

## 7. 実装順

1. 型定義（`types/secondary-check.ts`）
2. 完全フロントモック（`services/secondary-check-mock.ts`）+ LLM 抽象（`services/llm-client.ts`）
3. `MockLLMClient`（ルールベース tool 呼び出し）
4. `useSecondaryCheck` hook
5. `SecondaryCheckPanel` UI（判断履歴 + 最終判定バー）
6. `ApplicationDetail` を 3 ペイン化
7. テスト（hook + MockLLMClient の主要シナリオ）
8. dev-harness で動作確認
