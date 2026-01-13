#  Revenium Middleware for Anthropic

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Documentation](https://img.shields.io/badge/docs-revenium.io-blue)](https://docs.revenium.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready middleware library for metering and monitoring Anthropic API usage in Python applications. Supports both direct Anthropic API and AWS Bedrock with comprehensive streaming functionality.

## Features

- **Precise Usage Tracking**: Monitor tokens, costs, and request counts for Anthropic chat completions
- **Seamless Integration**: Drop-in middleware that works with minimal code changes
- **Decorator Support**: Automatic metadata injection with `@revenium_metadata` and selective metering with `@revenium_meter`
- **AWS Bedrock Support**: Full integration with automatic detection and metering for Anthropic models via AWS Bedrock
- **Complete Streaming Support**: Full streaming functionality for both Anthropic API and AWS Bedrock
- **Hybrid Initialization**: Auto-initialization on import + explicit control for advanced configuration
- **Thread-Safe**: Production-ready with comprehensive thread safety for concurrent applications
- **Flexible Configuration**: Customize metering behavior to suit your application needs

## What's Supported

| Feature | Direct Anthropic API | AWS Bedrock |
|---------|---------------------|-------------|
| **Chat Completion** | Full support | Full support |
| **Streaming** | Full support | Full support |
| **Token Metering** | Automatic | Automatic |
| **Metadata Tracking** | Full support | Full support |
| **Decorator Support** | Full support | Full support |
| **Thread Safety** | Production-ready | Production-ready |
| **Auto-initialization** | Zero-config | Zero-config |

**Note**: The middleware only wraps `messages.create` and `messages.stream` endpoints. Other Anthropic SDK features work normally but aren't metered.

## Quick Start

**For complete examples and setup instructions, see [`examples/README.md`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/README.md)**

### 1. Create Project Directory

```bash
# Create project directory and navigate to it
mkdir my-anthropic-project
cd my-anthropic-project
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Package

```bash
# Install packages (run after activation)
pip install revenium-middleware-anthropic python-dotenv

# Or with AWS Bedrock support:
pip install revenium-middleware-anthropic[bedrock] python-dotenv
```

### 4. Configure Environment Variables

Create a `.env` file in your project directory:

```bash
# Revenium API keys
REVENIUM_METERING_API_KEY="hak_..."
REVENIUM_METERING_BASE_URL="https://api.revenium.ai"

# Vendor API keys
ANTHROPIC_API_KEY="sk-ant-..."

# Optional: Enable debug logging
# REVENIUM_LOG_LEVEL=DEBUG
```

### 5. Run Your First Example

Download and run an example from the repository:

```bash
curl -O https://raw.githubusercontent.com/revenium/revenium-middleware-anthropic-python/main/examples/getting_started.py
python getting_started.py
```

Or use this simple code:

```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import anthropic
import revenium_middleware_anthropic  # Auto-initializes on import

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=100,
    messages=[{"role": "user", "content": "Please verify you are ready to assist me."}]
)
print(message.content[0].text)
```

**That's it!** The middleware automatically meters all Anthropic API calls. No code changes required.

**For complete examples and setup instructions, see [`examples/README.md`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/README.md)**

- [`examples/getting_started.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/getting_started.py) - Minimal example with all metadata fields documented
- [`examples/anthropic-advanced.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/anthropic-advanced.py) - Production-ready with detailed metadata tracking
- [`examples/anthropic-streaming.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/anthropic-streaming.py) - Streaming support with token tracking
- [`examples/anthropic-bedrock.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/anthropic-bedrock.py) - Complete AWS Bedrock integration
- [`examples/example_decorator.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/example_decorator.py) - Decorator-based metadata injection (v0.4.0+)

## AWS Bedrock Integration

The middleware provides complete AWS Bedrock integration with automatic detection and full streaming support.

**Provider Detection:** The middleware automatically chooses between Bedrock and direct Anthropic API based on:
- AWS credentials availability (`aws configure`, IAM roles, environment variables)
- Base URL detection (when `base_url` contains `amazonaws.com`)
- Defaults to direct Anthropic API for safety - Bedrock only used when explicitly configured

**See [`examples/anthropic-bedrock.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/anthropic-bedrock.py)** for complete working examples covering:
- Basic chat completion via AWS Bedrock
- Metadata tracking with Bedrock
- Streaming support with Bedrock
- Model mapping and configuration

### Bedrock Configuration

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REVENIUM_METERING_API_KEY` | Your Revenium API key | **Required** |
| `REVENIUM_METERING_BASE_URL` | Revenium API endpoint | **Required** |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `REVENIUM_BEDROCK_DISABLE` | Set to `1` to disable Bedrock support | Not set |

#### AWS Authentication

The middleware uses the standard AWS credential chain:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM roles (for EC2/Lambda/ECS)
4. AWS SSO

**Required AWS permissions:**
- `bedrock:InvokeModel` (for non-streaming requests)
- `bedrock:InvokeModelWithResponseStream` (for streaming requests)

### Supported Models

The middleware automatically maps Anthropic model names to Bedrock model IDs:

| Anthropic Model | Bedrock Model ID |
|----------------|------------------|
| `claude-3-opus-20240229` | `anthropic.claude-3-opus-20240229-v1:0` |
| `claude-3-sonnet-20240229` | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `claude-3-haiku-20240307` | `us.anthropic.claude-3-5-haiku-20241022-v1:0` |
| `claude-3-5-sonnet-20240620` | `anthropic.claude-3-5-sonnet-20240620-v1:0` |
| `claude-3-5-sonnet-20241022` | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `claude-3-5-haiku-20241022` | `anthropic.claude-3-5-haiku-20241022-v1:0` |

For other models, the middleware uses the format `anthropic.{model_name}`.

## Streaming Support

The middleware provides complete streaming support for both direct Anthropic API and AWS Bedrock with:
- **Universal Interface**: Same code works with both providers
- **Automatic Detection**: Provider routing happens transparently
- **Complete Token Tracking**: Accurate token counting and metering
- **Thread-Safe**: Production-ready concurrent streaming support
- **Graceful Fallback**: Automatic fallback to direct API if Bedrock fails

**See [`examples/anthropic-streaming.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/anthropic-streaming.py)** for complete streaming examples with metadata tracking and error handling.

## Metadata Fields

Add business context to track usage by organization, user, task type, or custom fields. Metadata can be passed in two ways:

1. **Directly via `usage_metadata`** (recommended for dynamic values)
2. **Via decorators** (recommended for function-level defaults - see [Decorator Support](#decorator-support))

Pass a `usage_metadata` dictionary with any of these optional fields:

| Field | Description | Use Case |
|-------|-------------|----------|
| `trace_id` | Unique identifier for session or conversation tracking | Link multiple API calls together for debugging, user session analytics, or distributed tracing across services |
| `task_type` | Type of AI task being performed | Categorize usage by workload (e.g., "chat", "code-generation", "doc-summary") for cost analysis and optimization |
| `subscriber.id` | Unique user identifier | Track individual user consumption for billing, rate limiting, or user analytics |
| `subscriber.email` | User email address | Identify users for support, compliance, or usage reports |
| `subscriber.credential.name` | Authentication credential name | Track which API key or service account made the request |
| `subscriber.credential.value` | Authentication credential value | Associate usage with specific credentials for security auditing |
| `organization_id` | Organization or company identifier | Multi-tenant cost allocation, usage quotas per organization |
| `subscription_id` | Subscription plan identifier | Track usage against subscription limits, identify plan upgrade opportunities |
| `product_id` | Your product or feature identifier | Attribute AI costs to specific features in your application (e.g., "chatbot", "email-assistant") |
| `agent` | AI agent or bot identifier | Distinguish between multiple AI agents or automation workflows in your system |
| `response_quality_score` | Custom quality rating (0.0-1.0) | Track user satisfaction or automated quality metrics for model performance analysis |

**Resources:**
- [API Reference](https://revenium.readme.io/reference/meter_ai_completion) - Complete metadata field documentation
- [`examples/anthropic-advanced.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/anthropic-advanced.py) - Working code examples

## Trace Visualization Fields (v0.3.0+)

Enhanced observability fields for distributed tracing and analytics. These fields provide deep insights into your AI operations across environments, regions, and workflows.

### How to Set Trace Fields

**Recommended approach:** Pass fields directly in `usage_metadata` for maximum control and dynamic values:

```python
message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}],
    usage_metadata={
        "environment": "production",
        "region": "us-east-1",
        "trace_type": "customer-support",
        "trace_name": "Support Chat Session"
    }
)
```

**Fallback mechanism:** Environment variables can be used as defaults when fields are not provided in `usage_metadata`. This is useful for container/deployment-level configuration, but direct passing is preferred for dynamic, request-specific values.

### Available Fields

| Field | Environment Variable (Fallback) | Description | Use Case |
|-------|----------------------------------|-------------|----------|
| `environment` | `REVENIUM_ENVIRONMENT`<br/>Auto-detects: `ENVIRONMENT`, `DEPLOYMENT_ENV` | Deployment environment (e.g., "production", "staging", "dev") | Track usage and costs across different deployment environments; identify staging vs production usage |
| `region` | `REVENIUM_REGION`<br/>Auto-detects: `AWS_REGION`, `AZURE_REGION`, `GCP_REGION` | Cloud region identifier (e.g., "us-east-1", "eastus", "us-central1") | Multi-region deployment tracking; analyze latency and costs by region |
| `credential_alias` | `REVENIUM_CREDENTIAL_ALIAS` | Human-readable API key name (e.g., "prod-anthropic-key", "staging-key") | Track which credential was used; useful for credential rotation and security auditing |
| `trace_type` | `REVENIUM_TRACE_TYPE` | Workflow category identifier (max 128 chars, alphanumeric/hyphens/underscores) | Group similar workflows (e.g., "customer-support", "data-analysis", "code-review") for analytics and cost attribution |
| `trace_name` | `REVENIUM_TRACE_NAME` | Human-readable trace label (max 256 chars) | Label trace instances (e.g., "Customer Support Chat", "Document Analysis Pipeline") for easy identification |
| `parent_transaction_id` | `REVENIUM_PARENT_TRANSACTION_ID` | Parent transaction ID for distributed tracing | Link child operations to parent transactions across microservices and workflows |
| `transaction_name` | `REVENIUM_TRANSACTION_NAME` | Human-friendly operation name | Label individual operations (e.g., "Generate Response", "Analyze Sentiment", "Summarize Document") |
| `operation_subtype` | - | Additional operation context | Auto-detected based on API usage (e.g., "tool_use", "streaming"); can be overridden |

**Note:** `operation_type` is automatically detected by the middleware based on the API endpoint (e.g., "CHAT" for messages.create) and cannot be overridden.

**Example - Direct passing (recommended):**

```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()

# Pass trace fields directly in usage_metadata
message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}],
    usage_metadata={
        "organization_id": "acme-corp",
        "product_id": "support-bot",
        "environment": "production",
        "region": "us-east-1",
        "trace_type": "customer-support",
        "trace_name": "Support Chat Session",
        "transaction_name": "Generate Response"
    }
)
```

**Example - Environment variables (fallback for deployment-level defaults):**

```bash
# Set deployment-level defaults
export REVENIUM_ENVIRONMENT="production"
export REVENIUM_REGION="us-east-1"
export REVENIUM_TRACE_TYPE="customer-support"
export REVENIUM_CREDENTIAL_ALIAS="prod-anthropic-key"

# These will be used when not provided in usage_metadata
# Direct values in usage_metadata always take precedence
```

**Best Practice:** Use environment variables for static deployment configuration (environment, region, credential_alias) and pass dynamic values (trace_name, transaction_name, organization_id) directly in `usage_metadata` or via decorators.

## Decorator Support (v0.4.0+)

The middleware supports powerful decorators for automatic metadata injection and selective metering, eliminating the need to pass `usage_metadata` to every API call.

### `@revenium_metadata` - Automatic Metadata Injection

Automatically inject metadata into all Anthropic API calls within a function's scope. This is the recommended approach for functions that make multiple API calls with shared metadata.

**Benefits:**
- **DRY Principle**: Define metadata once, apply to all API calls in the function
- **Cleaner Code**: No need to pass `usage_metadata` to each API call
- **Composable**: Decorators can be nested and combined
- **Precedence**: API-level metadata always overrides decorator metadata

**Basic Example:**

```python
from anthropic import Anthropic
from revenium_middleware import revenium_metadata
import revenium_middleware_anthropic

client = Anthropic()

@revenium_metadata(
    trace_id="session-12345",
    task_type="customer-support",
    organization_id="acme-corp",
    environment="production"
)
def handle_customer_query(question: str) -> str:
    # All API calls automatically include the decorator metadata
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

# Usage
answer = handle_customer_query("How do I reset my password?")
```

**Multiple API Calls Example:**

```python
@revenium_metadata(
    trace_id="batch-process-001",
    task_type="data-analysis",
    organization_id="analytics-team"
)
def analyze_documents(documents: list) -> list:
    results = []
    for doc in documents:
        # Each call automatically gets the same metadata
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": f"Analyze: {doc}"}]
        )
        results.append(response.content[0].text)
    return results
```

**Nested Decorators (Metadata Merging):**

```python
@revenium_metadata(
    organization_id="acme-corp",
    environment="production"
)
def outer_function():
    # This call gets: organization_id, environment
    response1 = client.messages.create(...)

    @revenium_metadata(
        trace_id="inner-trace",  # Adds new field
        task_type="analysis"     # Adds new field
        # organization_id and environment inherited from outer
    )
    def inner_function():
        # This call gets: organization_id, environment, trace_id, task_type
        response2 = client.messages.create(...)
        return response2

    return inner_function()
```

**API-Level Override:**

```python
@revenium_metadata(
    organization_id="acme-corp",
    task_type="default"
)
def mixed_metadata():
    # Uses decorator metadata
    response1 = client.messages.create(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": "Hello"}]
    )

    # API-level metadata overrides decorator
    response2 = client.messages.create(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": "Hello"}],
        usage_metadata={
            "task_type": "special-override",  # Overrides decorator
            "trace_id": "api-level-trace"     # Adds new field
            # organization_id still inherited from decorator
        }
    )
```

### `@revenium_meter` - Selective Metering

Control which functions are metered when selective metering is enabled. This is useful for metering only specific high-value operations while ignoring others.

**Note:** This decorator only has an effect when `REVENIUM_SELECTIVE_METERING=true` is set. By default, all API calls are metered automatically.

**Example:**

```python
from revenium_middleware import revenium_meter, revenium_metadata

# Only metered when REVENIUM_SELECTIVE_METERING=true
@revenium_meter()
@revenium_metadata(
    organization_id="premium-tier",
    task_type="premium-feature"
)
def premium_feature(prompt: str) -> str:
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# Not metered when REVENIUM_SELECTIVE_METERING=true
def free_feature(prompt: str) -> str:
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

**Enable selective metering:**

```bash
export REVENIUM_SELECTIVE_METERING=true
```

### Decorator Best Practices

1. **Use `@revenium_metadata` for shared metadata**: When multiple API calls share the same metadata
2. **Combine decorators**: Use both `@revenium_meter` and `@revenium_metadata` together
3. **API-level for dynamic values**: Use `usage_metadata` parameter for request-specific values
4. **Environment variables for deployment config**: Use env vars for static values like environment, region
5. **Decorator order matters**: Place `@revenium_meter` before `@revenium_metadata` (outer to inner)

**Resources:**
- [`examples/example_decorator.py`](https://github.com/revenium/revenium-middleware-anthropic-python/blob/HEAD/examples/example_decorator.py) - Complete decorator examples

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **"No module named 'boto3'"** | Install with Bedrock support: `pip install revenium-middleware-anthropic[bedrock]` |
| **Requests go to Anthropic instead of Bedrock** | Verify AWS credentials: `aws sts get-caller-identity` |
| **"AccessDenied" errors** | Ensure AWS credentials have `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` permissions |
| **Model not available** | Check if Claude models are available in your AWS region |
| **Middleware not working** | Verify `REVENIUM_METERING_API_KEY` and `REVENIUM_METERING_BASE_URL` are set |
| **Streaming errors** | Check AWS credentials; middleware automatically falls back to direct API |

**Debug Mode:** Set `REVENIUM_LOG_LEVEL=DEBUG` to see provider detection and routing decisions
**Force Direct API:** Set `REVENIUM_BEDROCK_DISABLE=1` to disable Bedrock detection
**Check Status:** Use `revenium_middleware_anthropic.is_initialized()` to verify setup

## Compatibility

- **Python 3.8+**
- **Anthropic Python SDK** (latest version recommended)
- **AWS Bedrock** (with `boto3>=1.34.0` when using `[bedrock]` extra)
- **Thread-Safe** (production-ready for concurrent applications)

## Logging

Control logging with the `REVENIUM_LOG_LEVEL` environment variable. Available levels:
- `DEBUG`: Detailed debugging information (provider detection, routing decisions)
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only
- `CRITICAL`: Critical error messages only

## Documentation

For detailed documentation, visit [docs.revenium.io](https://docs.revenium.io)

## Contributing

See [CONTRIBUTING.md](https://github.com/revenium/revenium-middleware-anthropic-python/blob/main/CONTRIBUTING.md)

## Code of Conduct

See [CODE_OF_CONDUCT.md](https://github.com/revenium/revenium-middleware-anthropic-python/blob/main/CODE_OF_CONDUCT.md)

## Security

See [SECURITY.md](https://github.com/revenium/revenium-middleware-anthropic-python/blob/main/SECURITY.md)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/revenium/revenium-middleware-anthropic-python/blob/main/LICENSE) file for details.

## Support

For issues, feature requests, or contributions:

- **Website**: [www.revenium.ai](https://www.revenium.ai)
- **GitHub Repository**: [revenium/revenium-middleware-anthropic-python](https://github.com/revenium/revenium-middleware-anthropic-python)
- **Issues**: [Report bugs or request features](https://github.com/revenium/revenium-middleware-anthropic-python/issues)
- **Documentation**: [docs.revenium.io](https://docs.revenium.io)
- **Email**: support@revenium.io

---

**Built by Revenium**
