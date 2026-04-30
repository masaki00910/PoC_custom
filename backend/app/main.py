from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    app = FastAPI(
        title="Insurance Check Backend",
        version="0.1.0",
        description="保険申込書一次チェック バックエンド (PoC)",
    )

    # ヘルスチェックは `/health` を採用。`/healthz` は一部リバースプロキシ層
    # (Knative queue-proxy 等) が予約パスとして握る環境があり、ユーザコンテナまで
    # リクエストが届かない事象が発生しうるため避ける。
    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.app_env.value}

    app.include_router(v1_router, prefix="/v1")

    return app


app = create_app()
