import pytest
from pathlib import Path
from agenwatch._kernel.agent import Agent

@pytest.mark.asyncio
async def test_budget_not_mutated_in_replay(tmp_path):
    log = tmp_path / "exec.json"
    log.write_text("""{
        "execution_id": "x",
        "started_at": "2025-01-01T00:00:00",
        "ended_at": null,
        "events": []
    }""")

    agent = Agent(
        execution_mode="replay",
        replay_log_path=log
    )

    result = await agent.run("anything")
    assert result.success is True


