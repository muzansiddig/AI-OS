from typing import Any
from pydantic import BaseModel, Field


class ServiceResult(BaseModel):
    success: bool
    status_code: int | None = None
    data: Any | None = None
    error: str | None = None
    message: str | None = None
    url: str | None = None


class ChatResponse(BaseModel):
    prompt: str
    intent: str | None = Field(default="general_task", description="Classified intent category")
    plan: list[str]
    results: dict[str, ServiceResult]
    context: dict[str, Any]
    artifacts: list[str]
