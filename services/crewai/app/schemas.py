from pydantic import BaseModel, Field
from typing import Any

class PromptRequest(BaseModel):
    prompt: str
    context: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[Any] = Field(default_factory=list)
    workspace: str | None = None
    previous_results: dict[str, Any] = Field(default_factory=dict)
