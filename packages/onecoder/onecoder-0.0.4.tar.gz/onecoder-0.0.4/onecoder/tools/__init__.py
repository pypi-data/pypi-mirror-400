from .registry import registry
from .interface import BaseTool

# Dynamic Discovery
def _initialize_tools():
    from ..discovery import DiscoveryAgent
    disco = DiscoveryAgent("onecoder.tools")
    disco.discover_and_register()

_initialize_tools()
