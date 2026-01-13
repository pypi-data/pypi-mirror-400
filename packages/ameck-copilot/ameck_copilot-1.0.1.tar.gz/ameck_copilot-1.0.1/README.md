# Ameck Copilot 🤖

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI-powered coding assistant with a beautiful web interface, powered by FREE Groq API.**

## ✨ Features

- 🚀 **Lightning Fast** - Powered by Groq's ultra-fast inference
- 💰 **Completely FREE** - Uses Groq's free tier (Llama 3.3 70B)
- 🎨 **Beautiful UI** - Modern, responsive web interface
- 💬 **Chat Interface** - Natural conversation with context awareness
- 🔍 **Code Analysis** - Explain, review, optimize, fix, and document code
- ⚡ **Code Generation** - Generate code from natural language descriptions
- 🔄 **Multiple Models** - Choose from various free models

## 📦 Installation

```bash
pip install ameck-copilot
```

## 🚀 Quick Start

### 1. Get your FREE Groq API key

1. Visit [console.groq.com/keys](https://console.groq.com/keys)
2. Sign up for a free account
3. Create a new API key

### 2. Run Ameck Copilot

```bash
ameck-copilot
```

On first run, you'll be prompted to enter your API key. It will be saved securely for future use.

### 3. Open in browser

The app will automatically open at `http://127.0.0.1:8000`

## 📖 Usage

### Commands

```bash
# Start the server (default)
ameck-copilot

# Start on a specific port
ameck-copilot run --port 3000

# Configure API key
ameck-copilot setup

# Show current configuration
ameck-copilot config
```

### Environment Variables

You can also set the API key via environment variable:

```bash
export GROQ_API_KEY=gsk_your_api_key_here
ameck-copilot
```

## 🎯 Features

### Chat
Have natural conversations about code. Ask questions, get explanations, and receive coding help.

### Modes
The assistant now supports multiple modes to tailor behavior:

- **Ask** — General Q&A and conversational assistance (default)
- **Agent** — Proposes prioritized actions, outlines goals, and asks clarifying questions when needed
- **Edit** — Produces edits/patches or unified diffs for code and text
- **Plan** — Generates concise, actionable plans with numbered steps and acceptance criteria

### Code Analysis
- **Explain** - Get detailed explanations of code
- **Review** - Get code quality feedback
- **Optimize** - Get performance improvements
- **Fix** - Identify and fix bugs
- **Document** - Add documentation
- **Test** - Generate unit tests

### Code Generation
Describe what you want to build and get production-ready code with proper error handling.

## 🤖 Available Models

## 📢 Publishing
This project can be published in three distribution channels:

- **PyPI** (Python package) — installable via `pip install ameck-copilot`.
- **VS Code Marketplace** — a minimal extension is included in `vscode-extension/` that opens the local web UI or starts the server.
- **GitHub** — recommended repo: `https://github.com/QuantBender/ameck-copilot` (I can create it if you provide a token).

See `RELEASE.md` for step-by-step publishing instructions and how to add required secrets.


| Model | Description |
|-------|-------------|
| Llama 3.3 70B | Best all-around (default) |
| Llama 3.1 8B | Fast & lightweight |
| GPT-OSS 120B | OpenAI's open model |
| GPT-OSS 20B | Smaller OpenAI model |
| Llama 4 Scout 17B | Latest Llama 4 |
| Qwen 3 32B | Alibaba's model |

## 🛠️ Development

### Clone and install locally

```bash
git clone https://github.com/ameck/ameck-copilot.git
cd ameck-copilot
pip install -e .
```

### Run in development mode

```bash
ameck-copilot run --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
ameck-copilot/
├── src/
│   └── ameck_copilot/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── app/
│       │   ├── main.py         # FastAPI application
│       │   ├── config.py       # Configuration
│       │   ├── models.py       # Pydantic models
│       │   ├── routes/         # API routes
│       │   └── services/       # Business logic
│       └── static/             # Frontend files
├── pyproject.toml
└── README.md
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com) - For providing free, fast AI inference
- [Meta](https://ai.meta.com) - For Llama models
- [FastAPI](https://fastapi.tiangolo.com) - For the amazing web framework

---

Made with ❤️ by Ameck
