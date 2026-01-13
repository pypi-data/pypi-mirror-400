"""キャッシュマネージャー"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from cachetools import TTLCache


class CacheManager:
    """キャッシュマネージャー

    法令データのキャッシュを管理します。
    - メモリキャッシュ（デフォルト）
    - ファイルキャッシュ（オプション）
    """

    # デフォルトTTL（秒）
    DEFAULT_LAW_DATA_TTL = 86400  # 24時間
    DEFAULT_SEARCH_TTL = 3600  # 1時間
    DEFAULT_REVISIONS_TTL = 21600  # 6時間

    def __init__(
        self,
        cache_type: str = "memory",
        cache_dir: str | None = None,
        max_size: int = 1000,
    ) -> None:
        """
        Args:
            cache_type: "memory" または "file"
            cache_dir: ファイルキャッシュのディレクトリ
            max_size: メモリキャッシュの最大エントリ数
        """
        self.cache_type = os.getenv("CACHE_TYPE", cache_type)
        self.cache_dir = Path(os.getenv("CACHE_DIR", cache_dir or ".cache"))
        self.max_size = max_size

        # メモリキャッシュ（カテゴリ別）
        self._law_data_cache: TTLCache[str, str] = TTLCache(
            maxsize=max_size, ttl=self.DEFAULT_LAW_DATA_TTL
        )
        self._search_cache: TTLCache[str, dict[str, Any]] = TTLCache(
            maxsize=max_size, ttl=self.DEFAULT_SEARCH_TTL
        )
        self._revisions_cache: TTLCache[str, dict[str, Any]] = TTLCache(
            maxsize=max_size, ttl=self.DEFAULT_REVISIONS_TTL
        )

        # ファイルキャッシュディレクトリ作成
        if self.cache_type == "file":
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, prefix: str, *args: Any, **kwargs: Any) -> str:
        """キャッシュキーを生成"""
        key_parts = [prefix, *[str(a) for a in args]]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
        key_str = ":".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    def _get_file_path(self, key: str) -> Path:
        """ファイルキャッシュのパスを取得"""
        return self.cache_dir / f"{key}.json"

    # --- 法令本文キャッシュ ---

    def get_law_data(self, law_id: str, asof: str | None = None) -> str | None:
        """法令本文をキャッシュから取得"""
        key = self._get_cache_key("law_data", law_id, asof=asof)

        # メモリキャッシュ確認
        if key in self._law_data_cache:
            return self._law_data_cache[key]

        # ファイルキャッシュ確認
        if self.cache_type == "file":
            file_path = self._get_file_path(key)
            if file_path.exists():
                data = json.loads(file_path.read_text())
                # メモリにも載せる
                self._law_data_cache[key] = data["content"]
                return data["content"]  # type: ignore[no-any-return]

        return None

    def set_law_data(self, law_id: str, content: str, asof: str | None = None) -> None:
        """法令本文をキャッシュに保存"""
        key = self._get_cache_key("law_data", law_id, asof=asof)

        # メモリキャッシュ
        self._law_data_cache[key] = content

        # ファイルキャッシュ
        if self.cache_type == "file":
            file_path = self._get_file_path(key)
            file_path.write_text(json.dumps({"law_id": law_id, "asof": asof, "content": content}))

    # --- 検索結果キャッシュ ---

    def get_search_result(
        self, keyword: str, law_type: str | None = None, **kwargs: Any
    ) -> dict[str, Any] | None:
        """検索結果をキャッシュから取得"""
        key = self._get_cache_key("search", keyword, law_type=law_type, **kwargs)

        if key in self._search_cache:
            return self._search_cache[key]

        return None

    def set_search_result(
        self, keyword: str, result: dict[str, Any], law_type: str | None = None, **kwargs: Any
    ) -> None:
        """検索結果をキャッシュに保存"""
        key = self._get_cache_key("search", keyword, law_type=law_type, **kwargs)
        self._search_cache[key] = result

    # --- 改正履歴キャッシュ ---

    def get_revisions(self, law_id: str) -> dict[str, Any] | None:
        """改正履歴をキャッシュから取得"""
        key = self._get_cache_key("revisions", law_id)

        if key in self._revisions_cache:
            return self._revisions_cache[key]

        return None

    def set_revisions(self, law_id: str, result: dict[str, Any]) -> None:
        """改正履歴をキャッシュに保存"""
        key = self._get_cache_key("revisions", law_id)
        self._revisions_cache[key] = result

    # --- 管理 ---

    def clear(self) -> None:
        """全キャッシュをクリア"""
        self._law_data_cache.clear()
        self._search_cache.clear()
        self._revisions_cache.clear()

        if self.cache_type == "file" and self.cache_dir.exists():
            for file in self.cache_dir.glob("*.json"):
                file.unlink()

    def stats(self) -> dict[str, int]:
        """キャッシュ統計を取得"""
        return {
            "law_data_count": len(self._law_data_cache),
            "search_count": len(self._search_cache),
            "revisions_count": len(self._revisions_cache),
        }
