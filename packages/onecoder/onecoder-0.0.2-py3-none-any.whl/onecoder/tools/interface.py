# onecoder/tools/interface.py

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

class BaseTool(BaseModel):
    """Base class for all tools in the system."""
    name: str
    description: str
    func: Callable
    parameters: Optional[Dict[str, Any]] = None

    def execute(self, **kwargs) -> Any:
        """Execute the tool function with the given arguments."""
        return self.func(**kwargs)

    async def execute_async(self, **kwargs) -> Any:
        """Execute the tool function asynchronously if it is a coroutine."""
        from ..metrics import TTUMetrics
        TTUMetrics.get_instance().track_first_tool_call()
        
        import asyncio
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        return self.func(**kwargs)
