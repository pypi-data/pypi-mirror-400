from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from ..tools.file_tools import read_file_tool, list_directory_tool


def create_file_reader_agent(model: LiteLlm) -> LlmAgent:
    """Create a file reader agent."""
    return LlmAgent(
        name="file_reader_agent",
        model=model,
        instruction=(
            "You are a specialized file reader agent. Your ONLY job is to execute the `read_file_tool` or `list_directory_tool`. "
            "When you receive a request, you must call the appropriate tool and return its output EXACTLY. "
            "DO NOT add any conversational filler, explanations, or labels. "
            "Your entire response MUST be just the content returned by the tool."
        ),
        tools=[read_file_tool, list_directory_tool],
        output_key="file_content",
    )
