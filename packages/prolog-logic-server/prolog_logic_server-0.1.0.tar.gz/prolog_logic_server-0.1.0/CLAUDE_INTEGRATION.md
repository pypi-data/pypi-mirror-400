# How to Add Logic Server Capabilities to Claude

This guide explains how to connect the Prolog logic server to Claude so I can use it during conversations.

## Quick Answer

**Use the MCP (Model Context Protocol) server!** This project already implements MCP servers that Claude Desktop can connect to.

## Option 1: MCP Integration (Recommended) ⭐

### What is MCP?

MCP (Model Context Protocol) is Claude's standard way to connect to external tools. Once configured, I can:
- Create reasoning sessions
- Assert facts from documents you share
- Query with Prolog logic
- Build knowledge across our conversation

### Setup Steps

#### 1. Install the Package

```bash
pip install prolog-logic-server
```

This installs the `logic_server_mcp` command globally.

#### 2. Test the MCP Server

```bash
# Test the stateful server (recommended)
logic_server_mcp
```

You should see it start without errors. Press Ctrl+C to stop.

#### 3. Configure Claude Desktop

**macOS/Linux:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:**
Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "logic-reasoning": {
      "command": "logic_server_mcp"
    }
  }
}
```

**Alternative: Development Mode (for contributors)**

If you're developing the package locally:

```bash
# Install in development mode
cd logic_server
pip install -e ".[mcp]"
```

Then use the module invocation in your config:
```json
{
  "mcpServers": {
    "logic-reasoning": {
      "command": "python3",
      "args": ["-m", "logic_server.mcp.stateful"]
    }
  }
}
```

#### 4. Restart Claude Desktop

Quit Claude Desktop completely and restart it.

#### 5. Verify It Works

Look for the 🔌 icon in Claude Desktop. You should see "prolog-reasoning" connected.

### How I'll Use It

Once connected, I can:

```
You: "Analyze this contract for me"
[You paste contract text]

Me: "I'll use the Prolog reasoning system to analyze this..."
[I call create_session()]
[I extract facts and call assert_facts()]
[I add rules with assert_rules()]
[I query for answers]

You: "What's the total cost?"
Me: [I call query() with the session]
"The total cost is $144,000/year..."
[With proof chain from Prolog!]
```

### Available Tools

Once configured, I'll have access to:

| Tool | What I Can Do |
|------|---------------|
| `create_session` | Start a new reasoning session |
| `destroy_session` | Clean up a session |
| `list_sessions` | See all active sessions |
| `assert_facts` | Add facts to a session |
| `assert_rules` | Add Prolog rules |
| `retract_facts` | Remove facts |
| `retract_rules` | Remove rules |
| `query_facts` | List accumulated facts |
| `query` | Run Prolog queries |
| `get_session_stats` | Get session statistics |
| `prolog_query` | One-shot queries (stateless) |

## Option 2: Custom Tool Integration via API

If you're using the Anthropic API directly (not Claude Desktop):

### 1. Expose as HTTP API

Create a simple Flask/FastAPI server:

```python
# api_server.py
from flask import Flask, request, jsonify
from logic_server.core.session import *

app = Flask(__name__)

@app.route('/session', methods=['POST'])
def create():
    session_id = create_session()
    return jsonify({"session_id": session_id})

@app.route('/session/<session_id>/facts', methods=['POST'])
def add_facts(session_id):
    facts = request.json.get('facts', [])
    result = assert_facts(session_id, facts)
    return jsonify(result)

@app.route('/session/<session_id>/query', methods=['POST'])
def run_query(session_id):
    query_text = request.json.get('query')
    result = query(session_id, query=query_text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### 2. Define Tools for Claude API

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

tools = [
    {
        "name": "create_prolog_session",
        "description": "Create a new Prolog reasoning session for multi-turn logic",
        "input_schema": {
            "type": "object",
            "properties": {},
        }
    },
    {
        "name": "assert_facts",
        "description": "Add facts to a Prolog session",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "facts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "predicate": {"type": "string"},
                            "args": {"type": "array"}
                        }
                    }
                }
            },
            "required": ["session_id", "facts"]
        }
    },
    {
        "name": "prolog_query",
        "description": "Query a Prolog session",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "query": {"type": "string"}
            },
            "required": ["session_id", "query"]
        }
    }
]

# Use in conversation
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=tools,
    messages=[
        {"role": "user", "content": "Analyze this contract..."}
    ]
)
```

### 3. Handle Tool Calls

```python
import requests

def handle_tool_call(tool_name, tool_input):
    if tool_name == "create_prolog_session":
        resp = requests.post("http://localhost:5000/session")
        return resp.json()

    elif tool_name == "assert_facts":
        resp = requests.post(
            f"http://localhost:5000/session/{tool_input['session_id']}/facts",
            json={"facts": tool_input['facts']}
        )
        return resp.json()

    elif tool_name == "prolog_query":
        resp = requests.post(
            f"http://localhost:5000/session/{tool_input['session_id']}/query",
            json={"query": tool_input['query']}
        )
        return resp.json()
```

## Option 3: Direct Python Integration

If you're building a custom application:

```python
from anthropic import Anthropic
from logic_server.core.session import *

client = Anthropic()

# Create a session at the start of conversation
session_id = create_session()

def chat_with_logic(user_message):
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=f"""
        You have access to a Prolog reasoning session (ID: {session_id}).
        When analyzing documents or doing logical reasoning:
        1. Extract facts from the text
        2. Use assert_facts() to add them
        3. Use query() to answer questions
        All your reasoning will be verifiable!
        """,
        messages=[{"role": "user", "content": user_message}],
        tools=[...]  # Define tools as above
    )

    # Handle tool calls
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            # Send result back to Claude

    return response
```

## Performance Optimization

### Use MQI for Speed

Install for 50x performance boost:

```bash
pip install janus-swi
```

Then the system automatically uses the fast MQI solver!

### Configure Pool Size

For high-throughput applications:

```python
from logic_server.core.mqi_solver import get_mqi_solver

# Get pooled solver
solver = get_mqi_solver(pool_size=4)
```

## Example: How I Would Use It

### Conversation Flow

```
👤 User: "Here's a contract. What obligations does Acme have?"

🤖 Claude: I'll analyze this using the Prolog reasoning system.

[I call: create_session()]
Session created: abc123

[I extract facts from contract text]
[I call: assert_facts(abc123, [
  {"predicate": "must_pay", "args": ["acme", "license_fee", 120000]},
  {"predicate": "must_pay", "args": ["acme", "support_fee", 24000]},
  {"predicate": "upon_termination_must", "args": ["acme", "cease_use"]},
  ...
])]

[I call: query(abc123, "has_obligation(acme, Obligation).")]

Based on the Prolog analysis, Acme has 5 obligations:
1. license_fee - $120,000 annually
2. support_fee - $24,000 annually
3. cease_use - upon termination
4. return_software - upon termination
5. pay_outstanding - upon termination

This is verified by formal logic!

👤 User: "What if they're 3 months late on payment?"

🤖 Claude: Let me calculate that with Prolog rules...

[I call: assert_rules(abc123, [
  "late_penalty(Party, Principal, Months, Total) :-
     must_pay(Party, _, Principal),
     late_penalty_percent(Party, Rate),
     Total is Principal * (Rate/100) * Months."
])]

[I call: query(abc123, "late_penalty(acme, 120000, 3, Total).")]

The late payment penalty would be $5,400
(1.5% per month × 3 months × $120,000 principal)

This calculation is formally verified!
```

## Troubleshooting

### MCP Server Not Showing Up

1. Check the config file path is correct
2. Ensure JSON is valid (use jsonlint.com)
3. Check logs: `~/Library/Logs/Claude/`
4. Restart Claude Desktop completely

### Import Errors

```bash
# Make sure package is installed
pip install prolog-logic-server

# Verify
python -c "import logic_server.mcp.stateful; print('OK')"

# Or check the command is available
which logic_server_mcp
```

### Performance Issues

Install janus-swi for 50x speedup:
```bash
pip install janus-swi
```

## Testing the Integration

Once configured, test with:

```
You: "Test the Prolog system"

Me: [I'll call create_session, assert some facts, and query them]
```

If I can successfully do that, the integration is working!

## What You Get

Once integrated, I become capable of:

✅ **Verifiable reasoning** - Every answer has a proof
✅ **Persistent memory** - Knowledge accumulates across turns
✅ **Complex logic** - Can handle sophisticated constraints
✅ **Grounded facts** - No hallucination, only verified data
✅ **Computational reasoning** - Can calculate, derive, infer
✅ **Multi-document analysis** - Build knowledge graphs

## Next Steps

1. **Try MCP integration first** (easiest)
2. **Test with contract analysis example**
3. **Experiment with your own documents**
4. **Build custom applications** using the API

Need help? The MCP server logs everything to help debug!
