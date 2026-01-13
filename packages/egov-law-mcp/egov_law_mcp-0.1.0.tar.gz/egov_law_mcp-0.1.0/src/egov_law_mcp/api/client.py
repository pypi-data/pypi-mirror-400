"""e-Gov法令API v2 クライアント"""

import asyncio
import os
from typing import Any

import httpx

from egov_law_mcp.models import ErrorCode


class EGovAPIError(Exception):
    """e-Gov API エラー"""

    def __init__(self, code: str, message: str, details: Any = None) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class EGovAPIClient:
    """e-Gov法令API v2 クライアント"""

    DEFAULT_BASE_URL = "https://laws.e-gov.go.jp/api/2"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RATE_LIMIT = 5  # requests per second

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        rate_limit: int | None = None,
    ) -> None:
        self.base_url = base_url or os.getenv("EGOV_API_BASE_URL", self.DEFAULT_BASE_URL)
        self.timeout = timeout or float(os.getenv("EGOV_API_TIMEOUT", str(self.DEFAULT_TIMEOUT)))
        self.rate_limit = rate_limit or int(
            os.getenv("RATE_LIMIT_PER_SECOND", str(self.DEFAULT_RATE_LIMIT))
        )
        self._last_request_time: float = 0.0
        self._lock = asyncio.Lock()

    async def _rate_limit_wait(self) -> None:
        """レート制限のための待機"""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            min_interval = 1.0 / self.rate_limit
            elapsed = now - self._last_request_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_request_time = asyncio.get_event_loop().time()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        accept: str = "application/json",
    ) -> httpx.Response:
        """APIリクエストを実行"""
        await self._rate_limit_wait()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"Accept": accept}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, params=params, headers=headers)
        except Exception as e:
            raise EGovAPIError(
                code=ErrorCode.API_CONNECTION_ERROR.value,
                message=f"Failed to connect to e-Gov API: {e}",
                details=str(e),
            ) from e

        # ステータスコードに応じたエラーハンドリング
        if response.status_code == 404:
            raise EGovAPIError(
                code=ErrorCode.LAW_NOT_FOUND.value,
                message="Resource not found.",
                details={"url": url, "status_code": 404},
            )
        elif response.status_code == 429:
            raise EGovAPIError(
                code=ErrorCode.RATE_LIMIT_EXCEEDED.value,
                message="Rate limit exceeded. Please wait and try again.",
                details={"url": url, "status_code": 429},
            )
        elif response.status_code >= 400:
            raise EGovAPIError(
                code=ErrorCode.INTERNAL_ERROR.value,
                message=f"API error: {response.status_code}",
                details={"url": url, "status_code": response.status_code, "body": response.text},
            )

        return response

    async def search_laws(
        self,
        keyword: str,
        law_type: str | None = None,
        asof: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        法令検索 (GET /laws)

        Args:
            keyword: 検索キーワード (law_title パラメータに設定)
            law_type: 法令種別 (Constitution, Act, CabinetOrder, MinisterialOrdinance, Rule)
            asof: 施行日時点 (YYYY-MM-DD形式)
            limit: 取得件数上限
            offset: ページネーション用オフセット

        Returns:
            法令一覧レスポンス
        """
        params: dict[str, Any] = {
            "law_title": keyword,
            "limit": limit,
            "offset": offset,
        }
        if law_type:
            params["law_type"] = law_type
        if asof:
            params["asof"] = asof

        response = await self._request("GET", "/laws", params=params)
        return response.json()  # type: ignore[no-any-return]

    async def get_law_data(
        self,
        law_id_or_num: str,
        asof: str | None = None,
    ) -> str:
        """
        法令本文取得 (GET /law_data/{law_id_or_num_or_revision_id})

        Args:
            law_id_or_num: 法令ID、法令番号、または法令履歴ID
            asof: 施行日時点 (YYYY-MM-DD形式)

        Returns:
            法令XMLデータ (文字列)
        """
        params: dict[str, Any] = {}
        if asof:
            params["asof"] = asof

        response = await self._request(
            "GET",
            f"/law_data/{law_id_or_num}",
            params=params if params else None,
            accept="application/xml",
        )
        return response.text

    async def get_law_revisions(self, law_id_or_num: str) -> dict[str, Any]:
        """
        法令履歴一覧取得 (GET /law_revisions/{law_id_or_num})

        Args:
            law_id_or_num: 法令IDまたは法令番号

        Returns:
            改正履歴レスポンス
        """
        response = await self._request("GET", f"/law_revisions/{law_id_or_num}")
        return response.json()  # type: ignore[no-any-return]

    async def keyword_search(
        self,
        keyword: str,
        law_id: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        キーワード検索 (GET /keyword)

        Args:
            keyword: 検索キーワード
            law_id: 特定の法令IDに限定する場合
            limit: 取得件数上限

        Returns:
            キーワード検索レスポンス
        """
        params: dict[str, Any] = {
            "keyword": keyword,
            "limit": limit,
        }
        if law_id:
            params["law_id"] = law_id

        response = await self._request("GET", "/keyword", params=params)
        return response.json()  # type: ignore[no-any-return]
