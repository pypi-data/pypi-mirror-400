"""
end_to_end_llm_prolog_example.py

End-to-end example of a swappable LLM abstraction with:
- Ollama HTTP adapter (for gpt-oss-20b or any local model)
- OpenAI Chat Completions adapter

The LLM can call a `prolog_query` tool to query facts.
"""

import argparse
import json
import requests
from openai import OpenAI
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from logic_server.core.solver import prolog_query


# =============================
# 1) Common data structures
# =============================

@dataclass
class ToolCall:
    name: str
    arguments: Any  # usually a JSON string for OpenAI-style tools
    id: Optional[str] = None  # OpenAI provides an id; Ollama may not


@dataclass
class ChatResult:
    role: str
    content: str
    tool_calls: List[ToolCall]

    def to_message(self) -> Dict[str, Any]:
        """
        Convert back into an OpenAI/Ollama-style chat message dict.
        """
        msg: Dict[str, Any] = {
            "role": self.role,
            "content": self.content,
        }
        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments,
                    },
                }
                for tc in self.tool_calls
            ]
        return msg


class LLMClient:
    """
    Abstract LLM interface. Different backends (Ollama, OpenAI, etc.)
    implement .chat() so the rest of the code can stay the same.
    """

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatResult:
        raise NotImplementedError


# =============================
# 2) Concrete adapters
# =============================

class OllamaLLMClient(LLMClient):
    """
    LLM client for Ollama's /api/chat endpoint.

    Docs: https://ollama.readthedocs.io/en/api/  (chat with tools) :contentReference[oaicite:2]{index=2}
    """

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatResult:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        resp = requests.post(f"{self.base_url}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        msg = data["message"]
        tool_calls: List[ToolCall] = []
        for tc in msg.get("tool_calls", []):
            tool_calls.append(
                ToolCall(
                    id=tc.get("id"),
                    name=tc["function"]["name"],
                    arguments=tc["function"]["arguments"],
                )
            )

        return ChatResult(
            role=msg.get("role", "assistant"),
            content=msg.get("content", "") or "",
            tool_calls=tool_calls,
        )


class OpenAILLMClient(LLMClient):
    """
    LLM client for OpenAI's /v1/chat/completions with tools. :contentReference[oaicite:3]{index=3}
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
    ):
        normalized_base = base_url.rstrip("/")
        if not normalized_base.endswith("/v1"):
            normalized_base = f"{normalized_base}/v1"

        self.client = OpenAI(api_key=api_key, base_url=normalized_base)
        self.model = model

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatResult:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
        )

        choice = response.choices[0].message
        tool_calls: List[ToolCall] = []
        if choice.tool_calls:
            for tc in choice.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=tc.function.arguments,
                    )
                )

        return ChatResult(
            role=choice.role or "assistant",
            content=choice.content or "",
            tool_calls=tool_calls,
        )


# =============================
# 3) Tool spec: prolog_query
# =============================

# Generic facts schema:
#   Fact = { "predicate": string, "args": (string|number|boolean)[] }

PROLOG_TOOL = {
    "type": "function",
    "function": {
        "name": "prolog_query",
        "description": "Run a Prolog query using structured facts and optional base knowledge packs.",
        "parameters": {
            "type": "object",
            "properties": {
                "facts": {
                    "type": "array",
                    "description": "Ground facts as predicate + argument list.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "predicate": {
                                "type": "string",
                                "description": "Predicate name, e.g. 'parent', 'edge', 'forbidden'.",
                            },
                            "args": {
                                "type": "array",
                                "description": "Arguments as strings, numbers, or booleans.",
                                "items": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "number"},
                                        {"type": "boolean"},
                                    ]
                                },
                            },
                        },
                        "required": ["predicate", "args"],
                    },
                },
                "rules_program": {
                    "type": "string",
                    "description": "Optional extra Prolog rules as plain text.",
                },
                "base_knowledge": {
                    "type": "array",
                    "description": "IDs of predefined Prolog knowledge packs.",
                    "items": {"type": "string"},
                },
                "query": {
                    "type": "string",
                    "description": "The Prolog query to run, e.g. 'person(P).'",
                },
                "max_solutions": {
                    "type": "integer",
                    "description": "Maximum number of solutions to return.",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}

TOOLS = [PROLOG_TOOL]


# =============================
# 4) Prolog tool implementation (stub)
# =============================

def prolog_query_tool(
    facts: Optional[List[Dict[str, Any]]] = None,
    rules_program: Optional[str] = None,
    base_knowledge: Optional[List[str]] = None,
    query: str = "",
    max_solutions: int = 5,
) -> Dict[str, Any]:
    """
    This is where you integrate your real Prolog engine (SWI, Tau, etc.).

    For demonstration, we delegate to the bundled minimal fact query engine.
    """
    return prolog_query(
        facts=facts or [],
        base_knowledge=base_knowledge,
        rules_program=rules_program,
        query=query,
        max_solutions=max_solutions,
    )


# =============================
# 5) Orchestration: tool-calling loop
# =============================

SYSTEM_PROMPT = """
You are a reasoning assistant. You can call a tool named `prolog_query` to solve logic
puzzles and constraint problems. Prefer using the tool when the user asks questions
about who owns what, how entities are related, or which assignments satisfy all conditions.
"""

USER_PET_PUZZLE = """
There are three friends: Alice, Bob, and Carol.
Each owns a different pet: a cat, a dog, or a fish.

- Alice does not own the cat or the dog.
- Bob owns a mammal.
- Bob does not own the dog.
- Carol does not own the cat.

Who owns which pet? Explain your reasoning.
"""


def handle_tool_call(tc: ToolCall) -> Dict[str, Any]:
    """
    Dispatch a single tool call to the appropriate local implementation.
    """
    if tc.name == "prolog_query":
        # arguments may arrive as a JSON string from the model
        if isinstance(tc.arguments, str):
            args = json.loads(tc.arguments)
        else:
            args = tc.arguments
        return prolog_query_tool(**args)
    else:
        return {"success": False, "error": f"Unknown tool {tc.name}"}


def trace_log(enabled: bool, label: str, payload: Any) -> None:
    """
    Pretty-print trace information when tracing is enabled.
    """
    if not enabled:
        return
    print(f"\n--- {label} ---")
    if isinstance(payload, str):
        print(payload)
        return
    try:
        print(json.dumps(payload, indent=2))
    except TypeError:
        print(payload)


def run_pet_puzzle_conversation(llm: LLMClient, trace: bool = False) -> None:
    """
    Full loop:
      1. Send system + user message + tool schema
      2. If the LLM requests a tool call, run `prolog_query_tool`
      3. Send tool output back as a tool message
      4. Ask the LLM again for the final natural language answer
    """

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PET_PUZZLE},
    ]

    trace_log(trace, "Initial messages", messages)

    while True:
        # 1) Ask the LLM
        result = llm.chat(messages, tools=TOOLS)
        assistant_msg = result.to_message()
        trace_log(trace, "LLM reply", assistant_msg)
        messages.append(assistant_msg)

        if result.tool_calls:
            # 2) Execute each tool call and append tool results
            for tc in result.tool_calls:
                trace_log(trace, f"Tool call requested: {tc.name}", tc.arguments)
                tool_output = handle_tool_call(tc)
                tool_msg: Dict[str, Any] = {
                    "role": "tool",
                    "content": json.dumps(tool_output),
                    "name": tc.name,
                }
                # OpenAI-style models expect tool_call_id; Ollama can ignore it
                if tc.id:
                    tool_msg["tool_call_id"] = tc.id
                messages.append(tool_msg)
                trace_log(trace, "Tool output", tool_output)

            # 3) Go around the loop again so LLM can use tool results
            trace_log(trace, "Messages so far", messages)
            continue

        # No tool_calls: this should be the final answer.
        trace_log(trace, "Final messages", messages)
        print("\n=== FINAL ANSWER ===\n")
        print(result.content.strip())
        break


# =============================
# 6) Entry point
# =============================

if __name__ == "__main__":
    # You can switch backends just by changing which client you instantiate.

    parser = argparse.ArgumentParser(description="End-to-end logic server sample.")
    parser.add_argument("--backend", default="openai", choices=["openai", "ollama"])
    parser.add_argument("--openai-api-key")
    parser.add_argument("--openai-model", default="gpt-4o-mini")
    parser.add_argument("--openai-base-url", default="https://api.openai.com/v1")
    parser.add_argument("--ollama-model", default="gpt-oss-20b")
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument("--no-trace", action="store_false", dest="trace")
    parser.set_defaults(trace=True)
    args = parser.parse_args()

    if args.backend == "ollama":
        llm = OllamaLLMClient(model=args.ollama_model, base_url=args.ollama_base_url)
    else:
        if not args.openai_api_key:
            raise SystemExit("--openai-api-key is required when --backend=openai")
        llm = OpenAILLMClient(
            api_key=args.openai_api_key,
            model=args.openai_model,
            base_url=args.openai_base_url,
        )

    run_pet_puzzle_conversation(llm, trace=args.trace)
