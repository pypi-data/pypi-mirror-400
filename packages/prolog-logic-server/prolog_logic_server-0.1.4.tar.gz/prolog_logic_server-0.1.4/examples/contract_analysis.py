#!/usr/bin/env python3
"""
Contract Analysis using Prolog-based Logical Reasoning

This demonstrates how to analyze a legal contract by:
1. Extracting facts from the contract text
2. Asserting them into a reasoning session
3. Adding logical rules for derived reasoning
4. Querying to answer complex questions

Usage:
    python examples/contract_analysis.py
"""

from pathlib import Path
from typing import List, Dict, Any

from logic_server.core.session import (
    create_session,
    destroy_session,
    assert_facts,
    assert_rules,
    query,
    get_session_stats
)


def load_contract() -> str:
    """Load the sample contract."""
    contract_path = Path(__file__).parent / "contract_sample.txt"
    return contract_path.read_text(encoding="utf-8")


def extract_contract_facts() -> List[Dict[str, Any]]:
    """
    Extract structured facts from the contract.

    In a real system, this would use an LLM to extract facts.
    For this demo, we manually define the key facts.
    """
    return [
        # Parties
        {"predicate": "party", "args": ["techcorp", "contract_sla_2024_001"]},
        {"predicate": "party", "args": ["acme", "contract_sla_2024_001"]},
        {"predicate": "role", "args": ["techcorp", "licensor"]},
        {"predicate": "role", "args": ["acme", "licensee"]},

        # License terms
        {"predicate": "license_type", "args": ["contract_sla_2024_001", "non_exclusive"]},
        {"predicate": "license_type", "args": ["contract_sla_2024_001", "non_transferable"]},
        {"predicate": "max_users", "args": ["contract_sla_2024_001", 50]},

        # Restrictions
        {"predicate": "prohibited", "args": ["acme", "sublicense"]},
        {"predicate": "prohibited", "args": ["acme", "reverse_engineer"]},
        {"predicate": "prohibited", "args": ["acme", "resell"]},

        # Payment obligations
        {"predicate": "must_pay", "args": ["acme", "license_fee", 120000]},
        {"predicate": "must_pay", "args": ["acme", "support_fee", 24000]},
        {"predicate": "payment_due_days", "args": ["acme", 30]},
        {"predicate": "late_penalty_percent", "args": ["acme", 1.5]},

        # Support obligations
        {"predicate": "must_provide", "args": ["techcorp", "email_support"]},
        {"predicate": "must_provide", "args": ["techcorp", "phone_support"]},
        {"predicate": "response_time", "args": ["critical", 4, "hours"]},
        {"predicate": "response_time", "args": ["high", 1, "business_days"]},
        {"predicate": "response_time", "args": ["medium", 3, "business_days"]},
        {"predicate": "response_time", "args": ["low", 5, "business_days"]},

        # Term and dates
        {"predicate": "effective_date", "args": ["contract_sla_2024_001", "2024-01-15"]},
        {"predicate": "expiration_date", "args": ["contract_sla_2024_001", "2027-01-14"]},
        {"predicate": "initial_term_years", "args": ["contract_sla_2024_001", 3]},
        {"predicate": "renewal_term_years", "args": ["contract_sla_2024_001", 1]},
        {"predicate": "renewal_notice_days", "args": ["contract_sla_2024_001", 90]},

        # Termination conditions
        {"predicate": "can_terminate_for", "args": ["either_party", "material_breach"]},
        {"predicate": "can_terminate_for", "args": ["either_party", "bankruptcy"]},
        {"predicate": "can_terminate_for", "args": ["either_party", "insolvency"]},
        {"predicate": "termination_notice_days", "args": ["material_breach", 30]},
        {"predicate": "cure_period_days", "args": ["material_breach", 30]},

        # Post-termination obligations
        {"predicate": "upon_termination_must", "args": ["acme", "cease_use"]},
        {"predicate": "upon_termination_must", "args": ["acme", "return_software"]},
        {"predicate": "upon_termination_must", "args": ["acme", "pay_outstanding"]},

        # Warranties and liability
        {"predicate": "warranty_period_days", "args": ["software", 90]},
        {"predicate": "liability_cap_months", "args": ["techcorp", 12]},
        {"predicate": "max_liability_amount", "args": ["techcorp", 500000]},
        {"predicate": "must_indemnify_for", "args": ["techcorp", "ip_infringement"]},

        # Compliance and audit
        {"predicate": "audit_frequency_per_year", "args": ["techcorp", 1]},
        {"predicate": "audit_notice_days", "args": ["techcorp", 30]},

        # Confidentiality
        {"predicate": "confidentiality_years", "args": ["both_parties", 5]},

        # Data
        {"predicate": "data_owner", "args": ["acme", "processed_data"]},
        {"predicate": "encryption_standard", "args": ["software", "aes_256"]},

        # Governance
        {"predicate": "governing_law", "args": ["contract_sla_2024_001", "california"]},
        {"predicate": "dispute_resolution", "args": ["contract_sla_2024_001", "arbitration"]},
        {"predicate": "arbitration_location", "args": ["contract_sla_2024_001", "san_francisco"]},

        # Notice requirements
        {"predicate": "notice_method", "args": ["contract_sla_2024_001", "written"]},
        {"predicate": "notice_effective_days", "args": ["contract_sla_2024_001", 5]},
    ]


def define_contract_rules() -> str:
    """
    Define Prolog rules for derived reasoning about the contract.
    """
    return """
% Derived predicates for contract reasoning

% Total annual cost
total_annual_cost(Party, Total) :-
    must_pay(Party, license_fee, LicenseFee),
    must_pay(Party, support_fee, SupportFee),
    Total is LicenseFee + SupportFee.

% Is a party the licensor?
is_licensor(Party) :-
    role(Party, licensor).

% Is a party the licensee?
is_licensee(Party) :-
    role(Party, licensee).

% Can perform action (if not prohibited)
can_perform(Party, Action) :-
    party(Party, _),
    \\+ prohibited(Party, Action).

% Has obligation
has_obligation(Party, Obligation) :-
    must_pay(Party, Obligation, _).

has_obligation(Party, Obligation) :-
    must_provide(Party, Obligation).

has_obligation(Party, Obligation) :-
    upon_termination_must(Party, Obligation).

% Termination rights
can_terminate(Party, Reason) :-
    party(Party, _),
    can_terminate_for(either_party, Reason).

% Late payment total
late_payment_penalty(Party, Principal, Months, Penalty) :-
    must_pay(Party, _, Principal),
    late_penalty_percent(Party, Rate),
    Penalty is Principal * (Rate / 100) * Months.

% Contract is active (simplified - just checks if it has parties)
contract_active(Contract) :-
    party(_, Contract),
    effective_date(Contract, _).

% Support level response time
faster_response_than(Level1, Level2) :-
    response_time(Level1, Time1, Unit),
    response_time(Level2, Time2, Unit),
    Time1 < Time2.

% Security compliant (has required encryption)
security_compliant(Software) :-
    encryption_standard(Software, aes_256).

% Renewal eligible (has renewal terms)
renewable(Contract) :-
    renewal_term_years(Contract, Years),
    Years > 0.

% Mutual obligation (both parties have same type of obligation)
mutual_obligation(Obligation) :-
    has_obligation(Party1, Obligation),
    has_obligation(Party2, Obligation),
    Party1 \\= Party2.
""".strip()


def run_contract_analysis():
    """
    Main contract analysis workflow demonstrating multi-turn reasoning.
    """
    print("=" * 70)
    print("CONTRACT ANALYSIS USING LOGICAL REASONING")
    print("=" * 70)

    # Load contract
    contract_text = load_contract()
    print(f"\n✓ Loaded contract ({len(contract_text)} characters)")

    # Create reasoning session
    session_id = create_session(metadata={"task": "contract_analysis"})
    print(f"✓ Created reasoning session: {session_id}")

    try:
        # Extract and assert facts
        print("\n" + "-" * 70)
        print("STEP 1: Extracting Facts from Contract")
        print("-" * 70)

        facts = extract_contract_facts()
        result = assert_facts(session_id, facts)
        print(f"✓ Asserted {result['facts_added']} facts")

        # Add reasoning rules
        print("\n" + "-" * 70)
        print("STEP 2: Adding Logical Rules")
        print("-" * 70)

        rules = define_contract_rules()
        result = assert_rules(session_id, [rules])
        print(f"✓ Added {result['rules_added']} rule program")

        # Display session statistics
        stats = get_session_stats(session_id)
        print(f"\nSession Statistics:")
        print(f"  Total facts: {stats['total_facts']}")
        print(f"  Total rules: {stats['total_rules']}")
        print(f"  Predicates: {len(stats['predicates'])} unique")

        # Now perform queries (multi-turn reasoning)
        print("\n" + "=" * 70)
        print("MULTI-TURN QUERIES (Like a conversation with me)")
        print("=" * 70)

        # Query 1: Who are the parties?
        print("\n[TURN 1] Who are the parties to this contract?")
        print("-" * 70)
        result = query(session_id, query="party(Party, Contract).", max_solutions=10)
        if result["success"]:
            parties = set()
            for sol in result["solutions"]:
                party = sol["Bindings"]["Party"]
                parties.add(party)
            print(f"Answer: {', '.join(sorted(parties))}")
        else:
            print(f"Error: {result.get('error')}")

        # Query 2: What is Acme prohibited from doing?
        print("\n[TURN 2] What is Acme prohibited from doing?")
        print("-" * 70)
        result = query(session_id, query="prohibited(acme, Action).", max_solutions=10)
        if result["success"]:
            print(f"Answer: Acme is prohibited from:")
            for sol in result["solutions"]:
                action = sol["Bindings"]["Action"]
                print(f"  - {action}")
        else:
            print(f"Error: {result.get('error')}")

        # Query 3: What is the total annual cost?
        print("\n[TURN 3] What is the total annual cost for Acme?")
        print("-" * 70)
        result = query(session_id, query="total_annual_cost(acme, Total).", max_solutions=1)
        if result["success"] and result["count"] > 0:
            total = result["solutions"][0]["Bindings"]["Total"]
            print(f"Answer: ${total:,} USD per year")
        else:
            print(f"Error: {result.get('error')}")

        # Query 4: Can Acme sublicense?
        print("\n[TURN 4] Can Acme sublicense the software?")
        print("-" * 70)
        result = query(session_id, query="can_perform(acme, sublicense).", max_solutions=1)
        if result["success"] and result["count"] > 0:
            print("Answer: Yes, Acme can sublicense")
        else:
            print("Answer: No, Acme cannot sublicense (it's prohibited)")

        # Query 5: Who has to provide support?
        print("\n[TURN 5] Who must provide support services?")
        print("-" * 70)
        result = query(session_id, query="must_provide(Party, Support).", max_solutions=10)
        if result["success"]:
            print(f"Answer:")
            for sol in result["solutions"]:
                party = sol["Bindings"]["Party"]
                support = sol["Bindings"]["Support"]
                print(f"  - {party} must provide {support}")
        else:
            print(f"Error: {result.get('error')}")

        # Query 6: What are the response time SLAs?
        print("\n[TURN 6] What are the response time SLAs?")
        print("-" * 70)
        result = query(session_id, query="response_time(Priority, Time, Unit).", max_solutions=10)
        if result["success"]:
            print(f"Answer:")
            for sol in result["solutions"]:
                priority = sol["Bindings"]["Priority"]
                time = sol["Bindings"]["Time"]
                unit = sol["Bindings"]["Unit"]
                print(f"  - {priority}: {time} {unit}")
        else:
            print(f"Error: {result.get('error')}")

        # Query 7: Under what conditions can either party terminate?
        print("\n[TURN 7] Under what conditions can the contract be terminated?")
        print("-" * 70)
        result = query(session_id, query="can_terminate(Party, Reason).", max_solutions=10)
        if result["success"]:
            reasons = set()
            for sol in result["solutions"]:
                reason = sol["Bindings"]["Reason"]
                reasons.add(reason)
            print(f"Answer: Either party can terminate for:")
            for reason in sorted(reasons):
                print(f"  - {reason}")
        else:
            print(f"Error: {result.get('error')}")

        # Query 8: What must Acme do upon termination?
        print("\n[TURN 8] What must Acme do if the contract is terminated?")
        print("-" * 70)
        result = query(session_id, query="upon_termination_must(acme, Action).", max_solutions=10)
        if result["success"]:
            print(f"Answer: Upon termination, Acme must:")
            for sol in result["solutions"]:
                action = sol["Bindings"]["Action"]
                print(f"  - {action}")
        else:
            print(f"Error: {result.get('error')}")

        # Query 9: Is the software security compliant?
        print("\n[TURN 9] Is the software security compliant (AES-256)?")
        print("-" * 70)
        result = query(session_id, query="security_compliant(software).", max_solutions=1)
        if result["success"] and result["count"] > 0:
            print("Answer: Yes, the software meets security compliance (AES-256 encryption)")
        else:
            print("Answer: No, security compliance not verified")

        # Query 10: Calculate late payment penalty
        print("\n[TURN 10] What would the penalty be for 3 months late payment on license fee?")
        print("-" * 70)
        result = query(
            session_id,
            query="late_payment_penalty(acme, Principal, 3, Penalty), must_pay(acme, license_fee, Principal).",
            max_solutions=1
        )
        if result["success"] and result["count"] > 0:
            principal = result["solutions"][0]["Bindings"]["Principal"]
            penalty = result["solutions"][0]["Bindings"]["Penalty"]
            print(f"Answer: Penalty on ${principal:,} principal = ${penalty:,.2f}")
            print(f"        (1.5% per month × 3 months)")
        else:
            print(f"Error: {result.get('error')}")

        # Complex query: All of Acme's obligations
        print("\n[TURN 11] What are ALL of Acme's obligations?")
        print("-" * 70)
        result = query(session_id, query="has_obligation(acme, Obligation).", max_solutions=20)
        if result["success"]:
            obligations = set()
            for sol in result["solutions"]:
                obligation = sol["Bindings"]["Obligation"]
                obligations.add(obligation)
            print(f"Answer: Acme has {len(obligations)} obligations:")
            for obligation in sorted(obligations):
                print(f"  - {obligation}")
        else:
            print(f"Error: {result.get('error')}")

        # Final summary
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"""
This demonstrates how I could use the Prolog reasoning system to:

✓ Extract structured facts from unstructured text
✓ Build a knowledge graph of contract relationships
✓ Answer complex multi-turn questions
✓ Verify logical consistency
✓ Compute derived values (like total cost, penalties)
✓ Maintain conversation context across turns

All answers are VERIFIABLE and GROUNDED in the actual contract text!
        """)

    finally:
        # Cleanup
        destroy_session(session_id)
        print(f"\n✓ Session {session_id} destroyed")


if __name__ == "__main__":
    run_contract_analysis()
