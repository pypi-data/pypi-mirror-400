"""法令改正履歴取得ツール"""

from datetime import date

from egov_law_mcp.api import EGovAPIClient, EGovAPIError
from egov_law_mcp.cache import CacheManager
from egov_law_mcp.models import LawRevision, LawRevisionsResult


async def get_law_revisions(
    law_id: str,
    client: EGovAPIClient | None = None,
    cache: CacheManager | None = None,
) -> LawRevisionsResult:
    """法令改正履歴を取得

    Args:
        law_id: 法令ID
        client: APIクライアント（テスト用）
        cache: キャッシュマネージャー（テスト用）

    Returns:
        改正履歴結果

    Raises:
        EGovAPIError: API呼び出しエラー
    """
    if client is None:
        client = EGovAPIClient()
    if cache is None:
        cache = CacheManager()

    # キャッシュ確認
    cached = cache.get_revisions(law_id)
    if cached:
        return LawRevisionsResult(**cached)

    # API呼び出し
    try:
        response = await client.get_law_revisions(law_id)
    except EGovAPIError:
        raise

    # レスポンスをパース
    revisions: list[LawRevision] = []
    raw_revisions = response.get("revisions", [])
    law_name = ""

    for item in raw_revisions:
        # 法令名を取得（最初の履歴から）
        if not law_name and "law_title" in item:
            law_name = item["law_title"]

        # 施行日をパース (amendment_enforcement_date を使用)
        enforced_date = None
        enforcement_date_str = item.get("amendment_enforcement_date")
        if enforcement_date_str:
            try:
                enforced_date = date.fromisoformat(enforcement_date_str)
            except ValueError:
                pass

        revisions.append(
            LawRevision(
                revision_id=item.get("law_revision_id", ""),
                enforced_date=enforced_date,
                amendment_type=item.get("amendment_type"),
                amendment_law_name=item.get("amendment_law_title"),
            )
        )

    result = LawRevisionsResult(
        law_id=law_id,
        law_name=law_name,
        revisions=revisions,
    )

    # キャッシュ保存
    cache.set_revisions(law_id, result.model_dump(mode="json"))

    return result
