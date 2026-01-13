from typing import List, Optional
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.models.lite_llm import LiteLlm
from ..tools import registry
from ..knowledge import ProjectKnowledge

def create_orchestrator_agent(model: LiteLlm, sub_agents: Optional[List[BaseAgent]] = None) -> LlmAgent:
    """Create an orchestrator agent that routes to specialist agents or uses tools."""

    # Get available tools from registry for the prompt
    tool_descriptions = registry.get_tool_descriptions()

    # Load Project Knowledge (Governance & Context)
    pk = ProjectKnowledge()
    durable_context = pk.get_durable_context()
    agents_guidelines = durable_context.get("agents_guidelines", "")

    governance_section = ""
    if agents_guidelines:
        governance_section = f"\n\nGOVERNANCE & POLICY (Must Follow):\n{agents_guidelines}\n"

    return LlmAgent(
        name="orchestrator_agent",
        model=model,
        sub_agents=sub_agents or [],
        instruction=(
            "You are the OneCoder Orchestrator, a high-level coordination agent for a multi-agent coding system.\n"
            f"{governance_section}\n"
            "YOUR MISSION:\n"
            "Analyze user requests and either solve them directly using your available tools or DELEGATE to a specialist sub-agent.\n\n"
            "SPECIALIST SUB-AGENTS:\n"
            "- 'refactoring_specialist': Code improvements, optimizations, and modernizing legacy code.\n"
            "- 'documentation_specialist': Writing docstrings, READMEs, and technical documentation.\n"
            "- 'file_reader_agent': Essential for exploring the codebase and reading file contents.\n"
            "- 'file_writer_agent': Used to apply changes or create new files.\n"
            "- 'research_agent': Optimized for broad codebase research, indexing, and structural analysis.\n\n"
            "EXTERNAL CAPABILITIES:\n"
            "- 'shell_executor': Can run any shell command. Use this for system queries or if a tool is missing.\n"
            "- 'gemini_ask': Use this to query the Gemini CLI for assistance.\n"
            "- **IMAGE GENERATION**: Image generation with 'nanobanana' requires the interactive Gemini TUI. If the user asks for images, instruct them to 'run gemini' in their terminal.\n\n"
            "AVAILABLE TOOLS:\n"
            f"{tool_descriptions}\n\n"
            "STRATEGY:\n"
            "1. **Analyze**: Understand if the task is deep research, focused refactoring, or simple file manipulation.\n"
            "2. **Delegate**: If a specialist exists for the task, call that sub-agent.\n"
            "3. **Synthesize**: When a sub-agent returns, summarize the findings and present them clearly to the user.\n\n"
            "RESPONSE STYLE:\n"
            "Maintain a helpful, professional engineer tone. Use markdown for code blocks and reports."
        ),
        output_key="final_response",
    )
