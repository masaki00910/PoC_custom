# CLAUDE.md — Frontend

このファイルは Claude Code がこのリポジトリで作業するときに必ず最初に読む規約です。
書かれている内容はプロジェクト全体の設計判断であり、**個別タスクの実装中にこれらの方針から逸脱してはいけません**。方針自体を変える必要があると判断した場合は、コード変更の前にその旨を明示して確認を取ってください。

---

## 1. プロジェクト概要

### 目的
保険申込書の一次チェックシステムのフロントエンド。
Power Apps 上で動作する PCF (Power Apps Component Framework) コンポーネントとして実装し、内部は React で構成する。

### 位置づけ
- 現在は **PoC フェーズ** だが、**商用利用を見据えた設計・実装**を行う
- PoC で作ったコードがそのまま本番に昇格できる品質を目指す

### プロジェクト全体の規約
このリポジトリ固有ではない、プロジェクト全体の約束事:
- **コンテナエンジンは Podman に統一。Docker は使用禁止** (frontend は PCF のためコンテナ化は不要だが、backend / database の起動時に関係する)
- **3 リポジトリ間のバージョン整合は OpenAPI (backend) / スキーマ定義 (database) を契約として取る**
- **個人情報・Secret はいかなる形式でもコミットしない**

詳細は各リポジトリの CLAUDE.md を参照。

### 全体構成での役割
本システムは **3 リポジトリ構成**:
- `frontend/` — Power Apps PCF (React) (**このリポジトリ**)
- `backend/` — Python FastAPI
- `database/` — PostgreSQL スキーマ、マイグレーション、マスタデータ、IaC

```
[ユーザー (M365認証済)]
       ↓
[Power Apps + PCF(React)]  ← このリポジトリ
       ↓ Entra ID トークン付き HTTPS
       ↓
[GCP API Gateway → Cloud Run: FastAPI]  ← backend リポジトリ
       ↓
[Cloud SQL (PostgreSQL)]  ← database リポジトリが管理
```

### 採用技術
- PCF (Power Apps Component Framework)
- React 18 (関数コンポーネント + Hooks のみ)
- TypeScript (strict mode)
- MSAL.js (Microsoft Entra ID 認証)
- Fluent UI React v9 (Power Apps の UI に調和させる)

---

## 2. アーキテクチャ

### 基本方針
- **PCF はあくまで薄いラッパー**。実体は React アプリとして作る
- ビジネスロジックは極力バックエンドに寄せる。フロントは「表示」と「入力」と「API 呼び出し」に徹する
- 認証は MSAL.js で Entra ID からトークンを取得し、バックエンドに Bearer トークンで渡す

### レイヤー構成

```
InsuranceCheckControl/
├── index.ts                   ← PCF ライフサイクル (薄い)
├── components/                ← UI (プレゼンテーション)
├── hooks/                     ← 状態管理・ロジックの再利用単位
├── services/                  ← API 通信・認証 (副作用を集約)
├── types/                     ← 型定義 (OpenAPI 自動生成 + 手書き)
└── utils/                     ← 純粋関数
```

### 依存方向のルール

```
components → hooks → services
          ↘         ↗
            types, utils
```

- `components/` はビジネスロジックを持たない。データ取得や副作用は `hooks/` 経由
- `services/` は UI に依存しない。React 固有 API (useState 等) を呼ばない
- `utils/` は純粋関数のみ。副作用禁止
- 循環依存は絶対禁止

### ディレクトリ構造 (正)

```
frontend/
├── CLAUDE.md                  ← このファイル
├── README.md
├── package.json
├── tsconfig.json
├── pcfconfig.json
├── .eslintrc.json
├── .prettierrc
├── .gitignore
├── .env.example
│
├── docs/
│   ├── pcf-setup.md
│   ├── auth-flow.md
│   └── api-integration.md
│
├── InsuranceCheckControl/
│   ├── ControlManifest.Input.xml
│   ├── index.ts
│   ├── components/
│   │   ├── App.tsx
│   │   ├── ApplicationList/
│   │   │   ├── ApplicationList.tsx
│   │   │   ├── ApplicationList.test.tsx
│   │   │   └── index.ts
│   │   ├── ApplicationDetail/
│   │   ├── CheckResultView/
│   │   ├── ImageViewer/
│   │   └── common/            ← 共通UI (Button, ErrorBoundary 等)
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useAuth.ts
│   │   ├── useApplication.ts
│   │   └── useCheckResult.ts
│   ├── services/
│   │   ├── api-client.ts
│   │   ├── auth.ts
│   │   └── error-handler.ts
│   ├── types/
│   │   ├── api.generated.ts   ← OpenAPI から自動生成
│   │   ├── domain.ts          ← フロント独自の型
│   │   └── pcf.d.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   └── styles/
│
├── dev-harness/               ← PCF 外で React を単独開発するための最小Viteアプリ
│   ├── main.tsx
│   └── vite.config.ts
│
├── scripts/
│   ├── generate-api-types.sh  ← バックエンドの openapi.json から型生成
│   └── build-solution.sh
│
├── solution/                  ← Power Apps ソリューション梱包用
│
├── tests/
│   └── e2e/                   ← Playwright (将来)
│
└── .github/workflows/
    └── ci.yml
```

**新しいディレクトリを勝手に増やさない**。必要な場合は先に提案して合意を取る。

---

## 3. コーディング規約

### TypeScript
- `tsconfig.json` は `strict: true` 必須
- `any` 型の使用禁止。やむを得ない場合は `unknown` を使い、型ガードで絞る
- 型定義は `types/` に集約。コンポーネントファイル内に散らさない
- `as` による型アサーションは最小限に。使う場合は理由をコメントで明記

### React
- 関数コンポーネントのみ。クラスコンポーネント禁止
- Hooks のルール (トップレベル呼び出し、条件分岐内禁止) を守る
- 1 コンポーネント 1 ファイル 1 フォルダを原則とする
- コンポーネントのファイル名・エクスポート名は PascalCase
- Props は必ず型定義する。`any` や `object` で逃げない
- 状態管理は最小限に。グローバルステートが必要になったら先に相談 (最初は必要ない)

### スタイル
- Fluent UI v9 のコンポーネントを優先使用
- カスタム CSS は最小限に。必要なら CSS Modules または Fluent UI の `makeStyles`
- インライン style は禁止 (動的な値のみ例外)

### リンター・フォーマッタ
- ESLint + Prettier
- PR 前に `npm run lint` と `npm run format` を通す
- CI で lint エラーがあればブロック

### 命名規則
- コンポーネント: PascalCase (`ApplicationList`)
- フック: camelCase で `use` プレフィックス (`useApplication`)
- 関数・変数: camelCase
- 定数: UPPER_SNAKE_CASE
- 型・インターフェース: PascalCase。インターフェースに `I` プレフィックスをつけない

### コメント
- **なぜその実装にしたか**を書く。何をしているかはコードで表現する
- TSDoc で公開 API (hooks, services のエクスポート関数) に説明を書く

---

## 4. 認証 (MSAL.js + Entra ID)

### 基本フロー
1. PCF 初期化時、MSAL.js を初期化
2. ユーザー操作のトリガーでトークン取得 (`acquireTokenSilent` を優先)
3. API 呼び出し時、`Authorization: Bearer {token}` ヘッダに付与
4. 401 が返ってきた場合、トークン再取得 → リトライ。それでもダメなら再ログイン誘導

### 絶対ルール
- **トークンを localStorage や sessionStorage に平文で保存しない**。MSAL.js のキャッシュ機構に任せる
- **トークンをログに出力しない** (console.log 含む)
- **クライアント ID 以外の Secret をフロントに持たない**。PKCE フロー前提
- Entra ID のアプリ登録は 2 つ (フロント用 SPA / バックエンド用 API) に分離
- リダイレクト URI は Power Apps のホスト (`https://apps.powerapps.com` 等) を正確に登録

### PCF 内で MSAL.js を動かすときの注意
- Power Apps は iframe 内で動作するため、**サードパーティ Cookie / ストレージの制約を受ける**
- 問題が出たら Popup 方式 or Power Automate 経由の認証に切り替える判断が必要
- MSAL.js は `@azure/msal-browser` を使用。設定は `services/auth.ts` に集約

### ユーザー情報の扱い
- ログイン済みユーザーの情報は `hooks/useAuth.ts` 経由で取得
- ユーザー識別には Entra ID の `oid` (Object ID) を使う。メールアドレスは識別子として使わない
- ユーザー名や所属などの個人情報を UI に出す場合、必要最小限に留める

---

## 5. API 連携

### 基本方針
- バックエンドとの契約は **OpenAPI スキーマを正** とする
- 型定義はバックエンドの `openapi.json` から自動生成
- 自動生成型は `types/api.generated.ts` に配置、**手で編集しない**

### 型生成
```bash
# バックエンドが出している openapi.json から型生成
npm run generate:api-types
# = npx openapi-typescript <URL> -o InsuranceCheckControl/types/api.generated.ts
```

バックエンドのスキーマが変わったら必ず再生成する。CI で差分チェックを推奨。

### API クライアント
- `services/api-client.ts` に集約
- `fetch` ベースのラッパー。認証トークン自動付与、エラーハンドリング、リトライを実装
- 環境ごとのベース URL は `config` 経由で注入 (ハードコードしない)

### エラーハンドリング
- API エラーは `services/error-handler.ts` で統一的に処理
- UI に出すエラーメッセージは**個人情報を含まない**。「通信に失敗しました」「処理に失敗しました (エラーコード: xxx)」程度
- コンソールに詳細エラーを出すのは開発環境のみ
- ErrorBoundary でコンポーネントレベルのクラッシュをキャッチし、画面全体が真っ白にならないようにする

### 長時間処理
- AI によるチェック実行は数秒〜十数秒かかる
- 同期 API で待たず、**ジョブ ID を返す非同期 API** を使う
- フロントはジョブ ID でポーリング (またはバックエンドが WebSocket 対応したら切り替え)
- ユーザーには進捗表示 (スピナー + 推定残時間) を出す

---

## 6. テスト方針

### 基本原則
- **テストを書かないコードを main にマージしない**
- PoC でもテストを書く。書かない習慣をつけない

### テストの種類
- **単体テスト**: `*.test.tsx` を各コンポーネント・フックと同じフォルダに配置
  - フレームワーク: Vitest + React Testing Library
  - コンポーネントの描画・インタラクションをテスト
- **E2E テスト**: `tests/e2e/`
  - フレームワーク: Playwright (PoC 終盤〜商用化時に整備)
  - 主要シナリオを自動化

### カバレッジ目標
- `hooks/`, `utils/`, `services/`: 80% 以上
- `components/`: 主要インタラクションを網羅 (数値目標なし)

### モック
- API 呼び出しは `msw` (Mock Service Worker) でモック
- MSAL は `services/auth.ts` 経由で使っているので、そこをモック

---

## 7. セキュリティと個人情報の扱い

### ハードルール
- **個人情報をブラウザのログ (console) に出さない**
- **個人情報を localStorage / sessionStorage に保存しない**
- **個人情報を URL クエリパラメータに載せない** (ブラウザ履歴・アクセスログに残るため)
- **画像の URL 直接アクセスを許さない**。画像はバックエンド API 経由で取得し、一時的な blob URL で表示
- **クリップボードコピー機能を付ける場合は個人情報を除外**
- **エラーメッセージに個人情報を含めない**

### XSS 対策
- React のデフォルト (JSX はエスケープされる) に任せる
- `dangerouslySetInnerHTML` の使用禁止。やむを得ない場合は DOMPurify 経由
- URL を href に入れる場合は必ずスキーム検証 (`javascript:` を弾く)

### 画像表示
- 画像はバックエンドから byte で取得し、`URL.createObjectURL` で blob URL 化して表示
- コンポーネントのアンマウント時に `URL.revokeObjectURL` でメモリ解放
- 画像の右クリック保存を禁止する必要がある場合は、CSS + JS で制御 (完全な防御にはならない点に注意)

### ログ出力
- 本番ビルドでは `console.log` を削除 (バンドラ設定で)
- エラーログは構造化し、個人情報を含まないフィールドのみ送信
- 将来的に Application Insights 等に送る場合、送信内容を CLAUDE.md に明記

---

## 8. PCF 特有の注意事項

### ライフサイクル
- `init`: 一度だけ呼ばれる。React のマウントをここで行う
- `updateView`: プロパティ変更時に呼ばれる。React に props を渡して再レンダリング
- `getOutputs`: Power Apps に返す出力
- `destroy`: アンマウント。React の unmount、MSAL のクリーンアップを行う

### プロパティ設計
- `ControlManifest.Input.xml` に定義するプロパティは**最小限**に
- API エンドポイント URL、環境名、ユーザー ID など、**キャンバスアプリの数式から渡せると便利なもの**を入力プロパティに
- 出力プロパティは必要なときのみ追加

### React のマウント先
- PCF が提供する `container` 要素にマウント
- 複数インスタンスが同じページに存在する可能性があることを前提に設計 (グローバル状態を汚染しない)

### 開発時の動作確認
- `npm start watch` で PCF のテストハーネスが起動
- React の細かい調整は `dev-harness/` の Vite アプリで行うと速い
- 最終確認は必ず Power Apps 上で実施 (iframe 制約を含む環境差を確認するため)

### ビルド・デプロイ
- `npm run build` で PCF をビルド
- `scripts/build-solution.sh` でソリューション zip を作成
- zip を Power Apps にインポートして利用

---

## 9. Claude Code への作業指示

### 作業前に必ず確認すること
1. このファイル (`CLAUDE.md`) 全体を読む
2. 関連する `docs/` 配下のドキュメントを確認
3. 既存のコンポーネント・フックに類似のものがないか確認
4. タスクが不明瞭な場合は実装前に質問する

### 作業中の原則
- **小さく変更し、頻繁にテストを流す**
- **依存方向ルールを守る**
- **勝手に設計判断を変えない**
- **自動生成ファイル (`types/api.generated.ts`) を手で編集しない**

### コード生成時のチェックリスト
- [ ] TypeScript の型が `any` を使わずについている
- [ ] コンポーネントに Props の型定義がある
- [ ] 副作用が hooks/services に閉じ込められている
- [ ] テストを書いた
- [ ] 個人情報を console.log に出していない
- [ ] localStorage/sessionStorage に個人情報を保存していない
- [ ] トークン関連のログ出力がない
- [ ] Fluent UI v9 のコンポーネントを使っている (独自スタイルで再発明していない)
- [ ] エラーハンドリングが実装されている

### 禁止事項まとめ
- `any` 型を使わない
- `dangerouslySetInnerHTML` を使わない
- クラスコンポーネントを書かない
- トークン・個人情報をストレージに保存しない
- 個人情報を console.log に出さない
- URL クエリパラメータに個人情報を載せない
- 自動生成ファイルを手で編集しない
- 循環依存を作らない
- グローバル state を勝手に導入しない
- 設計方針を無断で変更しない

### 推奨事項まとめ
- 不明点は先に質問する
- 既存コンポーネントのパターンを踏襲する
- Fluent UI v9 を優先使用する
- 小さい PR にする
- PoC でも商用品質を意識する

---

## 10. ローカル開発環境

### バックエンド・DB との連携
フロント開発中、バックエンド API と通信確認するためにローカルで backend / database を起動することがある。

- **`backend/` と `database/` は Podman (Podman Compose) で起動する前提**
- **Docker は本プロジェクトでは使用禁止** (backend / database リポジトリの規約に準拠)
- フロント側は Node.js のみで開発可能。フロントリポジトリ内で Podman を直接使う場面はほぼない

### ローカル開発の典型的な流れ
```bash
# 1. database リポジトリで Postgres を起動
cd ../database && make db-up

# 2. backend リポジトリで API サーバを起動
cd ../backend && make dev

# 3. frontend リポジトリで開発
npm run dev          # dev-harness (Vite)
# または
npm start watch      # PCF テストハーネス
```

### API 接続先
- ローカル開発時の API ベース URL は `.env.development` で `VITE_API_BASE_URL=http://localhost:8000` 等
- Podman rootless では**ホストから `127.0.0.1` 経由で Cloud Run 代替の backend にアクセス可能**
- `host.docker.internal` は使えない。必要なら `host.containers.internal` を使う (fetch 先として使うことはほぼない)

### CORS
- backend 側で `http://localhost:*` と Power Apps のオリジンを許可する設定が必要
- CORS エラーが出たら backend リポジトリの設定を確認する

---

## 11. よく使うコマンド

```bash
# 初期セットアップ
npm install

# 開発
npm start watch          # PCF のテストハーネス
npm run dev              # dev-harness の Vite アプリ
npm test                 # Vitest
npm run lint             # ESLint
npm run format           # Prettier

# 型生成
npm run generate:api-types

# ビルド・パッケージング
npm run build
npm run build:solution   # Power Apps ソリューション zip を生成
```

詳細は `package.json` のスクリプトと `README.md` を参照。

---

## 12. 参考: PoC から商用への昇格基準

このプロジェクトは PoC だが、以下を満たせば「商用利用可」と判断できる状態を目指す:

- 主要コンポーネント・フックに単体テストがある
- 主要シナリオに E2E テストがある
- MSAL.js 認証が Power Apps 実環境で安定動作
- API 連携のエラーハンドリングが網羅されている
- 個人情報の取り扱いがセキュリティレビューを通過
- アクセシビリティ基準 (WCAG 2.1 AA) を一定レベル満たす
- 本番環境の Entra ID アプリ登録・リダイレクト URI が整備されている
- ビルド・デプロイが自動化されている

PoC 中のコードはすべて、これらの条件を満たす将来の自分を見据えて書く。