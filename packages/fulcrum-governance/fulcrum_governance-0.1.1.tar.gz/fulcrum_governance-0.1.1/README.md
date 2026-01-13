mcp-name: io.github.Dewars30/fulcrum
# Fulcrum Python SDK

> Intelligent AI Governance for Enterprise Agents

[![PyPI version](https://badge.fury.io/py/fulcrum-governance.svg)](https://badge.fury.io/py/fulcrum-governance)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)](https://fulcrum.dev/license)

## Installation

```bash
pip install fulcrum-governance
```

## Quick Start

```python
from fulcrum import FulcrumClient

# Initialize client
client = FulcrumClient(
    host="your-fulcrum-server:50051",
    api_key="your-api-key"
)

# Wrap agent executions in governance envelopes
with client.envelope(workflow_id="customer-support-bot") as env:
    # Check if action is allowed before executing
    if env.guard("send_email", input_text=user_message):
        # Action approved - proceed
        result = send_email(user_message)
        env.log("email_sent", {"recipient": email, "status": "success"})
    else:
        # Action blocked by policy
        env.log("action_blocked", {"reason": "policy_violation"})
```

## Features

- **Policy Enforcement**: Real-time governance checks before agent actions
- **Cost Tracking**: Monitor and control LLM spending per workflow
- **Audit Trail**: Complete execution history for compliance
- **Fail-Safe Modes**: Configurable FAIL_OPEN or FAIL_CLOSED behavior

## Configuration

### Client Options

```python
from fulcrum import FulcrumClient, FailureMode

client = FulcrumClient(
    host="localhost:50051",          # Fulcrum server address
    api_key="your-api-key",          # API key for authentication
    tenant_id="your-tenant-id",      # Default tenant ID
    on_failure=FailureMode.FAIL_OPEN,  # FAIL_OPEN or FAIL_CLOSED
    timeout_ms=500,                  # Request timeout in milliseconds
    enable_tls=True,                 # Enable TLS encryption
    ca_cert_path="/path/to/ca.crt",  # Custom CA certificate (optional)
)
```

### Environment Variables

```bash
export FULCRUM_HOST="localhost:50051"
export FULCRUM_API_KEY="your-api-key"
export FULCRUM_TENANT_ID="your-tenant-id"
export FULCRUM_TIMEOUT_MS="500"
```

```python
# Client auto-discovers from environment
client = FulcrumClient.from_env()
```

## API Reference

### FulcrumClient

The main client for interacting with Fulcrum.

```python
client = FulcrumClient(host, api_key, **options)
```

#### Methods

| Method | Description |
|--------|-------------|
| `envelope(workflow_id, **kwargs)` | Create a governance envelope |
| `evaluate(action, input_text, **context)` | Evaluate a policy decision |
| `get_cost(envelope_id)` | Get cost for an envelope |
| `list_policies(tenant_id)` | List active policies |
| `health_check()` | Check server connectivity |

### Envelope

Context manager for governed executions.

```python
with client.envelope(
    workflow_id="my-workflow",
    execution_id="optional-custom-id",  # Auto-generated if not provided
    metadata={"user": "alice"},
) as env:
    # Governed execution
    pass
```

#### Envelope Methods

| Method | Description |
|--------|-------------|
| `guard(action, input_text, **metadata)` | Check if action is allowed |
| `log(event_type, payload)` | Log an event for audit |
| `checkpoint()` | Create execution checkpoint |
| `get_cost()` | Get current execution cost |

## Error Handling

```python
from fulcrum import FulcrumClient
from fulcrum.exceptions import (
    FulcrumError,           # Base exception
    PolicyViolationError,   # Action blocked by policy
    BudgetExceededError,    # Budget limit reached
    ConnectionError,        # Server unreachable
    AuthenticationError,    # Invalid API key
    TimeoutError,           # Request timed out
)

client = FulcrumClient(host="localhost:50051", api_key="key")

try:
    with client.envelope(workflow_id="my-agent") as env:
        if env.guard("send_email", input_text="Hello"):
            send_email("Hello")
except PolicyViolationError as e:
    print(f"Policy violation: {e.policy_id}")
    print(f"Reason: {e.message}")
    print(f"Matched rules: {e.matched_rules}")
except BudgetExceededError as e:
    print(f"Budget exceeded: ${e.current_spend:.2f} / ${e.budget_limit:.2f}")
except ConnectionError as e:
    print(f"Cannot reach Fulcrum server: {e}")
    # Handle based on failure mode
except TimeoutError:
    print("Request timed out")
```

## Integration Examples

### LangChain Integration

```python
from langchain.agents import AgentExecutor
from fulcrum import FulcrumClient

client = FulcrumClient.from_env()

def governed_agent_run(agent: AgentExecutor, query: str):
    with client.envelope(workflow_id="langchain-agent") as env:
        # Check if query is allowed
        if not env.guard("process_query", input_text=query):
            return {"error": "Query blocked by policy"}

        # Run agent with governance wrapper
        for step in agent.iter(query):
            if "tool" in step:
                tool_name = step["tool"]
                tool_input = step["tool_input"]

                # Check tool usage
                if not env.guard(tool_name, input_text=str(tool_input)):
                    env.log("tool_blocked", {"tool": tool_name})
                    continue

                env.log("tool_executed", {"tool": tool_name})

        return agent.invoke(query)
```

### LlamaIndex Integration

```python
from llama_index import VectorStoreIndex
from fulcrum import FulcrumClient

client = FulcrumClient.from_env()

def governed_query(index: VectorStoreIndex, query: str):
    with client.envelope(workflow_id="llamaindex-rag") as env:
        # Pre-query governance check
        if not env.guard("query", input_text=query):
            raise ValueError("Query not permitted")

        # Execute query
        response = index.as_query_engine().query(query)

        # Log for audit
        env.log("query_completed", {
            "query": query,
            "response_length": len(str(response)),
        })

        return response
```

### OpenAI Function Calling

```python
import openai
from fulcrum import FulcrumClient

client = FulcrumClient.from_env()

def governed_function_call(messages, tools):
    with client.envelope(workflow_id="openai-functions") as env:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
        )

        # Check function calls before execution
        for tool_call in response.choices[0].message.tool_calls or []:
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments

            if not env.guard(func_name, input_text=func_args):
                env.log("function_blocked", {"function": func_name})
                continue

            # Execute approved function
            result = execute_function(func_name, func_args)
            env.log("function_executed", {
                "function": func_name,
                "success": True,
            })

        return response
```

## Cost Tracking

```python
with client.envelope(workflow_id="my-agent") as env:
    # ... agent execution ...

    # Get current cost
    cost = env.get_cost()
    print(f"Total cost: ${cost.total_usd:.4f}")
    print(f"Input tokens: {cost.input_tokens}")
    print(f"Output tokens: {cost.output_tokens}")
    print(f"LLM calls: {cost.llm_calls}")
```

## Async Support

```python
import asyncio
from fulcrum import AsyncFulcrumClient

async def main():
    client = AsyncFulcrumClient(
        host="localhost:50051",
        api_key="your-api-key"
    )

    async with client.envelope(workflow_id="async-agent") as env:
        allowed = await env.guard("action", input_text="hello")
        if allowed:
            result = await do_async_work()
            await env.log("completed", {"result": result})

asyncio.run(main())
```

## Documentation

Full documentation: [https://docs.fulcrum.dev](https://docs.fulcrum.dev)

## Support

- Email: support@fulcrum.dev
- Documentation: https://docs.fulcrum.dev
- Issues: Contact your account representative

---

## MCP Integration

Fulcrum provides a Model Context Protocol (MCP) server for AI agent governance. The `check_governance` tool allows agents to evaluate actions against enterprise policies before execution.

```python
# MCP Server Configuration
# mcp-name: io.github.Fulcrum-Governance/fulcrum
```

See [MCP Registry](https://registry.modelcontextprotocol.io/) for configuration details.
