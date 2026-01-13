# Revenium Perplexity Middleware - Examples

This directory contains examples demonstrating how to use the Revenium middleware with Perplexity AI.

## Prerequisites

1. **Install the package:**
   ```bash
   pip install revenium-middleware-perplexity
   ```

2. **Set up environment variables:**
   Create a `.env` file in your project root:
   ```env
   # Perplexity Configuration
   PERPLEXITY_API_KEY=pplx_your_perplexity_api_key
   
   # Revenium Configuration
   REVENIUM_METERING_API_KEY=hak_your_revenium_api_key
   REVENIUM_METERING_BASE_URL=https://api.revenium.ai
   ```

## Examples

### 1. Getting Started (`getting_started.py`)

The simplest example - just import the middleware and use the OpenAI client with Perplexity's base URL.

```bash
python examples/getting_started.py
```

**What it demonstrates:**
- Basic middleware setup
- Simple chat completion
- Automatic usage tracking

### 2. Basic Usage (`basic.py`)

Shows how to add custom metadata to track business context.

```bash
python examples/basic.py
```

**What it demonstrates:**
- Custom metadata (organization, product, subscriber)
- Business context tracking
- Detailed token usage

### 3. Streaming (`streaming.py`)

Demonstrates streaming responses with automatic metering.

```bash
python examples/streaming.py
```

**What it demonstrates:**
- Streaming chat completions
- Real-time response processing
- Automatic usage collection from stream

### 4. Trace Visualization (`trace_visualization.py`)

Shows how to use trace visualization fields for distributed tracing.

```bash
python examples/trace_visualization.py
```

**What it demonstrates:**
- Environment-based trace fields
- Distributed tracing support
- Production monitoring setup

### 5. Decorator Usage (`example_decorator.py`)

Demonstrates automatic metadata injection using decorators.

```bash
python examples/example_decorator.py
```

**What it demonstrates:**
- `@revenium_metadata` decorator for automatic metadata injection
- `@revenium_meter` decorator for selective metering
- Combining decorators for advanced use cases
- API-level metadata override
- Cleaner code without repetitive `usage_metadata` parameters

### 6. Distributed Tracing (`example_tracing.py`)

Comprehensive distributed tracing examples with all trace fields.

```bash
python examples/example_tracing.py
```

**What it demonstrates:**
- All trace visualization fields in action
- Multi-service distributed tracing
- Retry tracking with trace fields
- Multi-environment tracking (dev, staging, prod)
- Parent-child transaction relationships

## Running Examples

All examples can be run directly with Python:

```bash
# Make sure you're in the project root
cd revenium-middleware-perplexity-python

# Basic examples
python examples/getting_started.py
python examples/basic.py
python examples/streaming.py
python examples/trace_visualization.py

# Advanced examples
python examples/example_decorator.py
python examples/example_tracing.py
```

## Common Issues

**Import Error:**
- Make sure the package is installed: `pip install -e .`
- Or install from PyPI: `pip install revenium-middleware-perplexity`

**API Key Error:**
- Verify your `.env` file has the correct API keys
- Check that `python-dotenv` is installed

**No Metering Data:**
- Verify `REVENIUM_METERING_API_KEY` is set correctly
- Check Revenium dashboard for incoming data
- Enable debug logging: `export REVENIUM_LOG_LEVEL=DEBUG`

## Next Steps

- Read the main [README.md](../README.md) for complete documentation
- Check the [Revenium Documentation](https://docs.revenium.io)
- Explore the [Perplexity API Documentation](https://docs.perplexity.ai)

