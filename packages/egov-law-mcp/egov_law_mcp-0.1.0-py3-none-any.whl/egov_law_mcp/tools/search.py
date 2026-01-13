"""法令検索ツール"""

from typing import Any

from egov_law_mcp.api import EGovAPIClient, EGovAPIError
from egov_law_mcp.cache import CacheManager
from egov_law_mcp.models import ErrorCode, LawInfo, LawSearchResult, LawType


def list_law_types() -> dict[str, str]:
    """法令種別一覧を取得

    Returns:
        法令種別コードと日本語名のマッピング
    """
    return LawType.get_display_names()


async def search_laws(
    keyword: str,
    law_type: str | None = None,
    asof: str | None = None,
    limit: int = 20,
    offset: int = 0,
    client: EGovAPIClient | None = None,
    cache: CacheManager | None = None,
) -> LawSearchResult:
    """法令を検索

    Args:
        keyword: 検索キーワード
        law_type: 法令種別（Constitution, Act, CabinetOrder, MinisterialOrdinance, Rule）
        asof: 施行日時点（YYYY-MM-DD形式）
        limit: 取得件数上限（デフォルト: 20、最大: 100）
        offset: ページネーション用オフセット
        client: APIクライアント（テスト用）
        cache: キャッシュマネージャー（テスト用）

    Returns:
        法令検索結果

    Raises:
        EGovAPIError: API呼び出しエラー
    """
    if client is None:
        client = EGovAPIClient()
    if cache is None:
        cache = CacheManager()

    # キャッシュ確認
    cached = cache.get_search_result(keyword, law_type=law_type, asof=asof, limit=limit, offset=offset)
    if cached:
        return LawSearchResult(**cached)

    # API呼び出し
    try:
        response = await client.search_laws(
            keyword=keyword,
            law_type=law_type,
            asof=asof,
            limit=limit,
            offset=offset,
        )
    except EGovAPIError:
        raise

    # レスポンスをパース
    laws: list[LawInfo] = []
    raw_laws = response.get("laws", [])

    for item in raw_laws:
        law_info = item.get("law_info", {})
        revision_info = item.get("revision_info", {})

        laws.append(
            LawInfo(
                law_id=law_info.get("law_id", ""),
                law_name=revision_info.get("law_title", ""),
                law_num=law_info.get("law_num", ""),
                law_type=law_info.get("law_type"),
            )
        )

    result = LawSearchResult(total_count=len(laws), laws=laws)

    # キャッシュ保存
    cache.set_search_result(
        keyword,
        result.model_dump(),
        law_type=law_type,
        asof=asof,
        limit=limit,
        offset=offset,
    )

    return result
