from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_address_master_match_ok() -> None:
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kana": "トウキョウトシブヤクジングウマエ1チョウメ",
        "attribute": "新",
        "document_item": "申込書住所カナ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-master-match", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OK"
    assert body["document_recovery_value"] == "150-0001"
    assert body["correlation_id"]


def test_address_master_match_ng_unknown_address() -> None:
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kana": "ナイショノジュウショ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-master-match", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "NG"


def test_address_master_match_japan_post_fallback_ok() -> None:
    """Aflac マスタヒット 0 件 → 郵政住所マスタフォールバックで OK 回復。"""
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kana": "カナガワケンヨコハマシアオバクウツクシガオカ",
        "address_kanji": "神奈川県横浜市青葉区美しが丘1丁目",
        "attribute": "新",
        "document_item": "申込書住所カナ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-master-match", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OK"
    assert body["document_recovery_value"] == "225-0002"
    assert "郵便局住所マスタにて強制回復" in body["recovery_reason"]
    assert body["details"]["address_kana_halfwidth"] == "ｶﾅｶﾞﾜｹﾝﾖｺﾊﾏｼｱｵﾊﾞｸｳﾂｸｼｶﾞｵｶ"


def test_address_master_match_japan_post_fallback_ng() -> None:
    """Aflac でも KEN_ALL でもヒットせず → NG (該当〒番号なし)。"""
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "address_kana": "ソンザイシナイジュウショ",
        "address_kanji": "東京都存在しない区存在しない町1丁目",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-master-match", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NG"
    assert "該当〒番号なし" in body["recovery_reason"]
