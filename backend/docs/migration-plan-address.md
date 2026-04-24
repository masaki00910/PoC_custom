# 住所フロー移行計画（Power Automate → Python）

- ステータス: **合意待ち**（本ドキュメントは実装前の計画。確認事項あり）
- 対象フロー元: `C:\work\2026\03_Aflac\20260423_PoC_custom\sample_modernflows\`
- 移行先: `C:\work\2026\03_Aflac\20260423_PoC_custom\backend\`
- 準拠: `backend/CLAUDE.md` §2 (レイヤー構成), §3 (CheckRule), §7 (監査/AI 説明可能性), §8 (外部依存)

---

## 1. 住所フローの依存関係

Power Automate 上の 3 つの住所エラー回復フローと、それらが参照する共通サブフロー。

```
F-05-005 住所回復処理 (65f74109..., orchestrator, 1763行)
 ├ 郵便番号が "000"/"*000" のときに発火
 ├ ca_id に「住所既契約突合チェック」が含まれる → 既契約DB突合 (AI) → OK なら完了
 └ 上記で回復できない or 別 ca_id → F-05-006 を呼ぶ
     │
     ▼
F-05-006 住所漢字・カナ突合 (ff08e2ed..., 1146行)
 ├ SharePoint から申込書画像取得 → AI で OCR
 ├ AI プロンプトで住所漢字と住所カナの整合チェック
 └ OK なら → F-05-008 を呼ぶ
     │
     ▼
F-05-008 住所マスタ突合 (305aa3c3..., 1384行)
 ├ AI で住所カナを分割 (都道府県/市区町村/大字/字丁)
 ├ Dataverse ca_aflac_address_masters を $filter で突合
 ├ 一致したら郵便番号を回復値として返す
 └ 郵政住所マスタにフォールバック、など複数分岐

住所固有ではない共通依存サブフロー（今回は実装せずインターフェースのみ定義）
 ├ F-05-003 点検結果登録           (9ac6ee46...)
 ├ F-05-007 文字数超過チェック     (92c9430a...)
 └ F-05-009 途中点検結果登録       (fdb5c92f...)
```

### 外部連携

| 連携先 | 用途 | 元の操作 |
|---|---|---|
| AI Builder カスタムプロンプト | OCR / 整合チェック / 住所カナ分割 / 既契約突合 | `aibuilderpredict_customprompt` (`recordId` 参照) |
| SharePoint | 申込書画像取得 | `GetFileContentByPath` |
| Dataverse | マスタ参照・登録データ照会・中間結果書き込み | `ca_aflac_address_masters` / `ca_registered_datas` / `ca_document_items` / `ca_ai_prompts` / `ca_check_results` 等 |

---

## 2. 移行スコープ（提案）

### 今回コミットに含める

1. **バックエンド骨格**
   - `pyproject.toml`（uv, Python 3.12, FastAPI, pydantic, SQLAlchemy async, pytest, ruff, mypy）
   - `app/main.py`（FastAPI 最小起動）
   - `app/config.py`（Pydantic Settings）
   - `Containerfile` / `compose.yml`（Podman）
   - `Makefile`
   - `.env.example` / `.gitignore` / `.containerignore`

2. **ドメイン基盤** (`app/domain/`)
   - `CheckRule` 抽象基底 + `Severity` / `CheckStatus`
   - エンティティ: `Application` / `CheckResult` / `CheckContext` / `ImageReference` / `AddressMasterRecord` / `RegisteredData`
   - `domain/exceptions.py`

3. **住所 CheckRule 3 本** (`app/domain/rules/address/`)
   - `postal_code_recovery.py` ← F-05-005
   - `address_kanji_kana_match.py` ← F-05-006
   - `address_master_match.py` ← F-05-008

4. **インターフェース** (`app/domain/interfaces/`)
   - `ai_client.py` — AI 呼び出し抽象（プロンプト名 + 入力 → 構造化出力）
   - `image_store.py` — 申込書画像取得
   - `address_master_repository.py` — Aflac住所マスタ / 郵政住所マスタ
   - `registered_data_repository.py` — `ca_registered_datas` 相当
   - `intermediate_result_recorder.py` — F-05-009 相当
   - `overflow_checker.py` — F-05-007 相当（抽象のみ、本体は別タスク）

5. **インフラ Fake 実装** (`app/infrastructure/`)
   - `ai/fake_client.py` — 決定的レスポンスを返す
   - `ai/prompts/` — 住所関連プロンプトをテキスト化、バージョン付き
   - `image_store/mock_store.py`
   - `db/repositories/in_memory_address_master.py`
   - `db/repositories/in_memory_registered_data.py`
   - `recorders/fake_recorder.py`
   - `overflow/noop_checker.py`

6. **単体テスト** (`tests/unit/rules/address/`)
   - 各ルールごとに 正常系 / 異常系 / 境界値
   - Fake 実装をそのまま使用（モック不要）

7. **ドキュメント**
   - `docs/check-rules-catalog.md` に住所 3 ルール追記
   - `docs/adr/0001-power-automate-migration.md` — Power Automate アクション → Python クラスの対応表、忠実度の判断

### 保留（別タスク）

- `api/` の FastAPI エンドポイント配線（`run_checks` ユースケース含む）
- Vertex AI 実装、SharePoint 実実装、DB 接続
- F-05-003 / F-05-007 / F-05-009 の**本体実装**（今回はインターフェースのみ）
- 住所以外のフロー移行

---

## 3. 確認したい設計判断

### Q1. F-05-005 の扱い
Orchestrator 的なフローで自身は単純判定しない。候補:
- **A. `PostalCodeRecoveryRule` として address/ に置き、内部で他 2 ルールを合成**（提案）
- B. `domain/orchestrator.py` に配置

→ A で進めたい。F-05-005 の「郵便番号エラー → 既契約突合 → 失敗したら漢字・カナ突合 → 住所マスタ突合」という**意思決定の階層感**を CheckRule として温存するため。

### Q2. AI プロンプトのバージョン管理
- CLAUDE.md §7 に従い `infrastructure/ai/prompts/{rule_name}_vN.txt` に配置
- Power Automate の AI Builder レコード ID はコメントで参照リンクとして残す
- `FakeAIClient` はプロンプト名 + 入力のハッシュから決定的にレスポンスを返す

→ OK で進めたい。

### Q3. 住所マスタの扱い
CLAUDE.md §8: 「マスタ管理は database/ リポジトリの責務」。
- 今回: `AddressMasterRepository` インターフェース + `InMemoryAddressMasterRepository`（テスト用、最小サンプル数件）
- 本番 DB 実装 (`SqlAlchemyAddressMasterRepository`) は database/ 側のスキーマ確定後

→ OK で進めたい。

### Q4. 監査ログ / 中間結果 (F-05-009 相当)
CLAUDE.md §7 で監査必須。
- `IntermediateResultRecorder` インターフェース + `FakeRecorder`（今回はログ出力のみ）
- 本番実装（DB 書き込み + Cloud Logging）は別タスク

→ OK で進めたい。

### Q5. 忠実度 vs Pythonic リファクタ
Power Automate のトリガー I/F は「text / text_1 / ... / text_5 の 6 個の文字列（中身は stringify された JSON）」という曖昧なもの。
- CLAUDE.md §3 の契約 `async def execute(application: Application, context: CheckContext) -> CheckResult` に一本化
- 元の `text_N` → Application / CheckContext の具体的フィールドへのマッピング表を ADR に記載
- 各 AI プロンプトの入出力スキーマ（Power Automate の `ParseJson` で定義されていたもの）を Pydantic モデルで型定義

→ OK で進めたい。

---

## 4. ファイル構成（予定）

```
backend/
├── CLAUDE.md (既存)
├── pyproject.toml
├── Containerfile
├── compose.yml
├── Makefile
├── .env.example
├── .gitignore
├── .containerignore
│
├── docs/
│   ├── migration-plan-address.md  ← このファイル
│   ├── check-rules-catalog.md
│   └── adr/
│       └── 0001-power-automate-migration.md
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── entities/
│   │   │   ├── application.py
│   │   │   ├── check_result.py
│   │   │   ├── check_context.py
│   │   │   ├── image_reference.py
│   │   │   └── master_data.py
│   │   ├── rules/
│   │   │   ├── base.py              ← CheckRule 抽象
│   │   │   └── address/
│   │   │       ├── postal_code_recovery.py
│   │   │       ├── address_kanji_kana_match.py
│   │   │       └── address_master_match.py
│   │   └── interfaces/
│   │       ├── ai_client.py
│   │       ├── image_store.py
│   │       ├── address_master_repository.py
│   │       ├── registered_data_repository.py
│   │       ├── intermediate_result_recorder.py
│   │       └── overflow_checker.py
│   │
│   └── infrastructure/
│       ├── ai/
│       │   ├── fake_client.py
│       │   └── prompts/
│       │       ├── address_kanji_kana_match_v1.txt
│       │       ├── address_kana_split_v1.txt
│       │       ├── address_existing_contract_check_v1.txt
│       │       ├── address_existing_contract_match_v1.txt
│       │       └── document_ocr_v1.txt
│       ├── image_store/
│       │   └── mock_store.py
│       ├── db/
│       │   └── repositories/
│       │       ├── in_memory_address_master.py
│       │       └── in_memory_registered_data.py
│       ├── recorders/
│       │   └── fake_recorder.py
│       └── overflow/
│           └── noop_checker.py
│
└── tests/
    ├── conftest.py
    ├── fixtures/
    │   ├── address_masters.py
    │   └── applications.py
    └── unit/
        └── rules/
            └── address/
                ├── test_postal_code_recovery.py
                ├── test_address_kanji_kana_match.py
                └── test_address_master_match.py
```

規模感: 25〜35 ファイル、テスト込みで 1500〜2500 行。

---

## 5. 次のステップ

本ドキュメントに対する承認または修正指示を受けてから実装に入る。Q1〜Q5 のうち修正希望があれば本ファイルに追記して差し戻す運用で。
