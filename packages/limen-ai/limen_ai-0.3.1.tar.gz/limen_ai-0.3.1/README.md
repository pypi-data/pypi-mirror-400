# LIMEN-AI (Łukasiewicz Interpretable Markov Engine for Neuralized AI)

[![PyPI version](https://img.shields.io/pypi/v/limen-ai.svg)](https://pypi.org/project/limen-ai/)
[![License](https://img.shields.io/badge/License-AGPL_3.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**LIMEN-AI** is a neurosymbolic library for building transparent, auditable AI applications. It combines Large Language Models (LLMs) with Łukasiewicz fuzzy logic and Energy-Based Models (EBM) to create systems that:

- Extract structured knowledge from unstructured text
- Perform probabilistic logical reasoning with fuzzy truth degrees
- Learn new rules inductively from examples
- Generate natural language explanations traceable to logical inference
- Support EU AI Act compliance requirements (Articles 13, 14, 15)
- Compatible with Ollama, OpenAI, Gemini, Claude, and DeepSeek

**Core Use Case**: Transform legal documents, policies, or domain texts into queryable knowledge bases with built-in explainability.

---

## 📦 Installation

```bash
pip install limen-ai
# Recommended for LLM features:
pip install requests python-dotenv
```

---

## 🚀 Quick Start (5 Lines)

```python
from limen import LimenClient

# Initialize with local Ollama
client = LimenClient(model_name="ollama/gpt-oss:20b")

# Extract and query
proposal = client.extract("TechCorp is provider. Client is GlobalRetail.")
client.add_knowledge(proposal)
answer = client.ask("Who is provider?")
print(answer.natural_language)  # "TechCorp is provider."
```

---

## 🛠️ Step-by-Step Guide: Build Your First Application

### 1. Set Up Environment Variables

Create a `.env` file in your project directory:

```ini
# Choose ONE provider (uncomment relevant section)

# Option A: Local Ollama (Free, good for development)
OLLAMA_BASE_URL=http://localhost:11434/v1

# Option B: OpenAI (Production - best quality)
OPENAI_API_KEY=sk-your-openai-key-here

# Option C: Anthropic Claude (Production - best reasoning)
ANTHROPIC_API_KEY=your-anthropic-key-here

# Option D: Google Gemini (Production - good for long docs)
GEMINI_API_KEY=your-gemini-key-here

# Option E: DeepSeek (Budget-friendly)
DEEPSEEK_API_KEY=your-deepseek-key-here
```

### 2. Install and Configure Ollama (Local LLM)

For development without API costs, use Ollama:

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull recommended model (fits in 16GB VRAM)
ollama pull gpt-oss:20b

# 3. Start Ollama server
ollama run gpt-oss:20b
```

**Recommended Ollama Models**:
- `gpt-oss:20b` - Best reasoning, JSON output (14-16GB VRAM)
- `qwen2.5:32b` - Best for reasoning (16GB VRAM)
- `qwen2.5:14b` - Good balance (8GB VRAM)

### 3. Initialize LIMEN-AI Client

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from limen import LimenClient

load_dotenv()

# Initialize client (choose your provider)
client = LimenClient(
    model_name="ollama/gpt-oss:20b",  # Local Ollama
    # model_name="openai/gpt-4o-mini",  # OpenAI
    # model_name="claude/claude-3-5-sonnet-20241022",  # Anthropic
    # model_name="gemini/gemini-1.5-pro",  # Google
    # model_name="deepseek/deepseek-chat",  # DeepSeek
    base_url=os.getenv("OLLAMA_BASE_URL"),  # For Ollama only
    enable_auto_induction=True,  # Enable rule learning
    use_neurosymbolic_ilp=True    # Use LLM-guided ILP
)
```

### 4. Extract Knowledge from Document

```python
# Load your document
contract_path = Path("your_contract.txt")
contract_text = contract_path.read_text(encoding="utf-8")

# Extract structured knowledge
proposal = client.extract(contract_text)

# Review what was extracted
print(proposal.to_markdown())
```

**Expected Output**:
```
## 1. Schema Extensions (New Predicates)
- **legalParty**(entity, role): Links entity to its legal role
- **effectiveDate**(date): Specifies effective date of agreement
- **paymentAmount**(amount, currency): Payment details

## 2. Fact Grounding (Extracted from Context)
| Predicate | Arguments | Confidence | Source |
| :--- | :--- | :--- | :--- |
| legalParty | TechCorp, Provider | 0.99 | Sentence 1 |
| legalParty | GlobalRetail, Client | 0.99 | Sentence 2 |
```

### 5. Commit Knowledge to Knowledge Base

```python
# After human verification of proposal, commit to KB
result = client.add_knowledge(proposal)

print(f"Added {len(result.facts_added)} facts to KB")
```

### 6. Query Your Knowledge Base

```python
# Natural language query
answer = client.ask("Who is the service provider?")

# Get results
print(f"Answer: {answer.natural_language}")

# Access structured inference results
for result in answer.answers:
    predicate = result['predicate']
    args = result['args']
    truth_degree = result['value']  # Fuzzy truth [0, 1]
    print(f"{predicate}({args}) = {truth_degree:.4f}")

# View logical trace (reasoning steps)
for step in answer.logical_trace:
    print(step)
```

### 7. Save and Restore Knowledge Base

```python
# Save complete state (schema, facts, formulas, rules)
client.save_state("my_knowledge_base.json")

# Later, restore without re-extracting
client2 = LimenClient(model_name="ollama/gpt-oss:20b")
client2.load_state("my_knowledge_base.json")

# Now query
answer = client2.ask("What is the monthly fee?")
```

---

## 🔧 Advanced Usage

### Direct Predicate Queries (For Local Models)

If using Ollama where natural language queries sometimes fail, query the KB directly:

```python
# After extraction and add_knowledge()

# Method 1: Iterate over all high-confidence facts
for atom, confidence in client.pipeline.assignment.values.items():
    if confidence > 0.8 and atom.predicate.name == "legalParty":
        entity = atom.arguments[0].name
        role = atom.arguments[1].name
        print(f"{entity} is {role} (confidence: {confidence:.2f})")

# Method 2: Query specific predicate
from limen.core import Atom

pred = client.pipeline.kb.get_predicate("legalParty")
provider = client.pipeline.kb.get_constant("TechCorp")
client_role = client.pipeline.kb.get_constant("Provider")
atom = Atom(pred, (provider, client_role))

truth_degree = client.pipeline.assignment.get(atom)
print(f"TechCorp is Provider: {truth_degree:.2f}")
```

**Benefits**:
- ✅ Deterministic results (no LLM query translation)
- ✅ Lower latency (no additional LLM calls)
- ✅ Reliable (works with any model quality)

### Manual Fact Addition (Fill LLM Gaps)

```python
# If LLM missed critical facts, add them manually
client.set_fact("terminationNotice", ["30 days"], 1.0)
client.set_fact("governingLaw", ["California"], 1.0)
client.set_fact("monthlyFee", [15000, "USD"], 1.0)
```

### Inductive Rule Learning

```python
# Provide labeled examples to teach the system rules
labels = {
    "legalParty": {
        "pos": [("TechCorp", "Provider"), ("GlobalRetail", "Client")],
        "neg": [("TechCorp", "Client"), ("GlobalRetail", "Provider")]
    }
}

# Trigger inductive learning
client.feedback(labels)

# Check learned rules
if client.pipeline.kb.induced_clauses:
    print("Learned rules:")
    for clause in client.pipeline.kb.induced_clauses:
        print(f"  IF {', '.join(clause.body)} THEN {clause.head} (weight: {clause.weight:.2f})")
```

### Human Oversight (Veto Power)

```python
# Override incorrect LLM extraction (Article 14(4) compliance)
client.veto("incorrectPredicate", ["arg1", "arg2"])

# This sets truth degree to 0.0 and adds a high-weight NOT formula
# Future inference will respect this override
```

---

## 🤖 LLM Provider Configuration

### Recommended Models by Use Case

| Provider | Model | Extraction | Query Translation | Best For | Cost |
|:---|:---|:---|:---:|:---|:---|
| **Ollama** | `gpt-oss:20b` | ⭐⭐⭐⭐ | ⭐⭐ | Development | Free |
| **Ollama** | `qwen2.5:32b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Best local | Free |
| **OpenAI** | `gpt-4o-mini` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Production | $$$ |
| **OpenAI** | `gpt-4o` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐⭐ | Production | $$$$ |
| **Anthropic** | `claude-3.5-sonnet` | ⭐⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐⭐ | Complex | $$$ |
| **Google** | `gemini-1.5-pro` | ⭐⭐⭐⭐ | ⭐⭐⭐ | Long docs | $$ |
| **DeepSeek** | `deepseek-chat` | ⭐⭐⭐ | ⭐⭐⭐ | Budget | $ |

**Key Observations**:
- **Ollama**: Good for development, but query translation varies between runs
- **GPT-4/Claude**: Recommended for production - high quality extraction and querying
- **Workaround for Ollama**: Use direct predicate queries instead of natural language

### Ollama Configuration

```python
client = LimenClient(
    model_name="ollama/gpt-oss:20b",
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
)
```

**Installation**:
```bash
ollama pull gpt-oss:20b  # 14-16GB VRAM
ollama run gpt-oss:20b
```

### OpenAI Configuration

```python
client = LimenClient(
    model_name="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Anthropic Claude Configuration

```python
client = LimenClient(
    model_name="claude/claude-3-5-sonnet-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### Google Gemini Configuration

```python
client = LimenClient(
    model_name="gemini/gemini-1.5-pro",
    api_key=os.getenv("GEMINI_API_KEY")
)
```

### DeepSeek Configuration

```python
client = LimenClient(
    model_name="deepseek/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)
```

---

## 📊 Understanding Results

LIMEN-AI returns a `StructuredAnswer` with multiple components:

```python
answer = client.ask("Who is the provider?")

# Natural language response (LLM-generated)
print(answer.natural_language)  # "TechCorp is the provider."

# Structured inference results (from sampling)
for result in answer.answers:
    predicate = result['predicate']
    args = result['args']
    truth_degree = result['value']  # Fuzzy truth [0, 1]
    print(f"{predicate}({args}) = {truth_degree:.4f}")

# Logical trace (reasoning steps)
for step in answer.logical_trace:
    print(step)
```

**Key Insight**: LIMEN-AI performs **probabilistic inference** using importance sampling. Truth degrees represent expected value under induced distribution, not simple lookup values.

---

## 📈 Domain-Specific Usage Patterns

### Legal Domain (Contracts, Regulations)

```python
# Extract legal entities, obligations, terms
client.extract(contract_text)

# Query for compliance, obligations, parties
answer = client.ask("What are the termination conditions?")
answer = client.ask("Who is liable for breach?")
answer = client.ask("What is the governing law?")
```

### Cybersecurity Domain (Incidents, Controls)

```python
# Extract security concepts, threats, controls
client.extract(security_policy_text)

# Query for incident response, controls, risks
answer = client.ask("What is the incident response time?")
answer = client.ask("What encryption is required?")
answer = client.ask("Which controls mitigate this threat?")
```

### Financial Domain (Risk, Compliance)

```python
# Extract risk factors, controls, metrics
client.extract(risk_framework_text)

# Query for compliance status, risk ratings, controls
answer = client.ask("What is the overall risk rating?")
answer = client.ask("Which controls are in place for AML?")
answer = client.ask("Is PCI-DSS compliance met?")
```

**Key**: LIMEN-AI works across **any domain**. Just provide domain-specific text and ask questions in that domain.

---

## ❓ Troubleshooting & FAQ

**Q: I get a `ConnectionError` when using Ollama.**
A: Ensure Ollama is running: `ollama run <model>`. Check `base_url` is correct (usually `http://localhost:11434/v1`).

**Q: Queries return "The fact is not supported" even though I see data in extraction.**
A: This is a **query translation issue**. The LLM failed to map your natural language question to the correct predicates.
- **Solution 1**: Use a better model (GPT-4, Claude) - recommended for production
- **Solution 2**: Query predicates directly instead of natural language (see "Direct Predicate Queries" section)

**Q: The extraction is missing some facts.**
A: Small local models have extraction limitations.
- **Solution 1**: Use GPT-4, Claude, or Gemini for complete extraction
- **Solution 2**: Manually add missing facts with `client.set_fact("predicate", ["arg1", "arg2"], 1.0)`

**Q: How do I save my Knowledge Base?**
A: Use `client.save_state("my_kb.json")` to save complete pipeline state:
- Schema (predicates with descriptions)
- Facts (ground truth assignments)
- Formulas (weighted rules)
- Induced clauses (learned rules)

Later, restore with `client.load_state("my_kb.json")`.

**Q: What's the difference between `save_state()` and `save_knowledge_base()`?**
A: `save_state()` (JSON) saves **everything** including facts and learned rules.
   `save_knowledge_base()` (SQLite) only saves KB structure (predicates/formulas) without facts.
   **Recommendation**: Always use `save_state()` for complete persistence.

---

## 🧪 Scientific Validation

LIMEN-AI is built on rigorous mathematical foundations:

### Łukasiewicz Logic
- T-norm: `min(a ⊕ b, 1 - a ⊖ b)`
- Implication: `a → b = 1 - a + b`
- Conjunction: `a ⊙ b = min(a, b)`

### Energy-Based Models
- Probability distribution: `P(X) = (1/Z) * exp(E(X))`
- Inference via sampling (Importance Sampling, Langevin MCMC)
- Learning via gradient-based optimization

### Neurosymbolic Integration
- LLM extracts schema and facts from natural language
- Probabilistic logic engine performs reasoning
- Inductive Logic Programming learns rules from examples

**No Experimental Data**: All examples in documentation use either:
- Hand-calculable pedagogical examples (clearly labeled as such)
- Real document processing (showing extraction and inference on actual texts)

---

## 📄 License

LIMEN-AI is licensed under the **AGPL-3.0**. See `LICENSE` file for details.

---

## 🤝 Contributing

We welcome contributions! Please see our GitHub repository.

---

**Built with 🤖 for building trustworthy AI.**
