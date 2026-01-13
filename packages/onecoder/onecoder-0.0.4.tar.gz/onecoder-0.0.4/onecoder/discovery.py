import importlib
import pkgutil
import inspect
import logging
import os
from pathlib import Path
from typing import List, Any
from .tools.interface import BaseTool
from .tools.registry import registry

logger = logging.getLogger(__name__)

class DiscoveryAgent:
    """
    DiscoveryAgent scans directories and modules to dynamically register tools.
    """

    def __init__(self, tools_package: str = "onecoder.tools"):
        self.tools_package = tools_package

    def discover_and_register(self):
        """
        Scans the tools package and register functions.
        Also scans paths in ONECODER_TOOLS_PATH environment variable.
        """
        logger.info(f"Starting tool discovery in {self.tools_package}")
        
        # 1. Discover internal tools
        try:
            package = importlib.import_module(self.tools_package)
            for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                if is_pkg:
                    continue
                try:
                    module = importlib.import_module(module_name)
                    self._scan_module(module)
                except Exception as e:
                    logger.error(f"Error scanning module {module_name}: {e}")
        except ImportError as e:
            logger.error(f"Could not import tools package {self.tools_package}: {e}")

        # 2. Discover external tools from ONECODER_TOOLS_PATH
        tools_path = os.environ.get("ONECODER_TOOLS_PATH")
        if tools_path:
            for path in tools_path.split(os.pathsep):
                if not path:
                    continue
                p = Path(path).absolute()
                if not p.exists():
                    logger.warning(f"External tools path does not exist: {p}")
                    continue
                
                logger.info(f"Scanning external tools path: {p}")
                self._scan_directory(p)

    def _scan_directory(self, directory: Path):
        """Scans a directory for .py files and imports them."""
        import sys
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
            
        for file in directory.glob("*.py"):
            if file.name.startswith("__"):
                continue
            
            module_name = file.stem
            try:
                # Use a unique namespace for external tools if needed, 
                # but simple import works for discovery
                module = importlib.import_module(module_name)
                self._scan_module(module)
            except Exception as e:
                logger.error(f"Error loading external tool module {module_name}: {e}")

    def _scan_module(self, module: Any):
        """Scans a module for functions ending in '_tool'."""
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and (name.endswith("_tool") or hasattr(obj, "_is_agentic_tool")):
                # Avoid registering if already exists
                tool_name = getattr(obj, "_tool_name", name.replace("_tool", ""))
                if registry.get_tool(tool_name):
                    continue
                
                # Extract metadata from docstring
                doc = inspect.getdoc(obj) or "No description provided."
                
                logger.debug(f"Discovered tool: {tool_name} in {module.__name__}")
                
                tool = BaseTool(
                    name=tool_name,
                    description=doc,
                    func=obj
                )
                registry.register(tool)

if __name__ == "__main__":
    # Test discovery
    logging.basicConfig(level=logging.DEBUG)
    disco = DiscoveryAgent("onecoder.tools")
    disco.discover_and_register()
    print(f"Registered tools: {[t.name for t in registry.list_tools()]}")
