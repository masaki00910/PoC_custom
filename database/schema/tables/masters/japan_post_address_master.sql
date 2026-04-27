-- japan_post_address_master
-- Source of truth: 日本郵便「読み仮名データの促音・拗音を小書きで表記するもの」 utf_ken_all.csv (UTF-8)
--   https://www.post.japanpost.jp/zipcode/dl/utf-zip.html
-- 列構成は KEN_ALL.CSV の公式 15 カラムに準拠する。派生列 postal_code_first3 のみ追加。
-- 商用時は全国データ取込のため COPY 前提。

CREATE TABLE japan_post_address_master (
    id                          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),

    -- KEN_ALL #1〜#9: 識別コードと住所名称
    local_government_code       VARCHAR(5),                  -- #1 全国地方公共団体コード (JIS X0401+X0402)
    old_postal_code             VARCHAR(5),                  -- #2 (旧)郵便番号 (5桁)
    postal_code                 VARCHAR(7) NOT NULL,         -- #3 郵便番号 (7桁)
    prefecture_name_kana        VARCHAR(200),                -- #4 都道府県名カナ (半角カナ)
    municipality_name_kana      VARCHAR(200),                -- #5 市区町村名カナ (半角カナ)
    town_name_kana              TEXT,                        -- #6 町域名カナ (KEN_ALLは括弧内サブ町域列挙で 400+ 文字になる行あり)
    prefecture_name             VARCHAR(20),                 -- #7 都道府県名 (漢字)
    municipality_name           VARCHAR(100),                -- #8 市区町村名 (漢字)
    town_name                   TEXT,                        -- #9 町域名 (KEN_ALL #6 と同じ理由で TEXT)

    -- KEN_ALL #10〜#13: フラグ (0/1)
    multiple_postal_codes_flag  SMALLINT,                    -- #10 一町域が二以上の郵便番号で表される場合
    koaza_banchi_flag           SMALLINT,                    -- #11 小字毎に番地が起番されている町域
    chome_flag                  SMALLINT,                    -- #12 丁目を有する町域
    multiple_towns_flag         SMALLINT,                    -- #13 一つの郵便番号で二以上の町域

    -- KEN_ALL #14〜#15: 更新メタ
    update_status               SMALLINT,                    -- #14 更新の表示 (0:変更なし / 1:変更あり / 2:廃止)
    change_reason               SMALLINT,                    -- #15 変更理由 (0:変更なし / 1:市政等 / 2:住居表示 / 3:区画整理 / 4:郵便区調整 / 5:訂正 / 6:廃止)

    -- 派生カラム (KEN_ALL外、範囲検索高速化用)
    postal_code_first3          VARCHAR(3) GENERATED ALWAYS AS (LEFT(postal_code, 3)) STORED,

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_jpaddr_multi_postal_codes CHECK (multiple_postal_codes_flag IS NULL OR multiple_postal_codes_flag IN (0, 1)),
    CONSTRAINT chk_jpaddr_koaza_banchi       CHECK (koaza_banchi_flag        IS NULL OR koaza_banchi_flag        IN (0, 1)),
    CONSTRAINT chk_jpaddr_chome              CHECK (chome_flag               IS NULL OR chome_flag               IN (0, 1)),
    CONSTRAINT chk_jpaddr_multi_towns        CHECK (multiple_towns_flag      IS NULL OR multiple_towns_flag      IN (0, 1)),
    CONSTRAINT chk_jpaddr_update_status      CHECK (update_status            IS NULL OR update_status            IN (0, 1, 2)),
    CONSTRAINT chk_jpaddr_change_reason      CHECK (change_reason            IS NULL OR change_reason            BETWEEN 0 AND 6)
);

-- 郵便番号は重複しうる (複数町域)
CREATE INDEX ix_jpaddr_postal_code        ON japan_post_address_master (postal_code);
CREATE INDEX ix_jpaddr_postal_code_first3 ON japan_post_address_master (postal_code_first3);
CREATE INDEX ix_jpaddr_prefecture         ON japan_post_address_master (prefecture_name);
CREATE INDEX ix_jpaddr_local_govt_code    ON japan_post_address_master (local_government_code);

COMMENT ON TABLE japan_post_address_master IS
    '日本郵便 KEN_ALL.CSV (utf_ken_all) を Source of Truth とする住所マスタ。15 列はすべて KEN_ALL 仕様に準拠';
COMMENT ON COLUMN japan_post_address_master.local_government_code IS
    'KEN_ALL #1: 全国地方公共団体コード (JIS X0401 都道府県 2桁 + X0402 市区町村 3桁)';
COMMENT ON COLUMN japan_post_address_master.update_status IS
    'KEN_ALL #14: 0=変更なし, 1=変更あり, 2=廃止';
COMMENT ON COLUMN japan_post_address_master.change_reason IS
    'KEN_ALL #15: 0=変更なし, 1=市政・区政等, 2=住居表示の実施, 3=区画整理, 4=郵便区調整等, 5=訂正, 6=廃止';
COMMENT ON COLUMN japan_post_address_master.postal_code_first3 IS
    '派生列。LEFT(postal_code, 3) を STORED で保持。KEN_ALL には存在しない';
