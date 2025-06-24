"""
File: src/tools/__init__.py
Purpose: Tool registry implementing the "Control Plane as a Tool" pattern for centralized tool management
Functionality: Provides unified interface for tool discovery, execution, and management with proper error handling
Update Trigger: When new tools are added, tool interfaces change, or execution policies are modified
Last Modified: 2024-06-24
"""
import time
from typing import Any, Dict, List, Optional

from ..models import ToolResult, ToolSchema
from .web_search import WebSearchTool
from .pdf_parser import PDFParserTool
from .data_analyzer import DataAnalyzerTool

class ToolRegistry:
    """
    Central registry implementing the Control Plane as a Tool pattern.
    Decouples agent reasoning from tool implementation details.
    """
    
    def __init__(self):
        self._tools: Dict[str, Any] = {}
        self._initialize_tools()
        print(f"ToolRegistry initialized with {len(self._tools)} tools: {list(self._tools.keys())}")
    
    def _initialize_tools(self) -> None:
        """Initialize and register all available tools."""
        try:
            self._tools = {
                "web_search": WebSearchTool(),
                "pdf_parser": PDFParserTool(),
                "data_analyzer": DataAnalyzerTool(),
            }
        except Exception as e:
            print(f"Warning: Error initializing some tools: {e}")
            # Initialize with minimal set of tools that work
            self._tools = {}
    
    def get_tool_schemas(self) -> List[ToolSchema]:
        """Return schemas for all available tools."""
        schemas = []
        for tool_name, tool in self._tools.items():
            if hasattr(tool, "get_schema"):
                schemas.append(tool.get_schema())
            else:
                # Fallback schema for tools without explicit schema
                schemas.append(ToolSchema(
                    name=tool_name,
                    description=f"Tool: {tool_name}",
                    parameters={},
                    required_parameters=[]
                ))
        return schemas
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tools.keys())
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is available."""
        return tool_name in self._tools
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool with the given parameters.
        This is the central control plane for all tool executions.
        """
        start_time = time.time()
        
        # Validate tool exists
        if not self.has_tool(tool_name):
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result="",
                error_message=f"Tool '{tool_name}' not found. Available tools: {self.get_tool_names()}",
                execution_time=0.0
            )
        
        try:
            # Get tool instance
            tool = self._tools[tool_name]
            
            # Execute tool with input validation and policy checks
            result = self._execute_with_safety(tool, **kwargs)
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                tool_name=tool_name,
                success=True,
                result=result,
                error_message=None,
                execution_time=execution_time,
                metadata={"input_params": kwargs}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing {tool_name}: {str(e)}"
            print(f"Tool execution error: {error_msg}")
            
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result="",
                error_message=error_msg,
                execution_time=execution_time,
                metadata={"input_params": kwargs, "error_type": type(e).__name__}
            )
    
    def _execute_with_safety(self, tool: Any, **kwargs) -> Any:
        """
        Execute tool with safety checks and validation.
        In production, this would include policy enforcement, rate limiting, etc.
        """
        # Input validation
        if hasattr(tool, "validate_input"):
            tool.validate_input(**kwargs)
        
        # Execute the tool
        if hasattr(tool, "execute"):
            return tool.execute(**kwargs)
        elif hasattr(tool, "run"):
            return tool.run(**kwargs)
        else:
            # Fallback for simple callable tools
            return tool(**kwargs)
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool."""
        if not self.has_tool(tool_name):
            return None
        
        tool = self._tools[tool_name]
        info = {
            "name": tool_name,
            "type": type(tool).__name__,
            "available": True
        }
        
        # Add schema if available
        if hasattr(tool, "get_schema"):
            info["schema"] = tool.get_schema().dict()
        
        # Add description if available
        if hasattr(tool, "description"):
            info["description"] = tool.description
        
        return info
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools with their information."""
        return {
            tool_name: self.get_tool_info(tool_name)
            for tool_name in self.get_tool_names()
        }
    
    def register_tool(self, name: str, tool: Any) -> None:
        """Register a new tool with the registry."""
        self._tools[name] = tool
        print(f"Registered new tool: {name}")
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            print(f"Unregistered tool: {name}")
            return True
        return False

# Global tool registry instance
tool_registry = ToolRegistry()
