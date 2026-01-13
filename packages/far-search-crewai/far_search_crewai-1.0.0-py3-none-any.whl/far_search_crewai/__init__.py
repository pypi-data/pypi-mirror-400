"""
FAR Search CrewAI Integration - Federal Acquisition Regulations search for CrewAI.

Provides a CrewAI tool for multi-agent FAR search workflows.
"""

from far_search_crewai.tool import FARSearchTool, create_far_search_tool

__version__ = "1.0.0"
__all__ = ["FARSearchTool", "create_far_search_tool"]

