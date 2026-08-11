from typing import Any, Optional
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[Any] = Field(default_factory=list)
    workspace: Optional[str] = None
    previous_results: dict[str, Any] = Field(default_factory=dict)
