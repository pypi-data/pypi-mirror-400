"""条文取得ツール"""

from egov_law_mcp.api import EGovAPIClient, EGovAPIError
from egov_law_mcp.cache import CacheManager
from egov_law_mcp.models import ErrorCode, LawArticle
from egov_law_mcp.parser import LawXMLParser


async def get_law_article(
    law_id: str,
    article_number: str,
    asof: str | None = None,
    client: EGovAPIClient | None = None,
    cache: CacheManager | None = None,
) -> LawArticle:
    """特定の条文を取得

    Args:
        law_id: 法令ID
        article_number: 条番号（例: "709", "1"）
        asof: 施行日時点（YYYY-MM-DD形式）
        client: APIクライアント（テスト用）
        cache: キャッシュマネージャー（テスト用）

    Returns:
        条文情報

    Raises:
        EGovAPIError: API呼び出しエラーまたは条文未検出
    """
    if client is None:
        client = EGovAPIClient()
    if cache is None:
        cache = CacheManager()

    parser = LawXMLParser()

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

    # 条文抽出
    article_content = parser.extract_article(xml_content, article_number)

    if article_content is None:
        raise EGovAPIError(
            code=ErrorCode.ARTICLE_NOT_FOUND.value,
            message=f"Article '{article_number}' not found in Law ID '{law_id}'.",
            details={"law_id": law_id, "article_number": article_number},
        )

    return LawArticle(
        law_id=law_id,
        law_name=law_name,
        article_number=article_number,
        content=article_content,
    )
