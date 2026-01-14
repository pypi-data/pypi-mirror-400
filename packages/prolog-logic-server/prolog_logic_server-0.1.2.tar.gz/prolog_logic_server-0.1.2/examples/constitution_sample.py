"""
Constitution fact extraction sample using Ollama + Prolog rules.

Example:
  python examples/constitution_sample.py --ollama-model gpt-oss:20b \
    --input-file examples/constitution.txt
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from logic_server.core.session import (
    assert_facts,
    assert_rules,
    create_session,
    destroy_session,
    query,
)
from logic_server.llm.clients import OllamaLLM


FACT_SPEC = [
    "document(us_constitution)",
    "article(article_i)",
    "section(article_i, section_1)",
    "vests_power_in(legislative_power, congress_of_the_united_states)",
    "congress_consists_of(senate)",
    "congress_consists_of(house_of_representatives)",
    "section(article_i, section_2)",
    "house_term_years(2)",
    "representative_min_age_years(25)",
    "representative_citizenship_years(7)",
    "representative_must_be_inhabitant_of_state(true)",
    "section(article_i, section_3)",
    "senators_per_state(2)",
    "senator_term_years(6)",
    "article(article_ii)",
    "section(article_ii, section_1)",
    "vests_power_in(executive_power, president_of_the_united_states)",
    "president_term_years(4)",
    "president_min_age_years(35)",
    "president_citizenship_years(14)",
    "president_must_be_natural_born(true)",
    "article(article_iii)",
    "section(article_iii, section_1)",
    "vests_power_in(judicial_power, supreme_court)",
    "judges_hold_office_during_good_behavior(true)",
    "article(article_v)",
    "amendment_proposal_requires_two_thirds_each_house(true)",
    "amendment_ratification_requires_three_fourths_states(true)",
    "article(article_vi)",
    "constitution_is_supreme_law(true)",
]

RULES_PROGRAM = """
bicameral_legislature(congress_of_the_united_states) :-
    congress_consists_of(senate),
    congress_consists_of(house_of_representatives).

legislative_branch(congress_of_the_united_states) :-
    vests_power_in(legislative_power, congress_of_the_united_states).

executive_branch(president_of_the_united_states) :-
    vests_power_in(executive_power, president_of_the_united_states).

judicial_branch(supreme_court) :-
    vests_power_in(judicial_power, supreme_court).

separation_of_powers :-
    legislative_branch(Legislative),
    executive_branch(Executive),
    judicial_branch(Judicial),
    Legislative \\= Executive,
    Legislative \\= Judicial,
    Executive \\= Judicial.

representative_requirements(Age, CitizenshipYears) :-
    representative_min_age_years(Age),
    representative_citizenship_years(CitizenshipYears).

president_requirements(Age, CitizenshipYears) :-
    president_min_age_years(Age),
    president_citizenship_years(CitizenshipYears).

senate_term_longer_than_house :-
    senator_term_years(SenateYears),
    house_term_years(HouseYears),
    SenateYears > HouseYears.

each_state_has_two_senators :-
    senators_per_state(2).

amendment_requires_supermajorities :-
    amendment_proposal_requires_two_thirds_each_house(true),
    amendment_ratification_requires_three_fourths_states(true).

constitution_is_supreme :-
    constitution_is_supreme_law(true).
""".strip()


ASSERTION_QUERIES = [
    (
        "bicameral_legislature(congress_of_the_united_states).",
        "Congress is bicameral (Senate + House).",
    ),
    (
        "legislative_branch(congress_of_the_united_states).",
        "The Constitution vests legislative power in Congress.",
    ),
    (
        "executive_branch(president_of_the_united_states).",
        "The Constitution vests executive power in the President.",
    ),
    (
        "judicial_branch(supreme_court).",
        "The Constitution vests judicial power in the Supreme Court.",
    ),
    (
        "separation_of_powers.",
        "The Constitution separates legislative, executive, and judicial powers.",
    ),
    (
        "representative_requirements(Age, CitizenshipYears).",
        "Representatives must meet minimum age and citizenship requirements.",
    ),
    (
        "president_requirements(Age, CitizenshipYears).",
        "Presidents must meet minimum age and citizenship requirements.",
    ),
    (
        "senate_term_longer_than_house.",
        "Senators serve longer terms than Representatives.",
    ),
    (
        "each_state_has_two_senators.",
        "Each state has two senators.",
    ),
    (
        "amendment_requires_supermajorities.",
        "Amendments require supermajorities in Congress and the states.",
    ),
    (
        "constitution_is_supreme.",
        "The Constitution is the supreme law of the land.",
    ),
]


def parse_json_array(text: str) -> List[Dict[str, Any]]:
    raw = text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(raw[start : end + 1])


def load_excerpt(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def extract_facts(llm: OllamaLLM, excerpt: str) -> List[Dict[str, Any]]:
    system_prompt = (
        "Extract facts from the provided legal excerpt. "
        "Output ONLY a JSON array of objects with keys 'predicate' and 'args'. "
        "Use the fact spec exactly as provided; do not add extra facts."
    )
    user_prompt = (
        "Legal excerpt:\n"
        f"{excerpt}\n\n"
        "Fact spec (return exactly these facts if supported by the excerpt):\n"
        + "\n".join(f"- {line}" for line in FACT_SPEC)
    )
    response = llm.chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return parse_json_array(response)


def run_assertions(session_id: str) -> None:
    print("\nCommon-sense assertions:")
    for query_text, description in ASSERTION_QUERIES:
        result = query(
            session_id=session_id,
            query=query_text,
            max_solutions=3,
        )
        if not result.get("success"):
            print(f"- {description} false [error: {result.get('error')}]")
            continue
        if result.get("count", 0) == 0:
            print(f"- {description} false")
            continue
        solutions = result.get("solutions", [])
        if not solutions:
            print(f"- {description} true")
            continue
        bindings = [sol.get("Bindings", {}) for sol in solutions]
        if all(not binding for binding in bindings):
            print(f"- {description} true")
            continue
        print(f"- {description} true {bindings}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Constitution fact extraction sample.")
    parser.add_argument("--ollama-model", default="gpt-oss:20b")
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument(
        "--input-file",
        default="examples/constitution.txt",
        help="Path to a text file containing the Constitution.",
    )
    args = parser.parse_args()

    llm = OllamaLLM(model=args.ollama_model, base_url=args.ollama_base_url, temperature=0)
    excerpt_path = Path(args.input_file)
    excerpt = load_excerpt(excerpt_path)
    facts = extract_facts(llm, excerpt)

    session_id = create_session(metadata={"task": "constitution review"})
    try:
        result = assert_facts(session_id, facts)
        if not result["success"]:
            raise SystemExit(f"assert_facts failed: {result}")
        rules_result = assert_rules(session_id, [RULES_PROGRAM])
        if not rules_result["success"]:
            raise SystemExit(f"assert_rules failed: {rules_result}")
        print(f"Asserted {result['facts_added']} facts.")
        print(json.dumps(facts, indent=2))
        run_assertions(session_id)
    finally:
        destroy_session(session_id)


if __name__ == "__main__":
    main()
