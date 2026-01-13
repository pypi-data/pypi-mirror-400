from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


def create_documentation_agent(model: LiteLlm) -> LlmAgent:
    """Create a documentation agent."""
    return LlmAgent(
        name="documentation_agent",
        model=model,
        instruction="You are an expert technical writer. Your task is to write clear and concise documentation for the given code.",
        output_key="documentation",
    )
