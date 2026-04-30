from __future__ import annotations

from typing import NewType
from uuid import UUID

from pydantic import BaseModel, ConfigDict

ApplicationId = NewType("ApplicationId", UUID)


class Application(BaseModel):
    """保険申込書 (最小フィールドセット)。

    F-05-008 住所マスタ突合の実行に必要な属性のみ保持。
    将来的に氏名・生年月日・契約商品コード等を追加する。
    """

    model_config = ConfigDict(frozen=True)

    application_id: ApplicationId
    # 補完後の住所カナ (元 Power Automate の text_4 相当)
    address_kana: str
    # 契約申込書の住所漢字 (元 Power Automate の text_3 相当)。
    # F-05-008 で Aflac マスタにヒットしなかったときの郵政住所マスタフォールバック (漢字突合) に使う。
    address_kanji: str = ""
