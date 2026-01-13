import pytest
from agenwatch._kernel.agent import Agent
from agenwatch._kernel.execution_manager import BudgetManager
from test.mocks.mock_llm import MockLLM

@pytest.mark.asyncio
@pytest.mark.xfail(reason="LLM-only budget is not supported by kernel contract; agent will not succeed.")
async def test_budget_llm_only_stops_agent():
    agent = Agent(
        llm_provider=MockLLM(always_text="thinking"),
        tools=[],
        max_iterations=10,
    )

    agent.execution_manager.budget_manager = BudgetManager(max_budget=1)

    result = await agent.run("do work")

    assert result.success is False



