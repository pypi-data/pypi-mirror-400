import pytest
from agenwatch._kernel.agent import Agent
from agenwatch._kernel.execution_manager import BudgetManager
from agenwatch._kernel.tools.function_tool import FunctionTool
from test.mocks.mock_llm import MockLLM

@pytest.mark.asyncio
async def test_retry_does_not_double_charge_budget():
    calls = {"count": 0}

    async def flaky():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("fail once")
        return {"ok": True}

    agent = Agent(
        llm_provider=MockLLM(always_call="flaky"),
        tools=[FunctionTool(name="flaky", fn=flaky)],
        max_iterations=5,
    )

    agent.execution_manager.budget_manager = BudgetManager(max_budget=1)

    await agent.run("do work")

    assert calls["count"] == 2


