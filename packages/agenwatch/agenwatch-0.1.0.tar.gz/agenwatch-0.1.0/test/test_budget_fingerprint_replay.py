import pytest
from agenwatch._kernel.agent import Agent
from agenwatch._kernel.execution_manager import BudgetManager
from agenwatch._kernel.tools.function_tool import FunctionTool
from test.mocks.mock_llm import MockLLM

@pytest.mark.asyncio
async def test_budget_not_mutated_in_replay():
    calls = {"count": 0}

    async def tool():
        calls["count"] += 1
        return {"ok": True}

    agent = Agent(
        llm_provider=MockLLM(always_call="tool"),
        tools=[FunctionTool(name="tool", fn=tool)],
        max_iterations=5,
    )

    agent.execution_manager.budget_manager = BudgetManager(max_budget=1)

    await agent.run("do work")
    await agent.run("do work")  # replay

    assert calls["count"] == 1


