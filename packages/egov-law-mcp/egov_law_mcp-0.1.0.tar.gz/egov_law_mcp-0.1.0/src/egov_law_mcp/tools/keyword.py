"""キーワード検索ツール"""

from egov_law_mcp.api import EGovAPIClient, EGovAPIError
from egov_law_mcp.models import KeywordSearchHit, KeywordSearchResult


async def keyword_search(
    keyword: str,
    law_id: str | None = None,
    limit: int = 20,
    client: EGovAPIClient | None = None,
) -> KeywordSearchResult:
    """法令本文内のキーワード検索

    Args:
        keyword: 検索キーワード
        law_id: 特定の法令IDに限定する場合
        limit: 取得件数上限（デフォルト: 20）
        client: APIクライアント（テスト用）

    Returns:
        キーワード検索結果

    Raises:
        EGovAPIError: API呼び出しエラー
    """
    if client is None:
        client = EGovAPIClient()

    # API呼び出し
    try:
        response = await client.keyword_search(
            keyword=keyword,
            law_id=law_id,
            limit=limit,
        )
    except EGovAPIError:
        raise

    # レスポンスをパース
    hits: list[KeywordSearchHit] = []
    raw_items = response.get("items", [])

    for item in raw_items:
        hits.append(
            KeywordSearchHit(
                law_id=item.get("law_id", ""),
                law_name=item.get("law_title", ""),
                article_number=item.get("article_num"),
                snippet=item.get("snippet", ""),
            )
        )

    return KeywordSearchResult(
        keyword=keyword,
        total_count=len(hits),
        hits=hits,
    )
