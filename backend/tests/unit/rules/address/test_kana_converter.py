from __future__ import annotations

from app.domain.rules.address.kana_converter import to_halfwidth_kana


def test_basic_gojuon() -> None:
    assert to_halfwidth_kana("アイウエオ") == "ｱｲｳｴｵ"
    assert to_halfwidth_kana("カキクケコ") == "ｶｷｸｹｺ"
    assert to_halfwidth_kana("ワヲン") == "ﾜｦﾝ"


def test_dakuten_handakuten_split_into_two_chars() -> None:
    """濁点・半濁点は元 PA フローと同様に 2 文字 (基底 + 結合用) に展開される。"""
    assert to_halfwidth_kana("ガ") == "ｶﾞ"
    assert to_halfwidth_kana("パ") == "ﾊﾟ"
    assert to_halfwidth_kana("ガギグゲゴ") == "ｶﾞｷﾞｸﾞｹﾞｺﾞ"
    assert to_halfwidth_kana("パピプペポ") == "ﾊﾟﾋﾟﾌﾟﾍﾟﾎﾟ"


def test_yoon_and_sokuon() -> None:
    assert to_halfwidth_kana("キャキュキョ") == "ｷｬｷｭｷｮ"
    assert to_halfwidth_kana("ガッコウ") == "ｶﾞｯｺｳ"


def test_unmapped_chars_passthrough() -> None:
    """マッピングに無い文字 (漢字・数字・空白・ヴ等) はそのまま保持する。"""
    assert to_halfwidth_kana("ABC123") == "ABC123"
    assert to_halfwidth_kana("東京都") == "東京都"
    # ヴは PA フロー側のマッピングに含まれていないためそのまま
    assert to_halfwidth_kana("ヴ") == "ヴ"


def test_real_address_kana_example() -> None:
    """実住所カナの変換例 (回帰テスト)。"""
    assert (
        to_halfwidth_kana("カナガワケンヨコハマシアオバクウツクシガオカ")
        == "ｶﾅｶﾞﾜｹﾝﾖｺﾊﾏｼｱｵﾊﾞｸｳﾂｸｼｶﾞｵｶ"
    )


def test_empty_string() -> None:
    assert to_halfwidth_kana("") == ""
