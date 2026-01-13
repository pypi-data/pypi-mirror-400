"""法令XMLからMarkdownへの変換パーサー"""

from lxml import etree


class LawXMLParser:
    """法令XMLパーサー

    e-Gov法令APIから取得したXMLをMarkdown形式に変換します。
    SPEC.mdの「5. データ変換ロジック」に準拠。
    """

    def __init__(self) -> None:
        self._namespaces: dict[str, str] = {}

    def _get_text(self, element: etree._Element | None) -> str:
        """要素からテキストを取得（Rubyタグのフリガナを除去）"""
        if element is None:
            return ""

        # Rtタグ（フリガナ）を除去してテキストを取得
        text_parts: list[str] = []

        def extract_text(el: etree._Element) -> None:
            if el.tag == "Rt":
                # フリガナは無視
                return
            if el.text:
                text_parts.append(el.text)
            for child in el:
                extract_text(child)
                if child.tail:
                    text_parts.append(child.tail)

        extract_text(element)
        return "".join(text_parts)

    def _parse_element(self, element: etree._Element) -> str:
        """任意のXML要素からテキストを取得"""
        return self._get_text(element)

    def get_law_title(self, xml_content: str) -> str:
        """法令タイトルを取得

        Args:
            xml_content: 法令XML文字列

        Returns:
            法令タイトル
        """
        root = etree.fromstring(xml_content.encode("utf-8"))
        law_title = root.find(".//LawTitle")
        return self._get_text(law_title) if law_title is not None else ""

    def parse_full_text(self, xml_content: str) -> str:
        """法令全文をMarkdown形式に変換

        Args:
            xml_content: 法令XML文字列

        Returns:
            Markdown形式の法令全文
        """
        root = etree.fromstring(xml_content.encode("utf-8"))
        lines: list[str] = []

        # 法令タイトル
        law_title = root.find(".//LawTitle")
        if law_title is not None:
            title = self._get_text(law_title)
            lines.append(f"# {title}")
            lines.append("")

        # 本則
        main_provision = root.find(".//MainProvision")
        if main_provision is not None:
            lines.extend(self._parse_provision(main_provision))

        # 附則
        suppl_provisions = root.findall(".//SupplProvision")
        for suppl in suppl_provisions:
            lines.append("")
            lines.append("---")
            lines.append("")
            suppl_label = suppl.get("AmendLawNum", "附則")
            lines.append(f"# 附則 {suppl_label}")
            lines.extend(self._parse_provision(suppl))

        return "\n".join(lines)

    def _parse_provision(self, provision: etree._Element) -> list[str]:
        """本則・附則をパース"""
        lines: list[str] = []

        for child in provision:
            tag = child.tag
            if tag == "Part":
                lines.extend(self._parse_part(child))
            elif tag == "Chapter":
                lines.extend(self._parse_chapter(child))
            elif tag == "Section":
                lines.extend(self._parse_section(child))
            elif tag == "Subsection":
                lines.extend(self._parse_subsection(child))
            elif tag == "Article":
                lines.extend(self._parse_article(child))
            elif tag == "Paragraph":
                lines.extend(self._parse_paragraph(child))

        return lines

    def _parse_part(self, part: etree._Element) -> list[str]:
        """編（Part）をパース"""
        lines: list[str] = []
        title = part.find("PartTitle")
        if title is not None:
            lines.append("")
            lines.append(f"# {self._get_text(title)}")
            lines.append("")

        for child in part:
            if child.tag == "Chapter":
                lines.extend(self._parse_chapter(child))
            elif child.tag == "Article":
                lines.extend(self._parse_article(child))

        return lines

    def _parse_chapter(self, chapter: etree._Element) -> list[str]:
        """章（Chapter）をパース"""
        lines: list[str] = []
        title = chapter.find("ChapterTitle")
        if title is not None:
            lines.append("")
            lines.append(f"## {self._get_text(title)}")
            lines.append("")

        for child in chapter:
            if child.tag == "Section":
                lines.extend(self._parse_section(child))
            elif child.tag == "Article":
                lines.extend(self._parse_article(child))

        return lines

    def _parse_section(self, section: etree._Element) -> list[str]:
        """節（Section）をパース"""
        lines: list[str] = []
        title = section.find("SectionTitle")
        if title is not None:
            lines.append("")
            lines.append(f"### {self._get_text(title)}")
            lines.append("")

        for child in section:
            if child.tag == "Subsection":
                lines.extend(self._parse_subsection(child))
            elif child.tag == "Article":
                lines.extend(self._parse_article(child))

        return lines

    def _parse_subsection(self, subsection: etree._Element) -> list[str]:
        """款（Subsection）をパース"""
        lines: list[str] = []
        title = subsection.find("SubsectionTitle")
        if title is not None:
            lines.append("")
            lines.append(f"#### {self._get_text(title)}")
            lines.append("")

        for child in subsection:
            if child.tag == "Article":
                lines.extend(self._parse_article(child))

        return lines

    def _parse_article(self, article: etree._Element) -> list[str]:
        """条（Article）をパース"""
        lines: list[str] = []

        # 条見出し
        caption = article.find("ArticleCaption")
        title = article.find("ArticleTitle")

        article_header = ""
        if title is not None:
            article_header = self._get_text(title)
        if caption is not None:
            cap_text = self._get_text(caption)
            if article_header:
                article_header = f"{article_header}{cap_text}"
            else:
                article_header = cap_text

        if article_header:
            lines.append("")
            lines.append(f"#### {article_header}")
            lines.append("")

        # 項
        for para in article.findall("Paragraph"):
            lines.extend(self._parse_paragraph(para))

        return lines

    def _parse_paragraph(self, paragraph: etree._Element) -> list[str]:
        """項（Paragraph）をパース"""
        lines: list[str] = []

        para_num = paragraph.find("ParagraphNum")
        para_sentence = paragraph.find("ParagraphSentence")

        para_text = ""
        if para_num is not None and self._get_text(para_num).strip():
            num_text = self._get_text(para_num).strip()
            para_text = f"**{num_text}** "

        if para_sentence is not None:
            sentences = para_sentence.findall("Sentence")
            sentence_texts = [self._get_text(s) for s in sentences]
            para_text += "".join(sentence_texts)

        if para_text.strip():
            lines.append(para_text)
            lines.append("")

        # 号
        for item in paragraph.findall("Item"):
            lines.extend(self._parse_item(item))

        return lines

    def _parse_item(self, item: etree._Element, indent: int = 0) -> list[str]:
        """号（Item）をパース"""
        lines: list[str] = []
        indent_str = "  " * indent

        item_title = item.find("ItemTitle")
        item_sentence = item.find("ItemSentence")

        item_text = f"{indent_str}* "
        if item_title is not None:
            item_text += f"{self._get_text(item_title)} "
        if item_sentence is not None:
            sentences = item_sentence.findall("Sentence")
            sentence_texts = [self._get_text(s) for s in sentences]
            item_text += "".join(sentence_texts)

        lines.append(item_text)

        # Subitem1 (号の細分)
        for subitem in item.findall("Subitem1"):
            lines.extend(self._parse_subitem(subitem, 1))

        return lines

    def _parse_subitem(self, subitem: etree._Element, level: int) -> list[str]:
        """号の細分（Subitem）をパース"""
        lines: list[str] = []
        indent_str = "  " * level

        title_tag = f"Subitem{level}Title"
        sentence_tag = f"Subitem{level}Sentence"

        title = subitem.find(title_tag)
        sentence = subitem.find(sentence_tag)

        sub_text = f"{indent_str}* "
        if title is not None:
            sub_text += f"{self._get_text(title)} "
        if sentence is not None:
            sentences = sentence.findall("Sentence")
            sentence_texts = [self._get_text(s) for s in sentences]
            sub_text += "".join(sentence_texts)

        lines.append(sub_text)

        # さらに深い階層のSubitem
        next_level = level + 1
        next_tag = f"Subitem{next_level}"
        for child_subitem in subitem.findall(next_tag):
            lines.extend(self._parse_subitem(child_subitem, next_level))

        return lines

    def extract_article(self, xml_content: str, article_number: str) -> str | None:
        """特定の条文を抽出

        Args:
            xml_content: 法令XML文字列
            article_number: 条番号（例: "709", "1"）

        Returns:
            Markdown形式の条文。見つからない場合はNone。
        """
        root = etree.fromstring(xml_content.encode("utf-8"))

        # 条番号で検索（Num属性で一致）
        article = root.find(f".//Article[@Num='{article_number}']")
        if article is None:
            # 数値形式でも試行
            article = root.find(f".//Article[@Num='{int(article_number)}']")

        if article is None:
            return None

        # 法令タイトル取得
        law_title = self.get_law_title(xml_content)

        lines: list[str] = []

        # 条見出し
        caption = article.find("ArticleCaption")
        title = article.find("ArticleTitle")

        article_header = ""
        if title is not None:
            article_header = self._get_text(title)
        if caption is not None:
            cap_text = self._get_text(caption)
            if article_header:
                article_header = f"{article_header}{cap_text}"

        if law_title:
            lines.append(f"# {law_title} {article_header}")
        else:
            lines.append(f"# {article_header}")
        lines.append("")

        # 項
        for para in article.findall("Paragraph"):
            lines.extend(self._parse_paragraph(para))

        return "\n".join(lines)

    def parse_toc(self, xml_content: str) -> str:
        """目次形式でパース（見出しのみ）

        Args:
            xml_content: 法令XML文字列

        Returns:
            目次形式のMarkdown
        """
        root = etree.fromstring(xml_content.encode("utf-8"))
        lines: list[str] = []

        # 法令タイトル
        law_title = root.find(".//LawTitle")
        if law_title is not None:
            title = self._get_text(law_title)
            lines.append(f"# {title}")
            lines.append("")

        # 本則の構造を取得
        main_provision = root.find(".//MainProvision")
        if main_provision is not None:
            lines.extend(self._parse_toc_structure(main_provision))

        return "\n".join(lines)

    def _parse_toc_structure(self, element: etree._Element) -> list[str]:
        """目次構造をパース（再帰）"""
        lines: list[str] = []

        for child in element:
            tag = child.tag

            if tag == "Part":
                title = child.find("PartTitle")
                if title is not None:
                    lines.append(f"# {self._get_text(title)}")
                lines.extend(self._parse_toc_structure(child))

            elif tag == "Chapter":
                title = child.find("ChapterTitle")
                if title is not None:
                    lines.append(f"## {self._get_text(title)}")
                lines.extend(self._parse_toc_structure(child))

            elif tag == "Section":
                title = child.find("SectionTitle")
                if title is not None:
                    lines.append(f"### {self._get_text(title)}")
                lines.extend(self._parse_toc_structure(child))

            elif tag == "Subsection":
                title = child.find("SubsectionTitle")
                if title is not None:
                    lines.append(f"#### {self._get_text(title)}")
                lines.extend(self._parse_toc_structure(child))

            elif tag == "Article":
                caption = child.find("ArticleCaption")
                title = child.find("ArticleTitle")
                article_text = ""
                if title is not None:
                    article_text = self._get_text(title)
                if caption is not None:
                    article_text += self._get_text(caption)
                if article_text:
                    lines.append(f"- {article_text}")

        return lines
