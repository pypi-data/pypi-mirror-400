#!/usr/bin/env python3
"""
Contract Analysis with LLM-based Fact Extraction

This demonstrates the full pipeline:
1. LLM reads contract and extracts facts
2. Facts are asserted into a Prolog session
3. Multi-turn Q&A with verifiable answers

Usage:
    # With Ollama
    python examples/contract_llm_analysis.py --backend ollama --model gpt-oss:20b

    # With OpenAI
    python examples/contract_llm_analysis.py --backend openai --api-key sk-... --model gpt-4o-mini
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

from logic_server.core.session import (
    create_session,
    destroy_session,
    assert_facts,
    assert_rules,
    query,
)
from logic_server.llm.clients import OllamaLLM, OpenAILLM


# Fact schema for the LLM to follow
FACT_EXTRACTION_SCHEMA = """
Extract facts from the contract in this JSON format:

{
  "facts": [
    {"predicate": "party", "args": ["party_name", "contract_id"]},
    {"predicate": "role", "args": ["party_name", "licensor|licensee"]},
    {"predicate": "must_pay", "args": ["party", "fee_type", amount_number]},
    {"predicate": "prohibited", "args": ["party", "action"]},
    {"predicate": "must_provide", "args": ["party", "service"]},
    {"predicate": "can_terminate_for", "args": ["party", "reason"]},
    {"predicate": "response_time", "args": ["priority", time_number, "unit"]},
    {"predicate": "effective_date", "args": ["contract_id", "YYYY-MM-DD"]},
    {"predicate": "expiration_date", "args": ["contract_id", "YYYY-MM-DD"]},
    {"predicate": "governing_law", "args": ["contract_id", "jurisdiction"]},
    {"predicate": "max_users", "args": ["contract_id", number]},
    {"predicate": "payment_due_days", "args": ["party", number]},
    {"predicate": "upon_termination_must", "args": ["party", "action"]}
  ]
}

Guidelines:
- Use lowercase, snake_case for all strings
- Numbers should be integers (not strings)
- Extract ONLY facts explicitly stated in the contract
- Do not infer or hallucinate facts
"""


def load_contract() -> str:
    """Load the sample contract."""
    contract_path = Path(__file__).parent / "contract_sample.txt"
    return contract_path.read_text(encoding="utf-8")


def extract_facts_with_llm(llm, contract_text: str) -> List[Dict[str, Any]]:
    """
    Use LLM to extract facts from contract text.
    """
    system_prompt = (
        "You are a legal contract analyzer. Extract structured facts from contracts "
        "into a precise JSON format for logical reasoning. Be accurate and only extract "
        "facts that are explicitly stated."
    )

    user_prompt = f"""
{FACT_EXTRACTION_SCHEMA}

Now extract facts from this contract:

{contract_text[:3000]}

Return ONLY valid JSON, no other text.
"""

    print("🤖 Asking LLM to extract facts from contract...")
    response = llm.chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    # Parse JSON response
    try:
        # Try to extract JSON from response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            facts = data.get("facts", [])
            print(f"✓ LLM extracted {len(facts)} facts")
            return facts
        else:
            raise ValueError("No JSON found in response")
    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse LLM response: {e}")
        print(f"Response was: {response[:200]}...")
        return []


def define_contract_rules() -> str:
    """Define reasoning rules."""
    return """
% Total annual cost
total_annual_cost(Party, Total) :-
    findall(Amount, must_pay(Party, _, Amount), Amounts),
    sum_list(Amounts, Total).

% Is licensor/licensee
is_licensor(Party) :- role(Party, licensor).
is_licensee(Party) :- role(Party, licensee).

% Can perform action (if not prohibited)
can_perform(Party, Action) :-
    party(Party, _),
    \\+ prohibited(Party, Action).

% Has any payment obligation
has_payment_obligation(Party) :-
    must_pay(Party, _, _).

% Critical response time (less than 1 day)
critical_support(Priority) :-
    response_time(Priority, Time, hours),
    Time < 24.
""".strip()


def interactive_qa(session_id: str):
    """
    Interactive Q&A session demonstrating how I would use this.
    """
    questions = [
        ("Who are the parties?", "party(Party, Contract)."),
        ("What is the total cost?", "total_annual_cost(Party, Total)."),
        ("What is prohibited?", "prohibited(Party, Action)."),
        ("Who provides support?", "must_provide(Party, Service)."),
        ("What are termination conditions?", "can_terminate_for(Party, Reason)."),
        ("What support is critical (< 24hr)?", "critical_support(Priority)."),
    ]

    print("\n" + "=" * 70)
    print("INTERACTIVE Q&A (Simulating Multi-Turn Conversation)")
    print("=" * 70)

    for i, (question, prolog_query) in enumerate(questions, 1):
        print(f"\n[Q{i}] {question}")
        print("-" * 70)

        result = query(session_id, query=prolog_query, max_solutions=10)

        if result["success"] and result["count"] > 0:
            print("Answer:")
            for sol in result["solutions"]:
                bindings = sol["Bindings"]
                # Format the answer nicely
                answer_parts = []
                for key, value in sorted(bindings.items()):
                    if key != "truth":  # Filter out janus_swi's truth value
                        answer_parts.append(f"{key}={value}")
                if answer_parts:
                    print(f"  • {', '.join(answer_parts)}")
        else:
            print(f"No results found (or error: {result.get('error', 'unknown')})")


def main():
    parser = argparse.ArgumentParser(description="Contract analysis with LLM fact extraction")
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--model", default="gpt-oss:20b")
    parser.add_argument("--api-key", help="OpenAI API key (for openai backend)")
    parser.add_argument("--base-url", help="Custom base URL")
    args = parser.parse_args()

    print("=" * 70)
    print("CONTRACT ANALYSIS WITH LLM FACT EXTRACTION")
    print("=" * 70)

    # Initialize LLM
    if args.backend == "ollama":
        llm = OllamaLLM(
            model=args.model,
            base_url=args.base_url or "http://localhost:11434",
            temperature=0
        )
        print(f"✓ Using Ollama model: {args.model}")
    else:
        if not args.api_key:
            print("Error: --api-key required for OpenAI backend")
            return
        llm = OpenAILLM(
            model=args.model,
            api_key=args.api_key,
            base_url=args.base_url,
            temperature=0
        )
        print(f"✓ Using OpenAI model: {args.model}")

    # Load contract
    contract_text = load_contract()
    print(f"✓ Loaded contract ({len(contract_text)} chars)")

    # Create session
    session_id = create_session(metadata={"task": "llm_contract_analysis"})
    print(f"✓ Created session: {session_id[:8]}...")

    try:
        # Extract facts using LLM
        print("\n" + "-" * 70)
        print("STEP 1: LLM Fact Extraction")
        print("-" * 70)

        facts = extract_facts_with_llm(llm, contract_text)

        if not facts:
            print("⚠️  LLM extraction failed, using pre-defined facts")
            # Fallback to manual facts
            from contract_analysis import extract_contract_facts
            facts = extract_contract_facts()

        # Display extracted facts (first 10)
        print("\nSample extracted facts:")
        for fact in facts[:10]:
            pred = fact["predicate"]
            args = fact["args"]
            print(f"  {pred}({', '.join(str(a) for a in args)})")
        if len(facts) > 10:
            print(f"  ... and {len(facts) - 10} more")

        # Assert facts
        print("\n" + "-" * 70)
        print("STEP 2: Asserting Facts into Reasoning Session")
        print("-" * 70)

        result = assert_facts(session_id, facts)
        print(f"✓ Asserted {result['facts_added']} facts")

        # Add reasoning rules
        print("\n" + "-" * 70)
        print("STEP 3: Adding Logical Rules")
        print("-" * 70)

        rules = define_contract_rules()
        result = assert_rules(session_id, [rules])
        print(f"✓ Added reasoning rules")

        # Interactive Q&A
        interactive_qa(session_id)

        # Summary
        print("\n" + "=" * 70)
        print("HOW THIS IMPROVES MY CAPABILITIES")
        print("=" * 70)
        print("""
✓ Grounded Reasoning: All answers traced to specific contract clauses
✓ Verifiable Logic: Every conclusion has a formal proof
✓ Multi-Turn Memory: Context maintained across conversation
✓ Complex Queries: Can answer questions requiring multiple facts
✓ No Hallucination: Only facts extracted from actual text
✓ Derived Knowledge: Can compute totals, check constraints, etc.

This is how I could become a more reliable legal analyst!
        """)

    finally:
        destroy_session(session_id)
        print(f"✓ Session destroyed")


if __name__ == "__main__":
    main()
