"""XMLパーサーのユニットテスト (TDD)"""

import pytest

from egov_law_mcp.parser.xml_to_markdown import LawXMLParser


class TestLawXMLParser:
    """LawXMLParserのテスト"""

    @pytest.fixture
    def parser(self) -> LawXMLParser:
        """テスト用パーサー"""
        return LawXMLParser()

    def test_parse_simple_article(self, parser: LawXMLParser) -> None:
        """単純な条文のパース"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Article Num="1">
                        <ArticleCaption>（目的）</ArticleCaption>
                        <ArticleTitle>第一条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <ParagraphSentence>
                                <Sentence>この法律は、テストを目的とする。</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.parse_full_text(xml)
        assert "テスト法" in result
        assert "第一条" in result
        assert "この法律は、テストを目的とする。" in result

    def test_parse_article_with_items(self, parser: LawXMLParser) -> None:
        """号を含む条文のパース"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Article Num="2">
                        <ArticleTitle>第二条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum>１</ParagraphNum>
                            <ParagraphSentence>
                                <Sentence>次に掲げるものをいう。</Sentence>
                            </ParagraphSentence>
                            <Item Num="1">
                                <ItemTitle>一</ItemTitle>
                                <ItemSentence>
                                    <Sentence>第一号の内容</Sentence>
                                </ItemSentence>
                            </Item>
                            <Item Num="2">
                                <ItemTitle>二</ItemTitle>
                                <ItemSentence>
                                    <Sentence>第二号の内容</Sentence>
                                </ItemSentence>
                            </Item>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.parse_full_text(xml)
        assert "一" in result
        assert "第一号の内容" in result
        assert "二" in result

    def test_parse_part_chapter_section(self, parser: LawXMLParser) -> None:
        """編・章・節のパース"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Part Num="1">
                        <PartTitle>第一編　総則</PartTitle>
                        <Chapter Num="1">
                            <ChapterTitle>第一章　通則</ChapterTitle>
                            <Section Num="1">
                                <SectionTitle>第一節　定義</SectionTitle>
                                <Article Num="1">
                                    <ArticleTitle>第一条</ArticleTitle>
                                    <Paragraph Num="1">
                                        <ParagraphNum/>
                                        <ParagraphSentence>
                                            <Sentence>条文内容</Sentence>
                                        </ParagraphSentence>
                                    </Paragraph>
                                </Article>
                            </Section>
                        </Chapter>
                    </Part>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.parse_full_text(xml)
        assert "# 第一編　総則" in result
        assert "## 第一章　通則" in result
        assert "### 第一節　定義" in result

    def test_extract_specific_article(self, parser: LawXMLParser) -> None:
        """特定条文の抽出"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>民法</LawTitle>
                <MainProvision>
                    <Article Num="708">
                        <ArticleTitle>第七百八条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <ParagraphSentence>
                                <Sentence>708条の内容</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
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
                    <Article Num="710">
                        <ArticleTitle>第七百十条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <ParagraphSentence>
                                <Sentence>710条の内容</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.extract_article(xml, "709")
        assert "第七百九条" in result
        assert "故意又は過失" in result
        assert "708条" not in result
        assert "710条" not in result

    def test_extract_article_not_found(self, parser: LawXMLParser) -> None:
        """存在しない条文の抽出"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Article Num="1">
                        <ArticleTitle>第一条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <ParagraphSentence>
                                <Sentence>内容</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.extract_article(xml, "999")
        assert result is None

    def test_parse_toc_format(self, parser: LawXMLParser) -> None:
        """目次形式のパース"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
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
                                        <Sentence>本文は目次には含まれない</Sentence>
                                    </ParagraphSentence>
                                </Paragraph>
                            </Article>
                        </Chapter>
                    </Part>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.parse_toc(xml)
        assert "第一編　総則" in result
        assert "第一章　通則" in result
        assert "第一条" in result
        assert "（目的）" in result
        assert "本文は目次には含まれない" not in result

    def test_remove_ruby_annotations(self, parser: LawXMLParser) -> None:
        """ルビ（フリガナ）の除去"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Article Num="1">
                        <ArticleTitle>第一条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <ParagraphSentence>
                                <Sentence><Ruby>民法<Rt>みんぽう</Rt></Ruby>を適用する。</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.parse_full_text(xml)
        assert "民法を適用する。" in result
        assert "みんぽう" not in result

    def test_get_law_title(self, parser: LawXMLParser) -> None:
        """法令タイトル取得"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>民法</LawTitle>
            </LawBody>
        </Law>
        """
        result = parser.get_law_title(xml)
        assert result == "民法"

    def test_parse_multiple_paragraphs(self, parser: LawXMLParser) -> None:
        """複数項のパース"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Article Num="1">
                        <ArticleTitle>第一条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum>１</ParagraphNum>
                            <ParagraphSentence>
                                <Sentence>第一項の内容。</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                        <Paragraph Num="2">
                            <ParagraphNum>２</ParagraphNum>
                            <ParagraphSentence>
                                <Sentence>第二項の内容。</Sentence>
                            </ParagraphSentence>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.parse_full_text(xml)
        assert "**１**" in result
        assert "第一項の内容。" in result
        assert "**２**" in result
        assert "第二項の内容。" in result

    def test_parse_subitem(self, parser: LawXMLParser) -> None:
        """号の細分（Subitem）のパース"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Law>
            <LawBody>
                <LawTitle>テスト法</LawTitle>
                <MainProvision>
                    <Article Num="1">
                        <ArticleTitle>第一条</ArticleTitle>
                        <Paragraph Num="1">
                            <ParagraphNum/>
                            <Item Num="1">
                                <ItemTitle>一</ItemTitle>
                                <ItemSentence>
                                    <Sentence>第一号</Sentence>
                                </ItemSentence>
                                <Subitem1 Num="1">
                                    <Subitem1Title>イ</Subitem1Title>
                                    <Subitem1Sentence>
                                        <Sentence>イの内容</Sentence>
                                    </Subitem1Sentence>
                                </Subitem1>
                                <Subitem1 Num="2">
                                    <Subitem1Title>ロ</Subitem1Title>
                                    <Subitem1Sentence>
                                        <Sentence>ロの内容</Sentence>
                                    </Subitem1Sentence>
                                </Subitem1>
                            </Item>
                        </Paragraph>
                    </Article>
                </MainProvision>
            </LawBody>
        </Law>
        """
        result = parser.parse_full_text(xml)
        assert "イ" in result
        assert "ロ" in result
        assert "イの内容" in result
