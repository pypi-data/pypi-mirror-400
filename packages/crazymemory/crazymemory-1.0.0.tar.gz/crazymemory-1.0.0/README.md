# CrazyMemory Python SDK

The official Python SDK for CrazyMemory (Neural Fabric X) - The Universal Memory Layer for AI Agents.

## Installation

```bash
pip install crazymemory
```

Or with MCP support:

```bash
pip install crazymemory[mcp]
```

## Quick Start

```python
from crazymemory import CrazyMemory

# Initialize the client
memory = CrazyMemory(
    api_url="http://localhost:8000",
    api_key="cm_your_api_key_here"  # Get from https://app.crazymemory.ai/api-keys
)

# Store a memory
memory.store(
    content="User prefers dark mode in all applications",
    metadata={"type": "preference", "category": "ui"}
)

# Search memories
results = memory.search("user preferences", limit=5)
for result in results:
    print(result.content)

# Get context for a prompt
context = memory.get_context(
    query="What are the user's UI preferences?",
    max_tokens=2000
)
print(context)
```

## One-Line Integration

Make any AI "CrazyMemory-aware" with a single decorator:

```python
from crazymemory import fabric_aware

@fabric_aware
def my_ai_function(prompt):
    # Your AI logic here
    # Context is automatically injected
    return response

# Or use the quick sync helper
from crazymemory import quick_sync

# Sync before starting a conversation
context = quick_sync("What should I know about this user?")
```

## Core Features

### Memory Operations

```python
from crazymemory import CrazyMemory

memory = CrazyMemory()

# Store with metadata
memory.store(
    content="API uses port 8765",
    metadata={
        "type": "fact",
        "project": "neural-fabric",
        "tags": ["api", "config"]
    }
)

# Semantic search
results = memory.search("configuration settings")

# Get recent memories
recent = memory.get_recent(limit=10)

# Update a memory
memory.update("mem_abc123", content="Updated content")

# Delete a memory
memory.delete("mem_abc123")
```

### Context Building

```python
# Build context for AI prompts
context = memory.build_context(
    query="Help me with authentication",
    max_tokens=4000,
    include_recent=True
)

# NFP (Neural Fabric Protocol) context
nfp_context = memory.get_nfp_context(
    query="What are the coding standards?",
    agent_id="my-agent",
    include_project=True
)
```

### Agent Management

```python
# Register your agent
memory.register_agent(
    agent_id="my-python-agent",
    name="Python Assistant",
    capabilities=["code_generation", "debugging"]
)

# Add notes for other agents
memory.add_agent_note(
    agent_id="my-python-agent",
    content="Currently working on auth module",
    type="current_work"
)

# Get notes from all agents
notes = memory.get_agent_notes()
```

### Conflict Detection

```python
# Check for conflicts before storing
conflicts = memory.check_conflicts(
    content="We should use Redux for state management"
)

if conflicts.has_conflicts:
    print("Warning: This conflicts with existing memories!")
    for conflict in conflicts.items:
        print(f"  - {conflict.content}")
else:
    memory.store(content="We should use Redux for state management")
```

### Sync Operations

```python
# Manual sync
memory.sync(direction="bidirectional")

# Get sync status
status = memory.get_sync_status()
print(f"Last sync: {status.last_sync}")
print(f"Cloud connected: {status.cloud_connected}")
```

## MCP Integration

Use CrazyMemory as an MCP server with Claude Desktop:

```python
from crazymemory import install_mcp_server

# Install to Claude Desktop configuration
install_mcp_server()
```

Or use the MCP client directly:

```python
from crazymemory import MCPClient

mcp = MCPClient()

# Call MCP tools
result = await mcp.call_tool("fabric_search", {"query": "user preferences"})
```

## Configuration

```python
from crazymemory import CrazyMemory

memory = CrazyMemory(
    base_url="http://localhost:8765",  # API endpoint
    api_key="your-api-key",            # Optional API key
    timeout=30,                         # Request timeout
    auto_sync=True                      # Auto-sync on changes
)
```

### Environment Variables

```bash
export CRAZYMEMORY_URL="http://localhost:8765"
export CRAZYMEMORY_API_KEY="your-api-key"
```

## Examples

### Conversation Memory

```python
from crazymemory import CrazyMemory

memory = CrazyMemory()

# At the start of a conversation, get context
context = memory.build_context("Starting new coding session")

# During the conversation, store important information
memory.store(
    content="User wants to build a REST API with FastAPI",
    metadata={"type": "requirement", "session": "current"}
)

# At the end, sync everything
memory.sync()
```

### Multi-Agent Workflow

```python
from crazymemory import CrazyMemory

# Agent 1: Cursor
cursor_memory = CrazyMemory()
cursor_memory.register_agent("cursor", "Cursor IDE")
cursor_memory.store(
    content="Implementing user authentication",
    metadata={"agent": "cursor", "type": "current_work"}
)

# Agent 2: Claude (later)
claude_memory = CrazyMemory()
claude_memory.register_agent("claude", "Claude Chat")

# Claude can see what Cursor was working on
context = claude_memory.build_context("What was the last task?")
# Returns: "Cursor was implementing user authentication..."
```

## API Reference

### CrazyMemory Class

| Method | Description |
|--------|-------------|
| `store(content, metadata)` | Store a new memory |
| `search(query, limit, filter)` | Semantic search |
| `get_recent(limit)` | Get recent memories |
| `update(id, content, metadata)` | Update a memory |
| `delete(id)` | Delete a memory |
| `build_context(query, max_tokens)` | Build context for prompts |
| `register_agent(agent_id, name)` | Register an agent |
| `add_agent_note(agent_id, content)` | Add agent note |
| `check_conflicts(content)` | Check for conflicts |
| `sync(direction)` | Sync with cloud |

## Requirements

- Python 3.8+
- `requests` library
- Optional: `mcp` library for MCP integration

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- 📖 [Documentation](https://docs.neuralfabricx.com)
- 🐛 [Report Issues](https://github.com/devmubarak/crazymemory/issues)
- 💬 [Discord Community](https://discord.gg/neuralfabricx)
- 🌐 [Website](https://neuralfabricx.com)
