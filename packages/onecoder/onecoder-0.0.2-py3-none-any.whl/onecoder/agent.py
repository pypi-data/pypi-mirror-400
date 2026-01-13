import os
from google.adk.agents import LlmAgent
from google.adk.models import Gemini, LiteLlm
from dotenv import load_dotenv

from .agents import (
    create_documentation_agent,
    create_orchestrator_agent,
    create_refactoring_agent,
    create_file_reader_agent,
    create_file_writer_agent,
    create_research_agent
)
from .config_manager import config_manager

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# --- LLM Configuration ---
def get_model():
    # 1. Check user configuration via config_manager
    model_config = config_manager.get_model_config()
    if model_config and model_config.get("model_name"):
        return LiteLlm(
            model=model_config.get("model_name"),
            api_key=model_config.get("api_key"),
            base_url=model_config.get("base_url"),
        )

    # 2. Priority: Gemini (Default)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        return Gemini(
            model="gemini-2.0-flash-exp",
            api_key=gemini_api_key
        )

    # 3. Priority: OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return LiteLlm(
            model="openai/gpt-4o",
            api_key=openai_api_key
        )

    # 4. Check for OLLAMA_API_KEY (Defaulting to qwen coder)
    ollama_api_key = os.getenv("OLLAMA_API_KEY")
    if ollama_api_key:
        base_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.com")
        return LiteLlm(
            model="ollama/qwen3-coder:480b-cloud",
            api_key=ollama_api_key,
            base_url=base_url,
        )

    # 5. Fallback to OpenRouter
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        return LiteLlm(
            model="openrouter/xiaomi/mimo-v2-flash:free",
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    
    raise ValueError(
        "No API key found. Please set GEMINI_API_KEY, OPENAI_API_KEY, OLLAMA_API_KEY, or OPENROUTER_API_KEY, "
        "or configure the model using 'onecoder config model'."
    )

# --- Agent Instances ---
_root_agent = None

def get_root_agent():
    global _root_agent
    if _root_agent is None:
        model = get_model()
        
        # Create specialist agents
        refactoring_agent = create_refactoring_agent(model)
        documentation_agent = create_documentation_agent(model)
        file_reader_agent = create_file_reader_agent(model)
        file_writer_agent = create_file_writer_agent(model)
        research_agent = create_research_agent(model)

        # Create the orchestrator as root_agent
        _root_agent = create_orchestrator_agent(
            model,
            sub_agents=[
                refactoring_agent,
                documentation_agent,
                file_reader_agent,
                file_writer_agent,
                research_agent
            ]
        )
    return _root_agent
