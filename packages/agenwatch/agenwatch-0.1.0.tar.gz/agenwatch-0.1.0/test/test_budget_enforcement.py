import pytest
from agenwatch._kernel.agent import Agent
from agenwatch._kernel.execution_manager import BudgetManager

class MockLLM:
    def __init__(self):
        self.calls = 0

    async def generate(self, messages, tools=None):
        self.calls += 1

        # First two iterations: call tool
        if self.calls <= 3:
            return {
                "text": '<function="costly">{}</function>',
                "instrumentation": {}
            }

        # Then stop
        return {
            "text": "<final>done</final>",
            "instrumentation": {}
        }


