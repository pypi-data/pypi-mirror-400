import pytest
from agenwatch._kernel.agent import Agent
from agenwatch._kernel.execution_manager import BudgetManager
from agenwatch._kernel.tools.function_tool import FunctionTool
from test.mocks.mock_llm import MockLLM

@pytest.mark.asyncio
async def test_budget_llm_plus_tool_exact_limit():
    calls = {"count": 0}

    async def tool():
        calls["count"] += 1
        return {"ok": True}

    agent = Agent(
        llm_provider=MockLLM(always_call="tool"),
        tools=[FunctionTool(name="tool", fn=tool)],
        max_iterations=10,
    )

    agent.execution_manager.budget_manager = BudgetManager(max_budget=2)

    await agent.run("do work")

    assert calls["count"] == 2


