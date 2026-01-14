# Lyzr SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The official Python SDK for Lyzr - Build production-ready AI agents in minutes**

Create powerful AI agents with a clean, intuitive API. Supports multiple LLM providers, knowledge bases (RAG), structured outputs, and streaming.

## ✨ Features

- 🚀 **Simple & Intuitive** - `agent.run("message")` - that's it!
- 🎯 **Type-Safe** - Full Pydantic v2 validation with autocomplete
- 🔌 **Modular** - Use what you need, extend what you want
- 🤖 **Multi-Provider** - OpenAI, Anthropic, Google, Groq, Perplexity, AWS Bedrock
- 📚 **Knowledge Bases** - Built-in RAG for documents, PDFs, websites
- 🎨 **Structured Outputs** - Type-safe responses with Pydantic models
- ⚡ **Streaming** - Real-time response streaming
- 📦 **Production-Ready** - Robust error handling, retries, validation

## 📦 Installation

```bash
pip install sumiki
```

## 🔑 Getting Your API Key

Get your free API key from **[studio.lyzr.ai](https://studio.lyzr.ai)**

Set it as an environment variable:
```bash
export LYZR_API_KEY="your-api-key-here"
```

## 🚀 Quick Start

```python
from lyzr import Studio

# Initialize (uses LYZR_API_KEY from environment)
studio = Studio()

# Or pass API key directly
studio = Studio(api_key="your-api-key-here")

# Create an agent
agent = studio.create_agent(
    name="Customer Support Agent",
    provider="openai/gpt-4o-mini"
)

# Run the agent
response = agent.run("What are your business hours?")
print(response.response)
```

## 📖 Core Features

### 1. Smart Agents

Agents are intelligent objects with built-in methods:

```python
# Create
agent = studio.create_agent(
    name="Sales Assistant",
    provider="openai/gpt-4o",
    temperature=0.7
)

# Run
response = agent.run("Hello!")

# Stream
for chunk in agent.run("Tell me about your products", stream=True):
    print(chunk.content, end="")

# Update
agent = agent.update(temperature=0.5)

# Clone
new_agent = agent.clone("Sales Assistant V2")

# Delete
agent.delete()
```

### 2. Structured Outputs with Pydantic

Get type-safe, validated responses:

```python
from pydantic import BaseModel
from typing import Literal

class SentimentAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    reasoning: str

agent = studio.create_agent(
    name="Sentiment Analyzer",
    provider="openai/gpt-4o",
    response_model=SentimentAnalysis
)

# Get typed response
result: SentimentAnalysis = agent.run("I love this product!")
print(result.sentiment)  # "positive" - fully typed!
print(result.confidence)  # 0.95
```

### 3. Knowledge Bases (RAG)

Create knowledge bases and use them with agents:

```python
# Create knowledge base
kb = studio.create_knowledge_base(
    name="product_docs",
    vector_store="qdrant"
)

# Add documents
kb.add_pdf("user_manual.pdf")
kb.add_docx("policies.docx")
kb.add_website("https://docs.mycompany.com", max_pages=50)
kb.add_text("FAQ: Business hours are 9am-5pm", source="faq.txt")

# Query directly
results = kb.query("How do I reset my password?", top_k=3)

# Use with agent at runtime
agent = studio.create_agent(
    name="Support Bot",
    provider="openai/gpt-4o"
)

response = agent.run(
    "What are your business hours?",
    knowledge_bases=[kb]  # ← Pass KB at runtime
)
```

### 4. Multiple Providers

```python
# OpenAI
agent = studio.create_agent(name="Bot", provider="openai/gpt-4o")

# Anthropic
agent = studio.create_agent(name="Bot", provider="anthropic/claude-sonnet-4-5")

# Google
agent = studio.create_agent(name="Bot", provider="google/gemini-2.5-pro")

# Auto-detect provider
agent = studio.create_agent(name="Bot", provider="gpt-4o")
```

## 🌟 Supported Models

### LLM Providers
- **OpenAI**: GPT-4o, GPT-5, o3, o4-mini
- **Anthropic**: Claude Sonnet 4.5, Claude Opus 4.5
- **Google**: Gemini 2.5 Pro, Gemini 3 Pro Preview
- **Groq**: Llama 3.3, Llama 4
- **Perplexity**: Sonar, Sonar Pro (with web search)
- **AWS Bedrock**: Amazon Nova, Claude via Bedrock

### Vector Stores (Knowledge Bases)
- Qdrant, Weaviate, PG-Vector, Milvus, Amazon Neptune

## 📚 Examples

See the `/examples` folder for complete working examples:

- `quickstart.py` - Basic agent creation and usage
- `structured_responses.py` - Pydantic models for typed outputs
- `knowledge_base_basic.py` - Creating and managing knowledge bases
- `kb_with_agent.py` - Using KBs with agents at runtime

## 🛠️ Advanced Usage

### Multiple Knowledge Bases

```python
products_kb = studio.create_knowledge_base(name="products")
policies_kb = studio.create_knowledge_base(name="policies")

# Use multiple KBs with custom config
response = agent.run(
    "What's the refund policy for Product X?",
    knowledge_bases=[
        products_kb.with_config(top_k=5, score_threshold=0.8),
        policies_kb.with_config(top_k=3, retrieval_type="mmr")
    ]
)
```

### Session Management

```python
# Auto-generated session
response = agent.run("Hello")

# Explicit session for continuity
session_id = "user_123"
response1 = agent.run("Question 1", session_id=session_id)
response2 = agent.run("Follow-up", session_id=session_id)
```

## 🐛 Error Handling

```python
from lyzr.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    InvalidResponseError
)

try:
    agent = studio.create_agent(name="Bot", provider="invalid/model")
except ValidationError as e:
    print(f"Error: {e.message}")
```

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🔗 Links

- **Get API Key**: [studio.lyzr.ai](https://studio.lyzr.ai)
- **Documentation**: [docs.lyzr.ai](https://docs.lyzr.ai)
- **GitHub**: [github.com/pradipta-lyzr/lyzr-sdk](https://github.com/pradipta-lyzr/lyzr-sdk)
- **PyPI**: [pypi.org/project/sumiki](https://pypi.org/project/sumiki)
- **Website**: [lyzr.ai](https://lyzr.ai)

## 💬 Support

- Email: support@lyzr.ai
- GitHub Issues: [github.com/pradipta-lyzr/lyzr-sdk/issues](https://github.com/pradipta-lyzr/lyzr-sdk/issues)

---

Built with ❤️ by [Lyzr](https://lyzr.ai)
