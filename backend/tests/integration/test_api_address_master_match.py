from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_healthz_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/healthz")
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
