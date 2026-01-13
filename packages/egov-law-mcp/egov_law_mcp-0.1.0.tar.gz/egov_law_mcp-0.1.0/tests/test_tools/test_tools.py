"""MCPツールのユニットテスト"""

import pytest
import respx
from httpx import Response

from egov_law_mcp.api import EGovAPIClient
from egov_law_mcp.cache import CacheManager
from egov_law_mcp.tools import (
    get_law_article,
    get_law_full_text,
    list_law_types,
    search_laws,
)


class TestListLawTypes:
    """list_law_typesのテスト"""

    def test_returns_all_law_types(self) -> None:
        """全法令種別が返される"""
        result = list_law_types()

        assert "Constitution" in result
        assert "Act" in result
        assert "CabinetOrder" in result
        assert "MinisterialOrdinance" in result
        assert "Rule" in result

        assert result["Constitution"] == "憲法"
        assert result["Act"] == "法律"


class TestSearchLaws:
    """search_lawsのテスト"""

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_laws_success(self) -> None:
        """法令検索が成功するケース"""
        mock_response = {
            "laws": [
                {
                    "law_info": {
                        "law_id": "329AC0000000089",
                        "law_type": "Act",
                        "law_num": "明治二十九年法律第八十九号",
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

        client = EGovAPIClient()
        cache = CacheManager()

        result = await search_laws(keyword="民法", client=client, cache=cache)

        assert result.total_count == 1
        assert result.laws[0].law_id == "329AC0000000089"
        assert result.laws[0].law_name == "民法"


class TestGetLawArticle:
    """get_law_articleのテスト"""

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_law_article_success(self) -> None:
        """条文取得が成功するケース"""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>民法</LawTitle>
                <MainProvision>
                    <Article Num="709">
                        <ArticleCaption>（不法行為による損害賠償）</ArticleCaption>
                        <ArticleTitle>第七百九条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <ParagraphSentence>
                                <Sentence>故意又は過失によって他人の権利又は法律上保護される利益を侵害した者は、これによって生じた損害を賠償する責任を負う。</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """

        respx.get("https://laws.e-gov.go.jp/api/2/law_data/329AC0000000089").mock(
            return_value=Response(200, content=mock_xml, headers={"content-type": "application/xml"})
        )

        client = EGovAPIClient()
        cache = CacheManager()

        result = await get_law_article(
            law_id="329AC0000000089",
            article_number="709",
            client=client,
            cache=cache,
        )

        assert result.law_id == "329AC0000000089"
        assert result.law_name == "民法"
        assert result.article_number == "709"
        assert "第七百九条" in result.content
        assert "故意又は過失" in result.content


class TestGetLawFullText:
    """get_law_full_textのテスト"""

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_law_full_text_markdown(self) -> None:
        """全文取得（Markdown形式）"""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Article Num="1">
                        <ArticleTitle>第一条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <ParagraphSentence>
                                <Sentence>テスト条文</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """

        respx.get("https://laws.e-gov.go.jp/api/2/law_data/TEST_ID").mock(
            return_value=Response(200, content=mock_xml, headers={"content-type": "application/xml"})
        )

        client = EGovAPIClient()
        cache = CacheManager()

        result = await get_law_full_text(
            law_id="TEST_ID",
            output_format="markdown",
            client=client,
            cache=cache,
        )

        assert result.law_id == "TEST_ID"
        assert result.law_name == "テスト法"
        assert "# テスト法" in result.content
        assert "第一条" in result.content

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_law_full_text_toc(self) -> None:
        """全文取得（目次形式）"""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Part Num="1">
                        <PartTitle>第一編　総則</PartTitle>
                        <Chapter Num="1">
                            <ChapterTitle>第一章　通則</ChapterTitle>
                            <Article Num="1">
                                <ArticleCaption>（目的）</ArticleCaption>
                                <ArticleTitle>第一条</ArticleTitle>
                                <Paragraph Num="1">
                                    <ParagraphNum/>
                                    <ParagraphSentence>
                                        <Sentence>本文</Sentence>
                                    </ParagraphSentence>
                                </Paragraph>
                            </Article>
                        </Chapter>
                    </Part>
                </MainProvision>
            </LawBody>
        </Law>
        """

        respx.get("https://laws.e-gov.go.jp/api/2/law_data/TEST_ID").mock(
            return_value=Response(200, content=mock_xml, headers={"content-type": "application/xml"})
        )

        client = EGovAPIClient()
        cache = CacheManager()

        result = await get_law_full_text(
            law_id="TEST_ID",
            output_format="toc",
            client=client,
            cache=cache,
        )

        assert "# 第一編　総則" in result.content
        assert "## 第一章　通則" in result.content
        assert "本文" not in result.content  # 本文は含まれない
