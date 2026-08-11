from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt or task instruction")
    session_id: Optional[str] = Field(default=None, description="Active session ID")
    context: dict[str, Any] = Field(default_factory=dict, description="Contextual state data")
    artifacts: list[Any] = Field(default_factory=list, description="Associated artifacts")
    workspace: Optional[str] = Field(default=None, description="Target workspace directory")
    previous_results: dict[str, Any] = Field(default_factory=dict, description="Results from upstream agent steps")


class AgentChatResponse(BaseModel):
    success: bool = True
    service: str = Field(..., description="Name of the service that executed the task")
    status: str = Field(default="completed", description="Task execution status: completed, failed, pending, running")
    result: Any | None = Field(default=None, description="Main output result")
    error: Optional[str] = Field(default=None, description="Error code or title if execution failed")
    detail: Optional[str] = Field(default=None, description="Detailed error traceback or message")
    workspace: Optional[str] = Field(default=None, description="Workspace path used during execution")
    artifacts: list[Any] = Field(default_factory=list, description="Generated artifacts")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Execution metadata (timing, token count, etc.)")


class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy", description="Status: healthy, degraded, unhealthy")
    service: str = Field(..., description="Service identifier")
    model: Optional[str] = Field(default=None, description="Configured LLM model")
    ollama_connected: Optional[bool] = Field(default=None, description="Whether Ollama backend is reachable")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional health diagnostics")
