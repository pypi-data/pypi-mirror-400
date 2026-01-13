## Datagusto SDK (Safety Middleware)

DatagustoSafetyMiddleware is a LangChain/LangGraph middleware that:

- Extracts tool definitions from requests and (optionally) registers them to your Datagusto backend.
- Submits user instructions for alignment.
- Calls safety validation before and after tool execution, blocking execution when the backend returns `should_proceed = false`.

This package is published as `datagusto-sdk` and exposes `DatagustoSafetyMiddleware`.

### Features

- Tool definition extraction (names, descriptions, JSON schemas for input/output).
- Automatic registration diffing (skips duplicate payloads).
- Alignment submission for the latest user instruction.
- Tool-level validation on start/end with structured payloads.
- Verbose logging for request/response bodies (optional).

### Requirements

- Python >= 3.12
- Dependencies: langchain, langgraph

### Installation

```bash
pip install datagusto-sdk
```

### Quickstart (LangChain agent)

```python
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.messages import HumanMessage
from datagusto_sdk import DatagustoSafetyMiddleware

@tool
def ping(msg: str) -> str:
    return f"pong: {msg}"

middleware = DatagustoSafetyMiddleware(
    verbose=True,
    include_schema=True,
    tool_filter=None,  # optional: list of tool names to register
)

agent = create_agent(
    model="claude-3-5-sonnet-latest",
    tools=[ping],
    middleware=[middleware],
)

agent.invoke({"messages": [HumanMessage("ping please")]})
```

### Configuration

- Environment variables (read automatically if args not provided):
  - `SERVER_URL`: Base URL for Datagusto backend (e.g., `https://api.example.com`)
  - `API_KEY`: Bearer token for API calls
- Runtime options:
  - `verbose` (bool): log request/response bodies; default True.
  - `include_schema` (bool): include JSON schemas for tool IO; default True.
  - `tool_filter` (list[str] | None): only register tools with names in this list.

### Behavior overview

1. `wrap_model_call`
   - Extract tools from `request.tools`, build payload, hash it.
   - If `server_url` and `api_key` are set and payload hash changed, call register API.
   - Extract latest human message and (if changed) post alignment; store `session_id` for validation.
2. `wrap_tool_call`
   - On each tool call, if `session_id` exists, call validate API with `on_start`.
   - If backend responds `should_proceed = false`, raises `RuntimeError` to block.
   - After tool runs, call validate API with `on_end`; may block further processing similarly.

### Error handling

- Network / HTTP errors are logged (when `verbose=True`) but do not crash the agent unless the backend explicitly blocks via `should_proceed = false`.
- Validation blocks raise `RuntimeError` with the backend response for transparency.

### License

MIT License. See `LICENSE`.
