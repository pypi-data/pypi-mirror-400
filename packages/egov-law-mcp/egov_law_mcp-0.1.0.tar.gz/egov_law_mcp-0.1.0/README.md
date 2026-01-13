# e-Gov法令API MCPサーバー

[![CI](https://github.com/takurot/egov-law-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/takurot/egov-law-mcp/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/egov-law-mcp.svg)](https://badge.fury.io/py/egov-law-mcp)
[![Python](https://img.shields.io/pypi/pyversions/egov-law-mcp.svg)](https://pypi.org/project/egov-law-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

日本の法令データを検索・取得できる「e-Gov 法令API Version 2」をラップしたMCPサーバーです。LLMが最新の法令条文に基づいて回答できるようになります。

## 特徴

- 🔍 **法令検索**: キーワードで日本の法令を検索
- 📜 **条文取得**: 特定の条文をMarkdown形式で取得（最重要機能）
- 📖 **全文/目次取得**: 法令全文または目次のみを取得
- 📅 **改正履歴**: 法令の改正履歴を取得
- 🔎 **キーワード検索**: 法令本文内の横断検索

## なぜこのMCPサーバーが必要か？

| 課題 | 解決策 |
|------|--------|
| **ハルシネーション** | LLMの学習データに頼らず、現行の正確な条文を取得 |
| **トークン消費** | 法令全文ではなく、必要な条文のみを抽出してコンテキストに含める |
| **可読性** | 複雑な法制執務XMLを、LLMが解釈しやすいMarkdownに変換 |

## インストール

```bash
pip install egov-law-mcp
```

## 使用方法

### Claude Desktopでの設定

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "egov-law": {
      "command": "python",
      "args": ["-m", "egov_law_mcp.server"]
    }
  }
}
```

### Gemini (Antigravity) での設定

`~/.gemini/antigravity/mcp_config.json`:

```json
{
  "mcpServers": {
    "egov-law": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "egov_law_mcp.server"]
    }
  }
}
```

## 利用可能なツール

### 1. `search_laws` - 法令検索

```
keyword="民法" → LawID: 129AC0000000089
```

### 2. `get_law_article` - 条文取得（最重要機能）

```markdown
# 民法 第七百九条（不法行為による損害賠償）

故意又は過失によって他人の権利又は法律上保護される利益を侵害した者は、
これによって生じた損害を賠償する責任を負う。
```

### 3. `get_law_full_text` - 全文/目次取得

- `output_format="markdown"`: 全文をMarkdown形式で取得
- `output_format="toc"`: 目次のみ（トークン節約）

### 4. `get_law_revisions` - 改正履歴取得

法令の改正履歴と施行日を取得

### 5. `keyword_search` - キーワード横断検索

複数の法令を横断してキーワード検索

### 6. `list_law_types` - 法令種別一覧

検索時に使用可能な法令種別コードを取得

## プロンプト例

**ユーザー**: 「隣の家の木の枝が自分の敷地に入ってきているんだけど、勝手に切ってもいいの？民法の条文を根拠に教えて。」

**LLMの動作**:
1. `search_laws(keyword="民法")` → 民法のLawIDを特定
2. `get_law_full_text(law_id="...", output_format="toc")` → 目次を確認
3. `get_law_article(law_id="...", article_number="233")` → 民法233条を取得

**結果**: 民法233条（竹木の枝の切除及び根の切取り）の正確な条文に基づいて回答

## 開発

### セットアップ

```bash
git clone https://github.com/takurot/egov-law-mcp.git
cd egov-law-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### テスト実行

```bash
# ユニットテストのみ
pytest tests/ -v -m "not e2e"

# E2Eテスト含む（実APIを使用）
pytest tests/ -v
```

## ライセンス

MIT License

## 関連リンク

- [e-Gov 法令API v2 Swagger UI](https://laws.e-gov.go.jp/api/2/swagger-ui)
- [e-Gov 法令検索](https://laws.e-gov.go.jp/)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
