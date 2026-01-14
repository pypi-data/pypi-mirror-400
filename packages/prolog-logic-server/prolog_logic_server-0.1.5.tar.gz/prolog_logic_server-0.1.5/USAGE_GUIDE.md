# Usage Guide: Logic Server

## Overview

This project provides three ways to use the logic solver:

1. **CLI Query** (`logic_server.cli.main`) - run queries against Prolog fact files.
2. **MCP Server** (`logic_server.mcp.server` and `logic_server.mcp.stateful`) - exposes tools to any MCP client.
3. **LLM Integration** (`examples/sample.py`) - demo of an LLM calling the solver via JSON tool calls.

## Installation

```bash
python -m pip install -e .
```

## Method 1: CLI Query

```bash
python -m logic_server.cli.main examples/puzzles/simple_pet_facts.pl --query "person(P)."
python -m logic_server.cli.main examples/puzzles/complex_pet_facts.pl --query "pet(P)."
python -m logic_server.cli.main examples/puzzles/complex_pet_facts.pl --query "person(P)." --max-solutions 3
```

## Method 2: MCP Server

### Run the servers

```bash
python -m logic_server.mcp.server
python -m logic_server.mcp.stateful
```

### Configure Claude Desktop

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "prolog-reasoning": {
      "command": "/absolute/path/to/python3",
      "args": ["-m", "logic_server.mcp.stateful"]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/python3` with your actual Python path. Find it by running:
```bash
which python3
```

For virtual environments:
```bash
cd /path/to/prolog
which python3  # Shows: /path/to/prolog/.venv/bin/python3
```

### Stateless tool

- Requires SWI-Prolog (`swipl`) available on your PATH.
- `logic_query(facts, rules_program, query, max_solutions, offset, limit, format, group_by, return_csv)` queries a single set of facts.
- `validate_query(facts, rules_program, query)` validates a query without executing.
- `list_predicates(facts, rules_program)` lists predicates in the provided facts/rules.

**Fact format**:
- Provide Prolog fact strings (e.g., `"person(alice)."`).

### Stateful tools

- `create_session(metadata)`
- `destroy_session(session_id)`
- `assert_facts(session_id, facts)`
- `assert_rules(session_id, rules)` - rules can be provided with or without trailing periods
- `query(session_id, query, max_solutions=5, offset=0, limit=None, format="raw")`
- `validate_query(session_id, query)`
- `list_predicates(session_id)`

**Note on Rules**: Rules can be provided with or without trailing periods (`.`). The system automatically ensures proper Prolog syntax:
```python
# Both formats work:
rules = ["has_pet(Person, Pet) :- owner(House, Person), pet(House, Pet)"]  # Without period
rules = ["has_pet(Person, Pet) :- owner(House, Person), pet(House, Pet)."]  # With period
```

## Method 3: LLM Integration (Optional)

```bash
python examples/sample.py --backend openai --openai-api-key "sk-..." --openai-model gpt-4o-mini
python examples/sample.py --backend ollama --ollama-model gpt-oss-20b
```

## End-to-end Example Script

See Method 3.

## Troubleshooting

- If MCP tools do not appear, confirm the JSON config path and restart the client.
- For OpenAI, ensure `OPENAI_API_KEY` is set.
- For Ollama, verify the server is running and the model is pulled.
