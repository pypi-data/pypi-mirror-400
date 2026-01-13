from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from ..tools.file_tools import write_file_tool


def create_file_writer_agent(model: LiteLlm) -> LlmAgent:
    """Create a file writer agent."""
    return LlmAgent(
        name="file_writer_agent",
        model=model,
        instruction=(
            "You are a specialized file writer agent. Your ONLY job is to execute the `write_file_tool`. "
            "When you receive a request, you must call the tool and return its output EXACTLY. "
            "DO NOT add any conversational filler, explanations, or confirmation messages. "
            "Your entire response MUST be just the string returned by the tool."
        ),
        tools=[write_file_tool],
        output_key="write_status",
    )
