from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


def create_refactoring_agent(model: LiteLlm) -> LlmAgent:
    """Create a refactoring agent."""
    return LlmAgent(
        name="refactoring_agent",
        model=model,
        instruction="You are an expert software engineer. Your task is to refactor the given code to improve its readability, performance, and maintainability.",
        output_key="refactored_code",
    )
