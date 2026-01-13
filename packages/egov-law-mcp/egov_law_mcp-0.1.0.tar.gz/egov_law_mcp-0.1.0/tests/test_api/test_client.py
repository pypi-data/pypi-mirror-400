"""e-Gov APIクライアントのユニットテスト (TDD)"""

import pytest
import respx
from httpx import Response

from egov_law_mcp.api.client import EGovAPIClient, EGovAPIError


class TestEGovAPIClient:
    """EGovAPIClientのテスト"""

    @pytest.fixture
    def client(self) -> EGovAPIClient:
        """テスト用クライアント"""
        return EGovAPIClient()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_laws_success(self, client: EGovAPIClient) -> None:
        """法令検索が成功するケース"""
        mock_response = {
            "laws": [
                {
                    "law_info": {
                        "law_id": "329AC0000000089",
                        "law_type": "Act",
                        "law_num": "明治二十九年法律第八十九号",
                        "law_num_era": "明治",
                        "law_num_year": 29,
                        "law_num_type": "法律",
                        "law_num_num": 89,
                    },
                    "revision_info": {
                        "law_title": "民法",
                    },
                }
            ]
        }

        respx.get("https://laws.e-gov.go.jp/api/2/laws").mock(
            return_value=Response(200, json=mock_response)
        )

        result = await client.search_laws(keyword="民法")

        assert result["laws"] is not None
        assert len(result["laws"]) == 1
        assert result["laws"][0]["law_info"]["law_id"] == "329AC0000000089"

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_laws_with_law_type(self, client: EGovAPIClient) -> None:
        """法令種別指定での検索"""
        mock_response = {"laws": []}

        route = respx.get("https://laws.e-gov.go.jp/api/2/laws").mock(
            return_value=Response(200, json=mock_response)
        )

        await client.search_laws(keyword="民法", law_type="Act")

        assert route.called
        assert "law_type" in str(route.calls.last.request.url)

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_law_data_success(self, client: EGovAPIClient) -> None:
        """法令本文取得が成功するケース"""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawNum>明治二十九年法律第八十九号</LawNum>
            <LawBody>
                <LawTitle>民法</LawTitle>
            </LawBody>
        </Law>
        """

        respx.get("https://laws.e-gov.go.jp/api/2/law_data/329AC0000000089").mock(
            return_value=Response(200, content=mock_xml, headers={"content-type": "application/xml"})
        )

        result = await client.get_law_data("329AC0000000089")

        assert result is not None
        assert "民法" in result

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_law_data_not_found(self, client: EGovAPIClient) -> None:
        """存在しない法令IDの場合"""
        respx.get("https://laws.e-gov.go.jp/api/2/law_data/INVALID_ID").mock(
            return_value=Response(404, json={"error": "Not found"})
        )

        with pytest.raises(EGovAPIError) as exc_info:
            await client.get_law_data("INVALID_ID")

        assert exc_info.value.code == "E002"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_law_revisions_success(self, client: EGovAPIClient) -> None:
        """改正履歴取得が成功するケース"""
        mock_response = {
            "law_revisions": [
                {
                    "law_revision_id": "rev001",
                    "amendment_type": "一部改正",
                    "enforcement_date": "2020-04-01",
                }
            ]
        }

        respx.get("https://laws.e-gov.go.jp/api/2/law_revisions/329AC0000000089").mock(
            return_value=Response(200, json=mock_response)
        )

        result = await client.get_law_revisions("329AC0000000089")

        assert result["law_revisions"] is not None
        assert len(result["law_revisions"]) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_keyword_search_success(self, client: EGovAPIClient) -> None:
        """キーワード検索が成功するケース"""
        mock_response = {
            "items": [
                {
                    "law_id": "329AC0000000089",
                    "law_title": "民法",
                    "article_num": "709",
                    "snippet": "...故意又は過失によって...",
                }
            ]
        }

        respx.get("https://laws.e-gov.go.jp/api/2/keyword").mock(
            return_value=Response(200, json=mock_response)
        )

        result = await client.keyword_search(keyword="損害賠償")

        assert result["items"] is not None

    @respx.mock
    @pytest.mark.asyncio
    async def test_api_connection_error(self, client: EGovAPIClient) -> None:
        """API接続エラーの場合"""
        respx.get("https://laws.e-gov.go.jp/api/2/laws").mock(side_effect=Exception("Connection failed"))

        with pytest.raises(EGovAPIError) as exc_info:
            await client.search_laws(keyword="民法")

        assert exc_info.value.code == "E001"

    @respx.mock
    @pytest.mark.asyncio
    async def test_rate_limit_error(self, client: EGovAPIClient) -> None:
        """レート制限エラーの場合"""
        respx.get("https://laws.e-gov.go.jp/api/2/laws").mock(
            return_value=Response(429, json={"error": "Too many requests"})
        )

        with pytest.raises(EGovAPIError) as exc_info:
            await client.search_laws(keyword="民法")

        assert exc_info.value.code == "E006"

    def test_client_default_base_url(self, client: EGovAPIClient) -> None:
        """デフォルトのベースURLが正しい"""
        assert client.base_url == "https://laws.e-gov.go.jp/api/2"

    def test_client_custom_base_url(self) -> None:
        """カスタムベースURL設定"""
        custom_client = EGovAPIClient(base_url="https://custom.example.com/api")
        assert custom_client.base_url == "https://custom.example.com/api"
