import pytest
from unittest.mock import MagicMock, patch
from onecoder.agents.orchestrator_agent import create_orchestrator_agent
from google.adk.models.lite_llm import LiteLlm

@pytest.mark.asyncio
async def test_orchestrator_loads_agents_md(tmp_path):
    # Mock ProjectKnowledge to return specific guidelines
    with patch("onecoder.agents.orchestrator_agent.ProjectKnowledge") as MockPK:
        mock_pk_instance = MockPK.return_value
        mock_pk_instance.get_durable_context.return_value = {
            "agents_guidelines": "DO NOT HALLUCINATE"
        }

        # Use real LiteLlm with dummy values to satisfy Pydantic
        dummy_model = LiteLlm(model="gpt-4", api_key="dummy")

        agent = create_orchestrator_agent(dummy_model)

        # Check instruction contains the guidelines
        assert "GOVERNANCE & POLICY" in agent.instruction
        assert "DO NOT HALLUCINATE" in agent.instruction

@pytest.mark.asyncio
async def test_orchestrator_handles_missing_agents_md():
    with patch("onecoder.agents.orchestrator_agent.ProjectKnowledge") as MockPK:
        mock_pk_instance = MockPK.return_value
        mock_pk_instance.get_durable_context.return_value = {}

        dummy_model = LiteLlm(model="gpt-4", api_key="dummy")
        agent = create_orchestrator_agent(dummy_model)

        assert "GOVERNANCE & POLICY" not in agent.instruction
