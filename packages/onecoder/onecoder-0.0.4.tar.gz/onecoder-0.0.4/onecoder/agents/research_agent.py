# onecoder/agents/research_agent.py

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from ..tools.executor import executor

def create_research_agent(model: LiteLlm) -> LlmAgent:
    """
    Create a research agent that uses the 'Agentic Search' pattern.
    It can dynamically discover and use tools to analyze the repository.
    """
    
    async def agentic_search(task_description: str) -> str:
        """
        Dynamically find and execute the best tool for the repository research task.
        """
        result = await executor.find_and_execute_tool(task_description)
        return str(result)

    return LlmAgent(
        name="research_agent",
        model=model,
        instruction=(
            "You are a repository research specialist. Your goal is to provide deep analysis of the codebase. "
            "You have access to a powerful 'agentic_search' tool that can find and execute various repository tools (like indexing, symbols, file tree). "
            "When asked to analyze, index, or search the repository, use 'agentic_search' with a descriptive task. "
            "Your response should synthesize the information you find into a clear report."
        ),
        tools=[agentic_search],
        output_key="research_report",
    )
