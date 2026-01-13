"""e-Gov法令API MCPサーバー"""

import asyncio
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from egov_law_mcp.api import EGovAPIError
from egov_law_mcp.cache import CacheManager
from egov_law_mcp.models import ErrorCode, ErrorDetail, ErrorResponse, LawType
from egov_law_mcp.tools import (
    get_law_article,
    get_law_full_text,
    get_law_revisions,
    keyword_search,
    list_law_types,
    search_laws,
)

# ロギング設定
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# グローバルキャッシュ
_cache = CacheManager()

# MCPサーバーインスタンス
app = Server("egov-law-mcp")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """利用可能なツール一覧を返す"""
    return [
        Tool(
            name="list_law_types",
            description="法令種別一覧を取得します。search_lawsで使用可能な法令種別コードを返します。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="search_laws",
            description="キーワードに基づいて法令を検索し、法令名と法令IDのリストを返します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "検索キーワード（例: 民法, 個人情報保護法）",
                    },
                    "law_type": {
                        "type": "string",
                        "description": "法令種別（Constitution, Act, CabinetOrder, MinisterialOrdinance, Rule）",
                        "enum": [t.value for t in LawType],
                    },
                    "asof": {
                        "type": "string",
                        "description": "施行日時点（YYYY-MM-DD形式）。未指定時は現在有効な法令。",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "取得件数上限（デフォルト: 20、最大: 100）",
                        "default": 20,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "ページネーション用オフセット",
                        "default": 0,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="get_law_article",
            description="指定した法令の特定の条文をMarkdown形式で取得します。これが最も重要な機能です。",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_id": {
                        "type": "string",
                        "description": "法令ID（search_lawsで取得）",
                    },
                    "article_number": {
                        "type": "string",
                        "description": "条番号（例: 709, 1）※半角数字推奨",
                    },
                    "asof": {
                        "type": "string",
                        "description": "施行日時点（YYYY-MM-DD形式）。未指定時は最新版。",
                    },
                },
                "required": ["law_id", "article_number"],
            },
        ),
        Tool(
            name="get_law_full_text",
            description="法令の全文を取得します。大規模な法令の場合はtoc形式で目次のみ取得することを推奨します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_id": {
                        "type": "string",
                        "description": "法令ID",
                    },
                    "output_format": {
                        "type": "string",
                        "description": "出力形式",
                        "enum": ["markdown", "toc", "xml_raw"],
                        "default": "markdown",
                    },
                    "asof": {
                        "type": "string",
                        "description": "施行日時点（YYYY-MM-DD形式）",
                    },
                },
                "required": ["law_id"],
            },
        ),
        Tool(
            name="get_law_revisions",
            description="法令の改正履歴一覧を取得します。過去の施行日を確認するのに使用します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_id": {
                        "type": "string",
                        "description": "法令ID",
                    },
                },
                "required": ["law_id"],
            },
        ),
        Tool(
            name="keyword_search",
            description="法令本文内のキーワード検索を行い、該当箇所を返します。複数の法令を横断検索できます。",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "検索キーワード",
                    },
                    "law_id": {
                        "type": "string",
                        "description": "特定の法令IDに限定する場合",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "取得件数上限（デフォルト: 20）",
                        "default": 20,
                    },
                },
                "required": ["keyword"],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """ツールを実行"""
    try:
        result: Any = None

        if name == "list_law_types":
            result = list_law_types()

        elif name == "search_laws":
            result = await search_laws(
                keyword=arguments["keyword"],
                law_type=arguments.get("law_type"),
                asof=arguments.get("asof"),
                limit=arguments.get("limit", 20),
                offset=arguments.get("offset", 0),
                cache=_cache,
            )
            result = result.model_dump()

        elif name == "get_law_article":
            result = await get_law_article(
                law_id=arguments["law_id"],
                article_number=arguments["article_number"],
                asof=arguments.get("asof"),
                cache=_cache,
            )
            # 条文はMarkdown形式でそのまま返す
            return [TextContent(type="text", text=result.content)]

        elif name == "get_law_full_text":
            result = await get_law_full_text(
                law_id=arguments["law_id"],
                output_format=arguments.get("output_format", "markdown"),
                asof=arguments.get("asof"),
                cache=_cache,
            )
            # 全文は内容のみ返す
            return [TextContent(type="text", text=result.content)]

        elif name == "get_law_revisions":
            result = await get_law_revisions(
                law_id=arguments["law_id"],
                cache=_cache,
            )
            result = result.model_dump(mode="json")

        elif name == "keyword_search":
            result = await keyword_search(
                keyword=arguments["keyword"],
                law_id=arguments.get("law_id"),
                limit=arguments.get("limit", 20),
            )
            result = result.model_dump()

        else:
            raise ValueError(f"Unknown tool: {name}")

        # 結果をJSON文字列として返す
        import json
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    except EGovAPIError as e:
        # APIエラーを整形して返す
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode(e.code),
                message=e.message,
                details=e.details,
            )
        )
        import json
        return [TextContent(type="text", text=json.dumps(error_response.model_dump(), ensure_ascii=False))]

    except Exception as e:
        # 予期しないエラー
        logger.exception(f"Unexpected error in tool {name}")
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.INTERNAL_ERROR,
                message=f"Internal server error: {e}",
            )
        )
        import json
        return [TextContent(type="text", text=json.dumps(error_response.model_dump(), ensure_ascii=False))]


async def run_server() -> None:
    """サーバーを起動"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main() -> None:
    """エントリーポイント"""
    logger.info("Starting e-Gov Law MCP Server...")
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
