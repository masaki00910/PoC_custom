from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_postal_zero_with_existing_contract_falls_back_to_f06() -> None:
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "document_item": "02_policyholder_postal_code",
        "document_value": "000",
        "error_flag": False,
        "ca_id": "住所既契約突合チェック",
        "address_kanji": "東京都渋谷区神宮前1-2-3",
        "address_kana": "トウキョウトシブヤクジングウマエ1チョウメ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-recovery", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 2
    assert body["results"][0]["rule_name"] == "existing_contract_match"
    assert body["results"][0]["status"] == "NG"
    assert body["results"][0]["details"]["stub"] == "true"
    assert body["results"][1]["rule_name"] == "address_kanji_kana_match"
    assert body["results"][1]["status"] == "OK"
    assert body["results"][1]["document_recovery_value"] == "150-0001"


def test_error_flag_with_kanji_kana_match_invokes_f06() -> None:
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "document_item": "02_insured_postal_code",
        "document_value": "150-0001",
        "error_flag": True,
        "ca_id": "住所漢字・カナ突合チェック",
        "address_kanji": "東京都渋谷区神宮前1-2-3",
        "address_kana": "トウキョウトシブヤクジングウマエ1チョウメ",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-recovery", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 1
    assert body["results"][0]["rule_name"] == "address_kanji_kana_match"
    assert body["results"][0]["status"] == "OK"
    assert "被保険者" in body["results"][0]["recovery_reason"]


def test_char_limit_check_returns_stub_response() -> None:
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "document_item": "02_policyholder_postal_code",
        "document_value": "150-0001",
        "error_flag": False,
        "ca_id": "文字数超過チェック",
        "address_kanji": "",
        "address_kana": "",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-recovery", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 1
    assert body["results"][0]["rule_name"] == "char_limit_check"
    assert body["results"][0]["status"] == "NG"
    assert body["results"][0]["details"]["todo_task"] == "T-006"


def test_unknown_document_item_returns_empty_results() -> None:
    payload = {
        "application_id": "11111111-2222-3333-4444-555555555555",
        "document_item": "99_unknown",
        "document_value": "000",
        "ca_id": "住所既契約突合チェック",
    }
    with TestClient(app) as client:
        response = client.post("/v1/checks/address-recovery", json=payload)
    assert response.status_code == 200
    assert response.json()["results"] == []
