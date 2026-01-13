# whisper-srt

CLI tool to transcribe MP3 audio files to SRT subtitle format using OpenAI Whisper API.

English | [日本語](README.ja.md)

## Features

- Simple CLI for MP3 to SRT conversion
- High-accuracy transcription via OpenAI Whisper API (`whisper-1`)
- Built-in AI/tech terminology for better recognition
- Custom vocabulary support

## Quick Start

**No installation required** - just run with [uv](https://docs.astral.sh/uv/):

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Transcribe (creates audio.srt)
uvx whisper-srt audio.mp3
```

Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys).

## Installation (Optional)

If you prefer a permanent install:

```bash
uv tool install whisper-srt
whisper-srt audio.mp3
```

## Usage

```bash
whisper-srt input.mp3                    # Basic usage (default: English)
whisper-srt input.mp3 -o output.srt      # Specify output
whisper-srt input.mp3 --language ja      # Specify language (Japanese)
whisper-srt --help                       # See all options
```

## Supported Languages

Default language is **English (`en`)**.

Common language codes (ISO-639-1):
| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English | `ja` | Japanese |
| `zh` | Chinese | `ko` | Korean |
| `es` | Spanish | `fr` | French |
| `de` | German | `pt` | Portuguese |

See [OpenAI Whisper documentation](https://platform.openai.com/docs/guides/speech-to-text) for all supported languages.

## Custom Vocabulary

Create `~/.config/whisper-srt/vocabulary.txt` with domain-specific terms:

```
YouTube
Podcast
MyCompanyName
```

## Pricing

$0.006/minute (~$0.36/hour)

## Development

```bash
git clone https://github.com/tomada1114/whisper-srt.git
cd whisper-srt
uv sync --dev
make ci   # lint + type-check + test
```

## License

MIT
