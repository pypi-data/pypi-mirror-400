import pytest

from test.mocks.mock_llm import MockLLM
from agenwatch._kernel.agent import Agent
from agenwatch._kernel.execution_manager import BudgetManager
from agenwatch._kernel.tools.function_tool import FunctionTool


@pytest.mark.asyncio
async def test_budget_hard_stop_real_execution():
    calls = {"count": 0}

    async def costly():
        calls["count"] += 1
        return {"ok": True}

    agent = Agent(
        llm_provider=MockLLM(always_call="costly"),
        tools=[FunctionTool(name="costly", fn=costly)],
        max_iterations=10,
    )

    agent.execution_manager.budget_manager = BudgetManager(max_budget=2)

    result = await agent.run("do work")

    assert calls["count"] == 2
    assert result.success is False
    # Accept either error_type or terminal_reason for budget stop
    error_str = (result.error_type or "") + " " + (result.terminal_reason or "")
    assert "budget" in error_str.lower()


