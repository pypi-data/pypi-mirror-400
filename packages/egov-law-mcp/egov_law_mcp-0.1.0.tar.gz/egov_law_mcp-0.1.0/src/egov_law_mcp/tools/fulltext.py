"""法令全文取得ツール"""

from egov_law_mcp.api import EGovAPIClient, EGovAPIError
from egov_law_mcp.cache import CacheManager
from egov_law_mcp.models import LawFullText, OutputFormat
from egov_law_mcp.parser import LawXMLParser


async def get_law_full_text(
    law_id: str,
    output_format: str = "markdown",
    asof: str | None = None,
    client: EGovAPIClient | None = None,
    cache: CacheManager | None = None,
) -> LawFullText:
    """法令全文を取得

    Args:
        law_id: 法令ID
        output_format: 出力形式（"markdown", "toc", "xml_raw"）
        asof: 施行日時点（YYYY-MM-DD形式）
        client: APIクライアント（テスト用）
        cache: キャッシュマネージャー（テスト用）

    Returns:
        法令全文

    Raises:
        EGovAPIError: API呼び出しエラー
    """
    if client is None:
        client = EGovAPIClient()
    if cache is None:
        cache = CacheManager()

    parser = LawXMLParser()

    # 出力形式を検証・変換
    try:
        fmt = OutputFormat(output_format)
    except ValueError:
        fmt = OutputFormat.MARKDOWN

    # キャッシュ確認
    xml_content = cache.get_law_data(law_id, asof=asof)

    # キャッシュミスの場合はAPI呼び出し
    if xml_content is None:
        try:
            xml_content = await client.get_law_data(law_id, asof=asof)
        except EGovAPIError:
            raise

        # キャッシュ保存
        cache.set_law_data(law_id, xml_content, asof=asof)

    # 法令タイトル取得
    law_name = parser.get_law_title(xml_content)

    # フォーマットに応じて変換
    if fmt == OutputFormat.XML_RAW:
        content = xml_content
    elif fmt == OutputFormat.TOC:
        content = parser.parse_toc(xml_content)
    else:  # markdown
        content = parser.parse_full_text(xml_content)

    return LawFullText(
        law_id=law_id,
        law_name=law_name,
        format=fmt,
        content=content,
    )
