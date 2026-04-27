# app.html 移行 TODO

ルートにあった `app.html`（単一 HTML + Babel Standalone の React デモ）を `frontend/` の
PCF + React 構成（`CLAUDE.md` §2）に 1:1 移植した段階。見た目は同一。

以下は CLAUDE.md の本来要件だが **移植第一弾では未対応**。別タスクとして順に潰す。

## 未対応項目

### 1. Fluent UI v9 への置換（CLAUDE.md §3）
- 現状: app.html のインライン style をそのまま保持
- 方針: `Button` / `Input` / `Dropdown` / `DataGrid` / `TabList` / `Textarea` / `Dialog` から
  段階的に置換。スタイルは `makeStyles` or CSS Modules に移行
- 影響範囲大（ほぼ全コンポーネント）。UI の見た目レビューを挟んで進める

### 2. MSAL.js + Entra ID 認証（CLAUDE.md §4）
- 現状: `services/auth.ts` に擬似ログイン（in-memory、localStorage 保存は削除済）
- 方針:
  - `@azure/msal-browser` を導入し `services/auth.ts` を MSAL 実装に差し替え
  - `VITE_MSAL_CLIENT_ID` / `VITE_MSAL_TENANT_ID` / `VITE_MSAL_REDIRECT_URI` を `.env` 経由で注入
  - `hooks/useAuth.ts` のインターフェースは維持（`session`/`login`/`logout`）
  - トークンは MSAL キャッシュに任せ、フロント側で Storage に保存しない
  - ユーザー識別は Entra ID の `oid` を採用（現状はダミー `userId` 文字列）

### 3. API クライアント (OpenAPI)（CLAUDE.md §5）
- 現状: `services/mock-data.ts` に直書き
- 方針:
  - `services/api-client.ts` を新設（fetch ラッパー + Bearer トークン自動付与 + 401 リトライ）
  - `types/api.generated.ts` はバックエンド `openapi.json` から生成（`npm run generate:api-types`）
  - `services/error-handler.ts` でエラーメッセージを統一（個人情報を含めない）
  - モックは `services/mock-data.ts` に残し、`VITE_ENABLE_MOCK_API=true` で切替可能にする

### 4. PCF パッケージング（CLAUDE.md §8）
- 未作成:
  - `InsuranceCheckControl/ControlManifest.Input.xml`
  - `InsuranceCheckControl/index.ts`（PCF ライフサイクル: `init`/`updateView`/`getOutputs`/`destroy`）
  - `pcfconfig.json`
  - `scripts/build-solution.sh`
  - `solution/`（Power Apps ソリューション zip 梱包用）
- 方針: React 部分が安定してから PCF 薄ラッパーを追加。`components/App.tsx` を
  PCF `container` にマウントするだけで済むよう、App.tsx は props を受け取らない設計を維持

### 5. テスト（CLAUDE.md §6）
- 作成済み:
  - `tests/unit/services/mock-llm-client.test.ts` — MockLLMClient 主要シナリオ
  - `tests/unit/services/secondary-check-mock.test.ts` — applyToolCall / fetchSecondaryCheckDetail
- 未作成:
  - `hooks/useAuth.ts` / `hooks/useSecondaryCheck.ts` の hook test（React Testing Library セットアップが必要）
  - `utils/formatters.ts` — pad / fmtDate の単体テスト
  - `components/ApplicationList` — React Testing Library で検索・ソート・ページング
  - API 呼び出しは `msw` でモック（API 連携実装後）

### 6. アクセシビリティ
- 現状: `div onClick` のタブ UI（キーボード非対応）、色だけで状態を伝えている箇所あり
- 方針: Fluent UI v9 への置換で大半は解消。残りは WCAG 2.1 AA で個別対応

### 7. CI
- 未作成: `.github/workflows/ci.yml`
- 方針: `npm run typecheck` / `npm run lint` / `npm test` / OpenAPI 差分チェック

### 8. Dev Harness 用の `tweaks-panel`
- 現状: dev-harness 側で DOM に注入（本番ビルドには含まれない）
- 方針: そのまま運用可。PCF ビルドには含めない

## 移植で CLAUDE.md から逸脱している点（要追認）

- **`components/AdminDashboard/` / `components/LoginPage/` / `components/SecondaryCheckPanel/` を新設**
  CLAUDE.md §2 のディレクトリ例には列挙されていないが、機能を保持するため追加。
  必要と判断したが、「新しいディレクトリは先に提案して合意を取る」原則に抵触するので追認依頼。
- **インライン style を暫定許容**
  CLAUDE.md §3 は「動的な値のみ例外」だが、現状は静的スタイルも大量にインライン。
  Fluent UI v9 置換タスク（項目 1）で解消予定。
- **`scripts/generate-api-types.sh` は未作成**
  `package.json` に同名スクリプトはプレースホルダ (`echo` のみ) で用意。
  backend の openapi.json が確定次第、実スクリプト化する。

## 二次チェック画面（2026-04-24 実装）

- `frontend/docs/migration-plan-secondary-check.md` の Phase 1 を実装済み
- 変更: `ApplicationDetail` を 3 ペイン化（チャット / 判断履歴 / 画像ビューア）
- 新規: `SecondaryCheckPanel/` / `useSecondaryCheck` / `MockLLMClient` / `ImageViewer` ラッパー
- 暫定: Q4=B（一次承認も `update_recovery_value` で明示記録）。DB 設計見直し時に A（NULL 解釈）へ戻す可能性あり
- 未対応: 実 LLM 接続 / backend API 実装 / 三次チェック / hook test
