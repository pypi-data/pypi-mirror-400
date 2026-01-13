"""Pydanticモデル定義"""

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LawType(str, Enum):
    """法令種別"""

    CONSTITUTION = "Constitution"
    ACT = "Act"
    CABINET_ORDER = "CabinetOrder"
    MINISTERIAL_ORDINANCE = "MinisterialOrdinance"
    RULE = "Rule"

    @classmethod
    def get_display_names(cls) -> dict[str, str]:
        """日本語表示名を取得"""
        return {
            cls.CONSTITUTION.value: "憲法",
            cls.ACT.value: "法律",
            cls.CABINET_ORDER.value: "政令",
            cls.MINISTERIAL_ORDINANCE.value: "府省令",
            cls.RULE.value: "規則",
        }


class OutputFormat(str, Enum):
    """出力フォーマット"""

    MARKDOWN = "markdown"
    TOC = "toc"
    XML_RAW = "xml_raw"


class ErrorCode(str, Enum):
    """エラーコード"""

    API_CONNECTION_ERROR = "E001"
    LAW_NOT_FOUND = "E002"
    ARTICLE_NOT_FOUND = "E003"
    INVALID_PARAMETER = "E004"
    INTERNAL_ERROR = "E005"
    RATE_LIMIT_EXCEEDED = "E006"


class LawInfo(BaseModel):
    """法令情報"""

    law_id: str = Field(..., description="法令ID")
    law_name: str = Field(..., description="法令名")
    law_num: str = Field(..., description="法令番号")
    law_type: str | None = Field(None, description="法令種別")
    promulgation_date: date | None = Field(None, description="公布日")
    enforcement_date: date | None = Field(None, description="施行日")


class LawSearchResult(BaseModel):
    """法令検索結果"""

    total_count: int = Field(..., description="総件数")
    laws: list[LawInfo] = Field(default_factory=list, description="法令リスト")


class LawArticle(BaseModel):
    """法令条文"""

    law_id: str = Field(..., description="法令ID")
    law_name: str = Field(..., description="法令名")
    article_number: str = Field(..., description="条番号")
    article_title: str | None = Field(None, description="条見出し")
    content: str = Field(..., description="条文内容(Markdown形式)")


class LawRevision(BaseModel):
    """法令改正情報"""

    revision_id: str = Field(..., description="法令履歴ID")
    enforced_date: date | None = Field(None, description="施行日")
    amendment_type: str | None = Field(None, description="改正区分")
    amendment_law_name: str | None = Field(None, description="改正法令名")


class LawRevisionsResult(BaseModel):
    """法令改正履歴結果"""

    law_id: str = Field(..., description="法令ID")
    law_name: str = Field(..., description="法令名")
    revisions: list[LawRevision] = Field(default_factory=list, description="改正履歴リスト")


class LawFullText(BaseModel):
    """法令全文"""

    law_id: str = Field(..., description="法令ID")
    law_name: str = Field(..., description="法令名")
    format: OutputFormat = Field(..., description="出力形式")
    content: str = Field(..., description="内容")


class KeywordSearchHit(BaseModel):
    """キーワード検索ヒット"""

    law_id: str = Field(..., description="法令ID")
    law_name: str = Field(..., description="法令名")
    article_number: str | None = Field(None, description="条番号")
    snippet: str = Field(..., description="マッチ箇所のスニペット")


class KeywordSearchResult(BaseModel):
    """キーワード検索結果"""

    keyword: str = Field(..., description="検索キーワード")
    total_count: int = Field(..., description="総件数")
    hits: list[KeywordSearchHit] = Field(default_factory=list, description="検索結果")


class ErrorDetail(BaseModel):
    """エラー詳細"""

    code: ErrorCode = Field(..., description="エラーコード")
    message: str = Field(..., description="エラーメッセージ")
    details: Any | None = Field(None, description="追加詳細")


class ErrorResponse(BaseModel):
    """エラーレスポンス"""

    error: ErrorDetail = Field(..., description="エラー情報")
