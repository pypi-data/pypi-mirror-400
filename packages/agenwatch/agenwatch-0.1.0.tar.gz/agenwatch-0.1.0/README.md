# AgenWatch

**Deterministic agent execution with runtime-enforced guardrails.**

AgenWatch is a production-grade Python SDK for running LLM agents
with **hard execution limits**, **budget enforcement**, and
**deterministic replay** — enforced during execution, not observed after.

---

## Install

```bash
pip install agenwatch
```

With provider support:
```bash
pip install agenwatch[openai]     # OpenAI
pip install agenwatch[anthropic]  # Anthropic
pip install agenwatch[groq]       # Groq
pip install agenwatch[litellm]    # 100+ providers (Gemini, Mistral, etc.)
pip install agenwatch[all]        # All providers
```

---

## Quick Example

```python
from agenwatch import Agent, tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

agent = Agent(
    name="calculator",
    model="gpt-4o-mini",
    tools=[add],
    budget=1.0,
)

result = agent.run("Add 2 and 3")

print(result.output)
print(result.cost)
```

---

## Why AgenWatch

- **Runtime-enforced budgets** — kernel-level kill switches, not just logging
- **No double-charging on retries** — fingerprint-based deduplication
- **Deterministic execution** — replayable agent runs
- **Provider agnostic** — OpenAI, Anthropic, Groq, Gemini, and 100+ via LiteLLM

---

## Status

**v0.1.0 — stable core**

---

## License

MIT
