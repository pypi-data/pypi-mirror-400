from typing import List

from pydantic import BaseModel, Field


MAX_TOOL_CALL = 15


class ResearchAgentConfig(BaseModel):
    topic: str = Field(..., description="Research topic or source text/URL to investigate.")
    max_tool_call: int = Field(
        15,
        ge=1,
        le=MAX_TOOL_CALL,
        description="Maximum number of tool calls allowed during research.",
    )


class ResearchAgentResponse(BaseModel):
    final_report: str = Field(..., description="Generated research report in markdown.")
    sources: List[str] = Field(default_factory=list, description="List of sources used in the report.")
    generation_time: int = Field(..., description="Total generation time in seconds.")
