# 🚀 VeriskGO - LLM Observability SDK

<div align="center">

**Production-ready observability for your GenAI applications**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-32.0.1-green.svg)](https://pypi.org/project/veriskgo/)
[![Tests](https://img.shields.io/badge/tests-444%20passing-brightgreen.svg)](./tests)
[![Coverage](https://img.shields.io/badge/coverage-53%25-yellow.svg)](./htmlcov)

*Track, monitor, and optimize your LLM applications with zero hassle*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Basic Tracing](#basic-tracing)
  - [LLM Calls](#llm-calls)
  - [AWS Bedrock](#aws-bedrock)
  - [LangChain Integration](#langchain-integration)
  - [ASGI Middleware](#asgi-middleware)
- [CLI Tools](#-cli-tools)
- [Configuration](#-configuration)
- [Advanced Features](#-advanced-features)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Support](#-support)

---

## 🎯 Overview

**VeriskGO** is a production-grade Python SDK designed to provide comprehensive observability for Large Language Model (LLM) applications. Built with enterprise needs in mind, it offers automatic tracing, cost tracking, and performance monitoring for all your GenAI workloads.

### Why VeriskGO?

- **🔍 Complete Visibility**: Track every LLM call, trace execution flows, and monitor system behavior
- **💰 Cost Control**: Automatic token counting and cost calculation for all major LLM providers
- **⚡ Zero Overhead**: Lightweight design with minimal performance impact
- **🔌 Easy Integration**: Drop-in decorators and middleware for instant instrumentation
- **🏢 Enterprise Ready**: Built for production with robust error handling and scalability

---

## ✨ Key Features

### 🎯 **Automatic Tracing**
- Distributed trace tracking across your entire application
- Nested span support for complex workflows
- Automatic parent-child relationship management
- Real-time trace visualization

### 💡 **LLM Provider Support**
- **AWS Bedrock**: Full support for Claude, Llama, Mistral, and more
- **OpenAI**: GPT-3.5, GPT-4, and all variants
- **Anthropic**: Claude 3 family (Opus, Sonnet, Haiku)
- **LangChain**: Native integration with callbacks

### 📊 **Cost & Usage Tracking**
- Automatic token counting (input/output)
- Real-time cost calculation
- Multi-model pricing database
- Custom pricing support

### 🔧 **Developer Experience**
- Simple decorator-based API
- Auto-instrumentation CLI tool
- ASGI middleware for web frameworks
- Comprehensive error handling

### 🚀 **Production Features**
- SQS-based event streaming
- Async/await support
- Thread-safe operations
- Automatic retry logic
- Spillover protection

---

## 🚀 Quick Start

Get up and running in 60 seconds:

```python
from veriskgo import TraceManager
from veriskgo.llm import track_llm_call

# Start a trace
trace_id = TraceManager.start_trace("my-ai-app")

# Track an LLM call
@track_llm_call(provider="bedrock", model="anthropic.claude-3-sonnet")
def ask_claude(prompt):
    # Your Bedrock call here
    response = bedrock_client.converse(...)
    return response

# Use it
result = ask_claude("What is the meaning of life?")

# End trace
TraceManager.end_trace()
```

**That's it!** 🎉 Your LLM calls are now fully observable.

---

## 📦 Installation

### Using pip

```bash
pip install veriskgo
```

### Using uv (recommended)

```bash
uv add veriskgo
```

### From source

```bash
git clone https://code.verisk.com/stash/scm/visr/llmops.observability.git
cd llmops.observability
pip install -e .
```

---

## 💻 Usage

### Basic Tracing

Track any function execution:

```python
from veriskgo.trace_manager import TraceManager

# Start a trace session
trace_id = TraceManager.start_trace("data-pipeline")

# Create spans for different operations
span_id = TraceManager.start_span(
    name="data-processing",
    input_data={"records": 1000},
    tags={"environment": "production"}
)

# Your business logic
process_data()

# End span
TraceManager.end_span(output={"processed": 950})

# End trace
TraceManager.end_trace()
```

### LLM Calls

Automatically track any LLM interaction:

```python
from veriskgo.llm import track_llm_call
import boto3

bedrock = boto3.client('bedrock-runtime')

@track_llm_call(provider="bedrock", model="anthropic.claude-3-sonnet")
def chat_with_claude(message):
    response = bedrock.converse(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        messages=[{"role": "user", "content": [{"text": message}]}]
    )
    return response

# Automatic tracking of:
# ✅ Tokens used (input/output)
# ✅ Cost calculation
# ✅ Latency measurement
# ✅ Response extraction
result = chat_with_claude("Explain quantum computing")
```

### AWS Bedrock

Deep integration with AWS Bedrock:

```python
from veriskgo.bedrock_observe import init_bedrock_observer
from veriskgo.integrations.aws import instrument_aws
import boto3

# Initialize Bedrock observer
init_bedrock_observer()

# Instrument boto3 session
session = boto3.Session()
instrument_aws(session)

# All Bedrock calls are now automatically tracked!
bedrock = session.client('bedrock-runtime')
response = bedrock.converse(
    modelId="anthropic.claude-3-opus-20240229-v1:0",
    messages=[...]
)
```

**Supported Operations:**
- ✅ `InvokeModel` - Standard inference
- ✅ `InvokeModelWithResponseStream` - Streaming responses
- ✅ `Converse` - Conversational API
- ✅ `ConverseStream` - Streaming conversations

### LangChain Integration

Seamless LangChain support:

```python
from veriskgo.llm import track_langchain
from langchain_aws import ChatBedrock

@track_langchain()
def run_chain(query):
    llm = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-east-1"
    )
    response = llm.invoke(query)
    return response

# Automatically captures:
# - Chain execution flow
# - Token usage from callbacks
# - Cost per invocation
# - Model metadata
result = run_chain("What is machine learning?")
```

### ASGI Middleware

Add observability to FastAPI, Starlette, or any ASGI app:

```python
from fastapi import FastAPI
from veriskgo.asgi_middleware import VeriskgoMiddleware

app = FastAPI()

# Add middleware
app.add_middleware(VeriskgoMiddleware)

@app.post("/api/chat")
async def chat(message: str):
    # Every request is automatically traced!
    response = await call_llm(message)
    return {"response": response}
```

**Automatic Features:**
- ✅ Request/response tracing
- ✅ User identification
- ✅ Session tracking
- ✅ Error capture
- ✅ Performance metrics

---

## 🛠️ CLI Tools

### Auto-Instrumentation

Automatically add tracing to your entire codebase:

```bash
# Instrument all functions in a file
veriskgo-instrument path/to/your_file.py

# Instrument entire directory
veriskgo-instrument src/ --recursive
```

**Before:**
```python
def process_data(data):
    return analyze(data)
```

**After:**
```python
from veriskgo.trace_manager import TraceManager

@TraceManager.track_function()
def process_data(data):
    return analyze(data)
```

### Environment Doctor

Check your observability setup:

```bash
veriskgo doctor
```

**Checks:**
- ✅ Python version compatibility
- ✅ Required dependencies
- ✅ AWS credentials
- ✅ SQS queue connectivity
- ✅ Environment variables
- ✅ Docker runtime (if applicable)

---

## ⚙️ Configuration

### Environment Variables

```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# SQS Queue (for event streaming)
export VERISKGO_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456/otel-queue

# Optional: Debug mode
export VERISKGO_DEBUG=true
```

### Programmatic Configuration

```python
from veriskgo.config import Config

# Configure SQS
Config.sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/123456/queue"

# Enable debug logging
Config.debug_mode = True
```

---

## 🔬 Advanced Features

### Custom Pricing

Add pricing for custom models:

```python
from veriskgo.core.pricing import MODEL_PRICING

# Add your custom model pricing (per token)
MODEL_PRICING["my-custom-model"] = {
    "input": 0.000001,   # $0.001 per 1K input tokens
    "output": 0.000003,  # $0.003 per 1K output tokens
}
```

### Manual Usage Tracking

Track usage without decorators:

```python
from veriskgo.core.usage import build_usage_payload

# Build usage data
usage = {
    "input_tokens": 1000,
    "output_tokens": 500
}

payload = build_usage_payload(usage, model_id="gpt-4")

# payload contains:
# - Token counts
# - Cost breakdown
# - Model metadata
```

### Nested Spans

Create complex trace hierarchies:

```python
trace_id = TraceManager.start_trace("complex-workflow")

# Parent span
parent_id = TraceManager.start_span("data-ingestion")

# Child span 1
child1_id = TraceManager.start_span("validate-data")
# ... validation logic
TraceManager.end_span()

# Child span 2
child2_id = TraceManager.start_span("transform-data")
# ... transformation logic
TraceManager.end_span()

# End parent
TraceManager.end_span()

TraceManager.end_trace()
```

### Custom Metadata

Enrich traces with custom data:

```python
TraceManager.start_span(
    name="api-call",
    input_data={"endpoint": "/api/v1/chat"},
    tags={
        "environment": "production",
        "version": "2.0",
        "user_id": "user_123",
        "session_id": "sess_456"
    }
)
```

---

## 🧪 Testing

VeriskGO has comprehensive test coverage with **444 tests** covering all major functionality.

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=veriskgo --cov-report=html

# Run specific test file
pytest tests/test_llm.py -v

# Run tests matching pattern
pytest tests/ -k "bedrock" -v
```

### Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=veriskgo --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

**Current Coverage:** 53% (633/1187 statements)

**Module Coverage:**
- ✅ bedrock_observe: 100% (isolated)
- ✅ llm: 85% (isolated)
- ✅ pricing: 96%
- ✅ usage: 97%
- ✅ CLI modules: 85-100%

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone repository
git clone https://code.verisk.com/stash/scm/visr/llmops.observability.git
cd llmops.observability

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e .

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### Running Tests

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=veriskgo --cov-report=term-missing

# Run specific test suite
pytest tests/test_bedrock_observe.py -v
```

### Code Style

We follow PEP 8 guidelines:

```bash
# Format code
black src/veriskgo/

# Check style
flake8 src/veriskgo/

# Type checking
mypy src/veriskgo/
```

### Submitting Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and add tests
3. Ensure all tests pass: `pytest tests/`
4. Commit your changes: `git commit -m "Add your feature"`
5. Push to branch: `git push origin feature/your-feature`
6. Create a Pull Request

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   FastAPI    │  │   LangChain  │  │  Bedrock SDK │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                       │
│                    │   VeriskGO     │                       │
│                    │   Middleware   │                       │
│                    └───────┬────────┘                       │
└────────────────────────────┼──────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Trace Manager   │
                    │  - Spans         │
                    │  - Metadata      │
                    │  - Timing        │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                 │
    ┌───────▼───────┐ ┌─────▼──────┐ ┌──────▼───────┐
    │ Usage Tracker │ │   Pricing  │ │  SQS Queue   │
    │ - Tokens      │ │ Calculator │ │  Publisher   │
    │ - Costs       │ └────────────┘ └──────┬───────┘
    └───────────────┘                       │
                                            │
                                    ┌───────▼────────┐
                                    │  AWS SQS       │
                                    │  Event Stream  │
                                    └───────┬────────┘
                                            │
                                    ┌───────▼────────┐
                                    │  Observability │
                                    │  Platform      │
                                    │  (Langfuse)    │
                                    └────────────────┘
```

---

## 📚 API Reference

### Core Classes

#### `TraceManager`

Manages distributed traces and spans.

```python
class TraceManager:
    @classmethod
    def start_trace(name: str, metadata: dict = None) -> str
    
    @classmethod
    def end_trace(final_output: Any = None) -> dict
    
    @classmethod
    def start_span(name: str, input_data: Any = None, tags: dict = None) -> str
    
    @classmethod
    def end_span(output: Any = None) -> None
    
    @classmethod
    def has_active_trace() -> bool
```

#### Decorators

```python
# Track any LLM call
@track_llm_call(provider: str, model: str)

# Track LangChain operations
@track_langchain()

# Track generic functions
@TraceManager.track_function(name: str = None)
```

---

## 🔒 Security

### Best Practices

- **Never commit credentials**: Use environment variables or AWS IAM roles
- **Rotate keys regularly**: Follow AWS security best practices
- **Limit permissions**: Use least-privilege IAM policies
- **Encrypt data**: Enable encryption for SQS queues
- **Monitor access**: Enable CloudTrail logging

### IAM Policy Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:GetQueueUrl"
      ],
      "Resource": "arn:aws:sqs:us-east-1:123456789012:otel-telemetry-queue"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 📝 License

Copyright © 2025 Verisk Analytics. All rights reserved.

---

## 🆘 Support

### Documentation
- Internal Wiki: [Link to internal docs]
- API Reference: [Link to API docs]

### Contact
- **Email**: llmops-support@verisk.com
- **Slack**: #llmops-observability
- **JIRA**: [Project Link]

### Troubleshooting

**Issue**: SQS connection fails
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify queue exists
aws sqs get-queue-url --queue-name otel-telemetry-queue
```

**Issue**: Bedrock calls not tracked
```bash
# Enable debug mode
export VERISKGO_DEBUG=true
python your_app.py
```

**Issue**: Import errors
```bash
# Reinstall in development mode
pip install -e .
```
  

<div align="center">

**[⬆ Back to Top](#-veriskgo---llm-observability-sdk)**

Made with ❤️ by Verisk AnalLLMOPS Team 

</div>
