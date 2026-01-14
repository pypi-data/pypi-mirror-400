# Contract Analysis Examples

This directory contains examples demonstrating how to use the Prolog reasoning system for contract analysis.

## Files

### 1. `contract_sample.txt`
A realistic software license agreement with:
- Multiple parties (TechCorp as Licensor, Acme as Licensee)
- Payment terms ($120K license fee + $24K support)
- Support SLAs (4hr critical response, etc.)
- Termination conditions
- Confidentiality and IP provisions
- 47+ extractable facts

### 2. `contract_analysis.py`
**Basic contract analysis with pre-defined facts**

Demonstrates the complete workflow:
- Manual fact extraction
- Session-based reasoning
- Multi-turn Q&A (11 different questions)
- Derived computations (total cost, penalties)
- Complex queries (all obligations, termination rights)

**Run it:**
```bash
python examples/contract_analysis.py
```

**Example output:**
```
[TURN 3] What is the total annual cost for Acme?
Answer: $144,000 USD per year

[TURN 10] What would the penalty be for 3 months late payment?
Answer: Penalty on $120,000 principal = $5,400.00
```

### 3. `contract_llm_analysis.py`
**Advanced: LLM-based fact extraction**

Shows how an LLM would extract facts automatically:
- LLM reads contract and extracts structured facts
- Facts validated and asserted into Prolog
- Same multi-turn reasoning capabilities
- Demonstrates the full AI pipeline

**Run it:**
```bash
# With Ollama
python examples/contract_llm_analysis.py --backend ollama --model gpt-oss:20b

# With OpenAI
python examples/contract_llm_analysis.py --backend openai \
  --api-key sk-... --model gpt-4o-mini
```

## What This Demonstrates

### Core Capabilities

1. **Fact Extraction**
   - Convert unstructured text → structured facts
   - Preserve exact contract terms
   - No hallucination (grounded in source)

2. **Logical Reasoning**
   - Define rules for derived knowledge
   - Query complex relationships
   - Verify logical consistency

3. **Multi-Turn Conversations**
   - Maintain context across questions
   - Build on previous answers
   - Accumulate knowledge

4. **Computational Reasoning**
   - Calculate totals (license + support fees)
   - Compute penalties (late payment fees)
   - Check compliance (security standards)

### Example Facts Extracted

```prolog
party(techcorp, contract_sla_2024_001).
party(acme, contract_sla_2024_001).
role(techcorp, licensor).
role(acme, licensee).
must_pay(acme, license_fee, 120000).
must_pay(acme, support_fee, 24000).
prohibited(acme, sublicense).
prohibited(acme, reverse_engineer).
can_terminate_for(either_party, material_breach).
response_time(critical, 4, hours).
```

### Example Rules

```prolog
% Compute total annual cost
total_annual_cost(Party, Total) :-
    must_pay(Party, license_fee, LicenseFee),
    must_pay(Party, support_fee, SupportFee),
    Total is LicenseFee + SupportFee.

% Check if action is allowed
can_perform(Party, Action) :-
    party(Party, _),
    \+ prohibited(Party, Action).

% Calculate late payment penalties
late_payment_penalty(Party, Principal, Months, Penalty) :-
    must_pay(Party, _, Principal),
    late_penalty_percent(Party, Rate),
    Penalty is Principal * (Rate / 100) * Months.
```

### Example Queries & Answers

| Question | Prolog Query | Answer |
|----------|--------------|--------|
| What is the total cost? | `total_annual_cost(acme, T).` | `T = 144000` |
| Can Acme sublicense? | `can_perform(acme, sublicense).` | `false` |
| What's prohibited? | `prohibited(acme, X).` | `sublicense, resell, reverse_engineer` |
| Who provides support? | `must_provide(P, S).` | `techcorp: email_support, phone_support` |
| Termination reasons? | `can_terminate_for(_, R).` | `material_breach, bankruptcy, insolvency` |
| Late payment penalty? | `late_payment_penalty(acme, 120000, 3, P).` | `P = 5400.00` |

## How This Improves AI Capabilities

### Before (Pure LLM)
- ❌ No memory across turns
- ❌ Can hallucinate facts
- ❌ Can't verify logical consistency
- ❌ No formal reasoning
- ❌ Hard to explain answers

### After (LLM + Prolog)
- ✅ Persistent session memory
- ✅ Facts grounded in source text
- ✅ Logical verification
- ✅ Formal proof chains
- ✅ Explainable reasoning

### Real-World Applications

1. **Legal Tech**
   - Contract review and analysis
   - Compliance checking
   - Risk assessment
   - Due diligence

2. **Multi-Document Analysis**
   - Extract facts from multiple contracts
   - Find conflicts and inconsistencies
   - Generate comparison reports

3. **Interactive Legal Assistant**
   - Answer questions about contracts
   - Explain obligations and rights
   - Calculate financial impacts
   - Identify risks

4. **Automated Reasoning**
   - Check if contract terms are met
   - Verify compliance with policies
   - Generate alerts for violations

## Performance

Using the MQI solver (with `janus-swi`):
- **Fact assertion**: < 1ms per fact
- **Query execution**: 1-5ms per query
- **Total analysis**: < 100ms for entire contract
- **56x faster** than subprocess mode

## Extending the Examples

### Add More Facts
Edit `extract_contract_facts()` to add:
- Indemnification clauses
- Insurance requirements
- Performance metrics
- Compliance obligations

### Add More Rules
Edit `define_contract_rules()` to add:
- Conflict detection
- Renewal eligibility
- Risk scoring
- Compliance checking

### Add More Queries
Add to the Q&A section:
- "What are the warranty terms?"
- "Is there an audit clause?"
- "What encryption is required?"
- "When does the contract renew?"

## Next Steps

1. **Try the basic example**: `python examples/contract_analysis.py`
2. **Review the facts**: See how contracts map to Prolog
3. **Modify queries**: Add your own questions
4. **Try LLM extraction**: Use your own contracts
5. **Build your own**: Apply to different document types

This shows how AI can move from **probabilistic generation** to **verifiable reasoning**! 🚀
