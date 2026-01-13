# e-Gov 法令検索 MCP Server 機能仕様書

> **Version**: 1.1.0  
> **Last Updated**: 2026-01-04  
> **API Version**: e-Gov 法令API Version 2 (v2.1.138)

## 1. 概要

日本の法令データを検索・取得できる「e-Gov 法令API Version 2」をラップし、LLMエージェントが最新の法令に基づいた回答、契約書チェック、コンプライアンス確認を行えるようにするためのMCPサーバー。

### 主な目的

* **ハルシネーションの防止**: LLMの学習データに頼らず、現行の正確な条文を取得する。
* **トークン節約**: 膨大な法令全文ではなく、必要な条文（第〇条）のみを抽出してコンテキストに含める。
* **可読性向上**: 複雑な法制執務XMLを、LLMが解釈しやすいMarkdownテキストに変換する。

---

## 2. 外部API仕様 (e-Gov 法令API v2)

本MCPサーバーがラップする外部APIの仕様です。

### 2.1. 基本情報

| 項目 | 値 |
| --- | --- |
| **ベースURL** | `https://laws.e-gov.go.jp/api/2` |
| **API Version** | v2.1.138 |
| **認証** | 不要（パブリックAPI） |
| **レスポンス形式** | JSON または XML（`response_format`パラメータまたは`Accept`ヘッダで指定） |
| **Swagger UI** | https://laws.e-gov.go.jp/api/2/swagger-ui |

### 2.2. 主要エンドポイント

#### 2.2.1. 法令一覧取得 (`GET /laws`)

条件に該当する法令の一覧（メタデータ）を取得します。

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `law_title` | string | No | 法令名（部分一致検索） |
| `law_num` | string | No | 法令番号 |
| `law_type` | string | No | 法令種別（憲法、法律、政令、府省令、規則） |
| `category` | integer | No | カテゴリ指標（行政組織など） |
| `asof` | string | No | 施行日時点（YYYY-MM-DD形式） |
| `updated_from` | string | No | 更新日範囲（開始） |
| `updated_to` | string | No | 更新日範囲（終了） |
| `offset` | integer | No | ページネーション用オフセット |
| `limit` | integer | No | 取得件数上限 |

**レスポンス**: `law_info`（基本情報）と `revision_info`（リビジョン情報）のリストを含む。

---

#### 2.2.2. 法令履歴一覧取得 (`GET /law_revisions/{law_id_or_num}`)

特定の法令の改正履歴一覧を取得します。

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `law_id_or_num` | string | **Yes** | 法令IDまたは法令番号（パスパラメータ） |

**レスポンス**: 過去から最新までの改正履歴情報リスト。各エントリに `amendment_type`（新規制定、一部改正、廃止等）を含む。

---

#### 2.2.3. 法令本文取得 (`GET /law_data/{law_id_or_num_or_revision_id}`)

指定した法令の本文（XML/JSON形式）を取得します。

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `law_id_or_num_or_revision_id` | string | **Yes** | 法令ID、法令番号、または法令履歴ID（パスパラメータ） |

**動作**:
- 法令IDまたは法令番号を指定した場合 → 最新版の本文を返却
- 法令履歴IDを指定した場合 → 特定のリビジョンの本文を返却

---

#### 2.2.4. 添付ファイル取得 (`GET /attachment/{law_revision_id}`)

法令本文に含まれる図表等の添付ファイルを取得します。

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `law_revision_id` | string | **Yes** | 法令履歴ID（パスパラメータ） |
| `src` | string | No | 特定のファイルパス |

**動作**: `src`未指定時はZIP形式で一括取得。

---

#### 2.2.5. キーワード検索 (`GET /keyword`)

法令本文内のキーワード検索を行います。

---

#### 2.2.6. 法令本文ファイル取得 (`GET /law_file/{file_type}/{law_id_or_num_or_revision_id}`)

法令本文を特定のファイル形式（PDF等）で取得します。

---

## 3. ツール定義 (MCP Tools)

LLMが利用可能な関数（Tool）の定義です。

### 3.1. `list_law_types` (法令種別一覧取得)

`search_laws` で使用可能な法令種別コードの一覧を返します。

* **引数**: なし

* **返り値の例**:
```json
{
  "Constitution": "憲法",
  "Act": "法律",
  "CabinetOrder": "政令",
  "MinisterialOrdinance": "府省令",
  "Rule": "規則"
}
```

---

### 3.2. `search_laws` (法令検索)

キーワードに基づいて法令を検索し、法令名と「法令ID（LawID）」のリストを返します。

* **引数**:
  * `keyword` (string, required): 検索キーワード（例: "民法", "個人情報保護法", "ドローン"）
  * `law_type` (string, optional): 法令種別。`list_law_types` で取得可能。
  * `asof` (string, optional): 施行日時点（YYYY-MM-DD形式）。未指定時は現在有効な法令。
  * `limit` (integer, optional): 取得件数上限（デフォルト: 20、最大: 100）
  * `offset` (integer, optional): ページネーション用オフセット（デフォルト: 0）

* **処理概要**:
  1. e-Gov API の `GET /laws` をコール（`law_title` パラメータにキーワードを設定）。
  2. 結果から `法令名`, `法令番号`, `法令ID` を抽出。
  3. リスト形式（JSON）で返却。

* **返り値の例**:
```json
{
  "total_count": 2,
  "laws": [
    {"law_name": "民法", "law_id": "329AC0000000089", "law_num": "明治二十九年法律第八十九号"},
    {"law_name": "民法施行法", "law_id": "331AC0000000011", "law_num": "明治三十一年法律第十一号"}
  ]
}
```

---

### 3.3. `get_law_article` (条文指定取得)

**【最重要機能】** 指定した法令の、特定の「条（Article）」の内容を取得します。

* **引数**:
  * `law_id` (string, required): `search_laws` で取得した法令ID。
  * `article_number` (string, required): 条数（例: "709", "1"）。※半角数字推奨
  * `asof` (string, optional): 施行日時点（YYYY-MM-DD形式）。未指定時は最新版。

* **処理概要**:
  1. e-Gov API の `GET /law_data/{law_id}` をコールしてXML（全条文）を取得（またはキャッシュから読み出し）。
  2. XMLパースを行い、`<Article Num="article_number">` に該当する要素を検索。
  3. 該当条文内の項（Paragraph）や号（Item）を含めてテキスト化し、返却する。

* **返り値の例 (Markdown形式)**:
```markdown
# 民法 第709条

故意又は過失によって他人の権利又は法律上保護される利益を侵害した者は、これによって生じた損害を賠償する責任を負う。
```

---

### 3.4. `get_law_full_text` (法令全文取得)

法令の全文を取得します。

* **引数**:
  * `law_id` (string, required): 法令ID。
  * `output_format` (string, optional): 
    * `"markdown"` (default): 文言を含めた全文。
    * `"toc"`: 目次（編・章・条の見出し）のみ。長大な法令の構造把握に使用。
    * `"xml_raw"`: 生のXMLデータ。
  * `asof` (string, optional): 施行日時点（YYYY-MM-DD形式）。

* **処理概要**:
  1. e-Gov API の `GET /law_data/{law_id}` からXMLを取得。
  2. XMLタグを除去・成形し、指定されたフォーマットで返却。

---

### 3.5. `get_law_revisions` (法令改正履歴取得)

法令の改正履歴一覧を取得します。

* **引数**:
  * `law_id` (string, required): 法令ID。

* **処理概要**:
  1. e-Gov API の `GET /law_revisions/{law_id}` をコール。
  2. 改正履歴リストを時系列で返却。

* **返り値の例**:
```json
{
  "law_id": "329AC0000000089",
  "law_name": "民法",
  "revisions": [
    {"revision_id": "xxx", "enforced_date": "2020-04-01", "amendment_type": "一部改正"},
    {"revision_id": "yyy", "enforced_date": "2017-06-02", "amendment_type": "一部改正"}
  ]
}
```

---

### 3.6. `keyword_search` (法令内キーワード検索)

法令本文内のキーワード検索を行い、該当箇所を返します。

* **引数**:
  * `keyword` (string, required): 検索キーワード。
  * `law_id` (string, optional): 特定の法令IDに限定する場合に指定。
  * `limit` (integer, optional): 取得件数上限（デフォルト: 20）

* **処理概要**:
  1. e-Gov API の `GET /keyword` をコール。
  2. キーワードにマッチした条文の一覧を返却。

---

## 4. リソース定義 (Resources)

MCPのResources機能を使用し、法令を直接読み込めるURIを提供します。プロンプト内で参照として渡す際に便利です。

* **URIスキーム**: `law://{law_id}`
  * 例: `law://329AC0000000089` (民法全文)

* **URIスキーム**: `law://{law_id}/article/{number}`
  * 例: `law://329AC0000000089/article/709` (民法709条)

* **URIスキーム**: `law://{law_id}?asof={date}`
  * 例: `law://329AC0000000089?asof=2020-04-01` (2020年4月1日時点の民法)

---

## 5. データ変換ロジック (XML Parsing Strategy)

e-GovのXMLは階層が深いため、単純なテキスト抽出では構造が失われます。以下のルールで変換を行います。

| XML要素 | Markdown変換ルール | 例 |
| --- | --- | --- |
| `<Part>` (編) | `# {PartTitle}` | `# 第一編 総則` |
| `<Chapter>` (章) | `## {ChapterTitle}` | `## 第一章 通則` |
| `<Section>` (節) | `### {SectionTitle}` | `### 第一節 通則` |
| `<Article>` (条) | `#### {ArticleTitle}` | `#### 第一条（基本原則）` |
| `<Paragraph>` (項) | `**{ParagraphNum}** {Text}` | `**１** 私権は、公共の福祉に...` |
| `<Item>` (号) | `* {ItemTitle} {Text}` | `* 一 〇〇の場合` |
| `<Subitem1>` (号の細分) | `  * {Text}` | `  * イ 〇〇の場合` |
| `<AppdxTable>` (別表) | `##### {AppdxTableTitle}` (内容は要約または表形式) | `##### 別表第一` |
| `<Sup>` (上付き文字) | `^{Text}` | `10^{6}` |
| `<Sub>` (下付き文字) | `_{Text}` | `CO_{2}` |

**※除外対象:**
* `<Ruby>` (フリガナ): トークン節約のため、タグ内の `<Rt>` 要素およびそのコンテンツは削除する。

---

## 6. エラーハンドリング

API呼び出しやデータ処理におけるエラーは、明確なエラーコードとメッセージとして返却します。

### 6.1. エラーコード一覧

| コード | HTTPステータス | 説明 | メッセージ例 |
| --- | --- | --- | --- |
| `E001` | - | API接続エラー | `Failed to connect to e-Gov API. Please try again later.` |
| `E002` | 404 | 法令未検出 | `Law ID '{law_id}' not found.` |
| `E003` | - | 条文未検出 | `Article '{article_number}' not found in Law ID '{law_id}'.` |
| `E004` | 400 | パラメータ不正 | `Invalid parameter: {param_name}` |
| `E005` | 500 | 内部エラー | `Internal server error occurred.` |
| `E006` | 429 | レート制限超過 | `Rate limit exceeded. Please wait and try again.` |

### 6.2. エラーレスポンス形式

```json
{
  "error": {
    "code": "E002",
    "message": "Law ID '999XX0000000001' not found.",
    "details": null
  }
}
```

---

## 7. キャッシング戦略

e-Gov APIはレスポンスに時間がかかる場合があり、また同じ法令（特に民法や刑法などの基本法）は頻繁に参照されます。

### 7.1. キャッシュ対象

| 対象 | TTL | 説明 |
| --- | --- | --- |
| 法令一覧検索結果 | 1時間 | 検索クエリをキーにキャッシュ |
| 法令本文 (XML) | 24時間 | `law_id` をキーにパース済みデータを保存 |
| 法令改正履歴 | 6時間 | `law_id` をキーにキャッシュ |

### 7.2. キャッシュ無効化

* 法令改正が検出された場合（`updated_from`/`updated_to` による差分チェック）
* 手動でのキャッシュクリア要求

### 7.3. 実装方式

* メモリキャッシュ（デフォルト）：小規模利用向け
* ファイルキャッシュ（オプション）：永続化が必要な場合
* Redis（オプション）：分散環境向け

---

## 8. 制限事項・注意点

### 8.1. API制限

* **レート制限**: e-Gov APIの公式なレート制限は未公開ですが、過度なリクエストは避けてください。本MCPサーバーでは1秒あたり最大5リクエストに制限しています。
* **レスポンスサイズ**: 法令全文取得時、民法など大規模な法令は数MBになる場合があります。

### 8.2. データの特性

* **法令XMLの構造**: 法令によりXML構造が異なる場合があります（附則の形式など）。
* **施行日の考慮**: 同じ法令IDでも施行日によって内容が異なります。`asof` パラメータで特定時点の法令を取得できます。
* **廃止法令**: 廃止された法令も検索可能ですが、`amendment_type` で判別が必要です。

### 8.3. 既知の制限

* 別表・図表の完全なレンダリングは未対応。テキスト抽出のみ。
* 一部の特殊文字（外字等）は代替文字で表示される場合があります。

---

## 9. 開発スタック

### 9.1. 推奨構成

| カテゴリ | 技術 | 備考 |
| --- | --- | --- |
| **パッケージ管理** | `pybun` | https://pypi.org/project/pybun-cli/ |
| **言語** | Python 3.10+ | 型ヒント必須 |
| **MCP SDK** | `mcp` | Model Context Protocol SDK |
| **HTTP通信** | `httpx` | 非同期HTTP通信 |
| **XMLパース** | `lxml` | 高速で柔軟なXMLパース |
| **データ検証** | `pydantic` | リクエスト/レスポンス検証 |
| **テスト** | `pytest` + `pytest-asyncio` | 非同期テスト対応 |
| **キャッシュ** | `cachetools` or `redis` | 用途に応じて選択 |

### 9.2. ディレクトリ構成

```
egov-law-mcp/
├── src/
│   └── egov_law_mcp/
│       ├── __init__.py
│       ├── server.py          # MCPサーバーエントリポイント
│       ├── tools/             # ツール実装
│       │   ├── __init__.py
│       │   ├── search.py      # search_laws, list_law_types
│       │   ├── article.py     # get_law_article
│       │   ├── fulltext.py    # get_law_full_text
│       │   ├── revisions.py   # get_law_revisions
│       │   └── keyword.py     # keyword_search
│       ├── api/               # e-Gov APIクライアント
│       │   ├── __init__.py
│       │   └── client.py
│       ├── parser/            # XMLパーサー
│       │   ├── __init__.py
│       │   └── xml_to_markdown.py
│       ├── cache/             # キャッシュ管理
│       │   ├── __init__.py
│       │   └── manager.py
│       └── models/            # Pydanticモデル
│           ├── __init__.py
│           └── schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_tools/
│   ├── test_api/
│   └── test_parser/
├── docs/
│   └── SPEC.md               # 本ドキュメント
├── pyproject.toml
└── README.md
```

---

## 10. 設定・デプロイ

### 10.1. 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `EGOV_API_BASE_URL` | No | `https://laws.e-gov.go.jp/api/2` | e-Gov APIベースURL |
| `CACHE_TYPE` | No | `memory` | `memory`, `file`, `redis` |
| `CACHE_TTL_SECONDS` | No | `86400` | キャッシュTTL（秒） |
| `CACHE_DIR` | No | `.cache` | ファイルキャッシュディレクトリ |
| `REDIS_URL` | No | - | Redisキャッシュ使用時のURL |
| `LOG_LEVEL` | No | `INFO` | ログレベル |
| `RATE_LIMIT_PER_SECOND` | No | `5` | 秒間リクエスト上限 |

### 10.2. MCPクライアント設定例

#### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "egov-law": {
      "command": "python",
      "args": ["-m", "egov_law_mcp.server"],
      "env": {
        "CACHE_TYPE": "file"
      }
    }
  }
}
```

#### pybunでの起動

```bash
pybun run python -m egov_law_mcp.server
```

---

## 11. 想定されるAIプロンプト例（ユースケース）

### 11.1. 基本的な法令調査

**ユーザー**:
「隣の家の木の枝が自分の敷地に入ってきているんだけど、勝手に切ってもいいの？民法の条文を根拠に教えて。」

**LLM (Thinking)**:
1. `search_laws(keyword="民法")` を実行 → LawID: `329AC0000000089` を特定。
2. `get_law_full_text(law_id="...", output_format="toc")` で目次を確認し、当たりをつける。
3. `get_law_article(law_id="...", article_number="233")` を実行。

**MCP Tool Output**:
```markdown
#### 第二百三十三条（竹木の枝の切除及び根の切取り）

**１** 土地の所有者は、隣地の竹木の枝が境界線を越えるときは、その竹木の所有者に、その枝を切除させることができる。

**２** 前項の場合において、竹木が数人の共有に属するときは、各共有者は、その枝を切り取ることができる。

（以下略）
```

---

### 11.2. 改正履歴の確認

**ユーザー**:
「民法の成年年齢っていつ変わったの？改正前の条文も見たい。」

**LLM (Thinking)**:
1. `search_laws(keyword="民法")` → LawID取得
2. `get_law_revisions(law_id="...")` → 2022年4月1日施行の改正を確認
3. `get_law_article(law_id="...", article_number="4", asof="2022-03-31")` → 改正前
4. `get_law_article(law_id="...", article_number="4")` → 現行

---

### 11.3. キーワード横断検索

**ユーザー**:
「『個人情報』について定めている法律を全部教えて。」

**LLM (Thinking)**:
1. `keyword_search(keyword="個人情報", limit=50)` を実行。
2. 複数の法令にまたがる結果を整理して回答。

---

## 12. ライセンス

* **本MCPサーバー**: MIT License
* **e-Gov法令データ**: 政府標準利用規約（第2.0版）に準拠

> 法令データは国民共有の財産であり、自由に利用することができます。ただし、e-Gov法令検索の利用規約を遵守してください。

---

## 13. 参考リンク

* [e-Gov 法令API v2 Swagger UI](https://laws.e-gov.go.jp/api/2/swagger-ui)
* [e-Gov 法令検索](https://laws.e-gov.go.jp/)
* [政府標準利用規約](https://www.kantei.go.jp/jp/singi/it2/info/h221228.html)
* [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
