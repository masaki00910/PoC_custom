from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AflacAddressMasterRecord(BaseModel):
    """`aflac_address_master` の参照用ビュー (突合に使う列のみ)。"""

    model_config = ConfigDict(frozen=True)

    postal_code: str | None
    prefecture_name_kana: str | None
    municipality_name_kana: str | None
    oaza_common_name_kana: str | None
    aza_cho_name_kana: str | None
