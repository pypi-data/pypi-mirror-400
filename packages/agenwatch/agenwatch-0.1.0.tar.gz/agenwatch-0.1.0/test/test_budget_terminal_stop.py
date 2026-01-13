import pytest
from agenwatch._kernel.agent import Agent
from agenwatch._kernel.execution_manager import BudgetManager
from agenwatch._kernel.tools.function_tool import FunctionTool
from test.mocks.mock_llm import MockLLM

@pytest.mark.asyncio
async def test_budget_stop_is_terminal():
    calls = {"count": 0}

    async def costly():
        calls["count"] += 1
        return {"ok": True}

    agent = Agent(
        llm_provider=MockLLM(always_call="costly"),
        tools=[FunctionTool(name="costly", fn=costly)],
        max_iterations=10,
    )

    agent.execution_manager.budget_manager = BudgetManager(max_budget=1)

    result = await agent.run("do work")

    assert calls["count"] == 1
    assert result.success is False


