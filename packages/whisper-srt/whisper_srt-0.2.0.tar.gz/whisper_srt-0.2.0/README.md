# whisper-srt

MP3音声ファイルをOpenAI Whisper APIでSRT字幕形式に変換するCLIツール。

## 特徴

- OpenAI Whisper API (`whisper-1`) による高精度な文字起こし
- SRT形式での直接出力（変換不要）
- AI駆動開発用語の組み込み語彙でプロンプト認識精度を向上
- ローカルモデル不要で高速起動

## 料金

- $0.006/分（1時間あたり約50-60円）
- 新規OpenAIアカウントには無料クレジット付与あり

## セットアップ

### 1. 仮想環境の作成

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. インストール

```bash
pip install -e ".[dev]"  # 開発用
pip install -e .         # 本番用
```

### 3. APIキーの設定

```bash
cp .env.example .env
# .env を編集して OPENAI_API_KEY を設定
```

`.env` ファイル:
```
OPENAI_API_KEY=sk-your-api-key-here
```

APIキーは [OpenAI Platform](https://platform.openai.com/api-keys) で取得できます。

## 使い方

```bash
# 基本的な使い方（出力: input.srt）
python -m transcribe input.mp3

# 出力ファイルを指定
python -m transcribe input.mp3 -o output.srt

# 言語を指定（ISO-639-1コード）
python -m transcribe input.mp3 --language en

# 詳細ログを有効化
python -m transcribe input.mp3 -v
```

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-o, --output` | 出力SRTファイルパス | `{入力ファイル名}.srt` |
| `--language` | 言語コード（ISO-639-1） | `ja` |
| `-v, --verbose` | 詳細ログ出力 | オフ |

## 組み込み語彙

以下のカテゴリのAI/技術用語が組み込まれており、認識精度を向上させます：

- AIサービス（Claude, ChatGPT, Gemini等）
- AIコーディングツール（Cursor, Windsurf, Cline等）
- MCP関連（Model Context Protocol, MCP Connector等）
- Claude Code機能（CLAUDE.md, サブエージェント, hooks等）
- 開発手法（DDD, Onion Architecture, AI駆動開発等）

## 開発

```bash
make help        # ヘルプを表示
make ci          # lint + type-check + test を実行
make test        # テストを実行
make test-cov    # カバレッジ付きでテストを実行
make lint        # linterを実行
make format      # コードをフォーマット
make type-check  # 型チェックを実行
```

## 依存関係

- Python 3.9+
- openai
- python-dotenv
