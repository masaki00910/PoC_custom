from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_consistent_returns_ok() -> None:
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kanji": "東京都渋谷区神宮前1-2-3",
        "address_kana": "トウキョウトシブヤクジングウマエ1チョウメ",
        "attribute": "新",
        "document_item": "申込書住所カナ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-kanji-kana-match", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OK"
    assert body["document_recovery_value"] == "150-0001"
    assert body["details"]["consistency_check_result"] == "OK"


def test_inconsistent_complement_ok_returns_ok() -> None:
    """整合 NG → 補完 OK で正しいカナを生成 → Aflac ヒットで OK 回復。"""
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kanji": "東京都渋谷区神宮前1-2-3",
        "address_kana": "トウキョウトチヨダクマルノウチ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-kanji-kana-match", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OK"
    assert body["document_recovery_value"] == "150-0001"
    assert body["details"]["consistency_check_result"] == "NG"
    assert body["details"]["complement_check_result"] == "OK"
    assert "補完" in body["recovery_reason"]


def test_inconsistent_complement_ng_returns_ng() -> None:
    """整合 NG → 補完 NG → 補完不可 NG。"""
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kanji": "存在しない漢字町",
        "address_kana": "ジングウマエ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-kanji-kana-match", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NG"
    assert body["details"]["complement_check_result"] == "NG"
    assert "補完できず" in body["recovery_reason"]


def test_complement_falls_through_to_japan_post_fallback() -> None:
    """整合 NG → 補完 OK → Aflac ヒット 0 件 → KEN_ALL フォールバック OK。"""
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kanji": "神奈川県横浜市青葉区美しが丘1丁目",
        "address_kana": "トウキョウトチヨダクマルノウチ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-kanji-kana-match", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OK"
    assert body["document_recovery_value"] == "225-0002"
    assert "郵便局住所マスタにて強制回復" in body["recovery_reason"]
