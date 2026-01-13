"""E2Eテスト - 実際のe-Gov APIを使用"""

import pytest

from egov_law_mcp.api import EGovAPIClient
from egov_law_mcp.cache import CacheManager
from egov_law_mcp.tools import (
    get_law_article,
    get_law_full_text,
    get_law_revisions,
    keyword_search,
    search_laws,
)


# E2Eテストは明示的に実行する必要がある
pytestmark = pytest.mark.e2e


class TestE2ESearchLaws:
    """search_laws E2Eテスト"""

    @pytest.mark.asyncio
    async def test_search_minpou(self) -> None:
        """民法を検索"""
        client = EGovAPIClient()
        cache = CacheManager()

        result = await search_laws(keyword="民法", limit=5, client=client, cache=cache)

        assert result.total_count > 0
        # 民法が結果に含まれるはず
        law_names = [law.law_name for law in result.laws]
        assert any("民法" in name for name in law_names), f"民法 not found in {law_names}"

    @pytest.mark.asyncio
    async def test_search_with_law_type(self) -> None:
        """法律種別を指定して検索"""
        client = EGovAPIClient()
        cache = CacheManager()

        result = await search_laws(
            keyword="民法", law_type="Act", limit=5, client=client, cache=cache
        )

        # 法律のみが返されるはず
        assert result.total_count > 0


class TestE2EGetLawArticle:
    """get_law_article E2Eテスト"""

    @pytest.mark.asyncio
    async def test_get_minpou_709(self) -> None:
        """民法709条（不法行為）を取得"""
        client = EGovAPIClient()
        cache = CacheManager()

        # まず民法のIDを取得
        search_result = await search_laws(keyword="民法", limit=1, client=client, cache=cache)
        assert search_result.total_count > 0

        minpou = None
        for law in search_result.laws:
            if law.law_name == "民法":
                minpou = law
                break

        assert minpou is not None, "民法 not found"

        # 709条を取得
        article = await get_law_article(
            law_id=minpou.law_id,
            article_number="709",
            client=client,
            cache=cache,
        )

        assert article.law_id == minpou.law_id
        assert article.article_number == "709"
        assert "故意又は過失" in article.content or "損害" in article.content

    @pytest.mark.asyncio
    async def test_get_minpou_233(self) -> None:
        """民法233条（竹木の枝の切除）を取得"""
        client = EGovAPIClient()
        cache = CacheManager()

        search_result = await search_laws(keyword="民法", limit=1, client=client, cache=cache)
        minpou = next((law for law in search_result.laws if law.law_name == "民法"), None)
        assert minpou is not None

        article = await get_law_article(
            law_id=minpou.law_id,
            article_number="233",
            client=client,
            cache=cache,
        )

        assert "竹木" in article.content or "枝" in article.content


class TestE2EGetLawFullText:
    """get_law_full_text E2Eテスト"""

    @pytest.mark.asyncio
    async def test_get_law_toc(self) -> None:
        """法令の目次を取得"""
        client = EGovAPIClient()
        cache = CacheManager()

        search_result = await search_laws(keyword="民法", limit=1, client=client, cache=cache)
        minpou = next((law for law in search_result.laws if law.law_name == "民法"), None)
        assert minpou is not None

        result = await get_law_full_text(
            law_id=minpou.law_id,
            output_format="toc",
            client=client,
            cache=cache,
        )

        assert result.law_name == "民法"
        # 民法には「第一編」などの編が含まれるはず
        assert "第一編" in result.content or "総則" in result.content


class TestE2EGetLawRevisions:
    """get_law_revisions E2Eテスト"""

    @pytest.mark.asyncio
    async def test_get_revisions(self) -> None:
        """改正履歴を取得"""
        client = EGovAPIClient()
        cache = CacheManager()

        search_result = await search_laws(keyword="民法", limit=1, client=client, cache=cache)
        minpou = next((law for law in search_result.laws if law.law_name == "民法"), None)
        assert minpou is not None

        result = await get_law_revisions(law_id=minpou.law_id, client=client, cache=cache)

        assert result.law_id == minpou.law_id
        # 民法は複数回改正されているはず
        assert len(result.revisions) > 0


class TestE2EKeywordSearch:
    """keyword_search E2Eテスト"""

    @pytest.mark.asyncio
    async def test_keyword_search(self) -> None:
        """キーワード検索"""
        client = EGovAPIClient()

        result = await keyword_search(keyword="損害賠償", limit=10, client=client)

        # 何かしらの結果が返るはず
        # （APIの仕様によっては0件の可能性もあるため、エラーにならないことを確認）
        assert result.keyword == "損害賠償"
        assert isinstance(result.total_count, int)
