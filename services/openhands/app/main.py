from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.schemas import PromptRequest
from app.adapter import adapter

app = FastAPI(
    title="OpenHands Service",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "service": "openhands",
            "error": "internal_server_error",
            "message": str(exc),
        },
    )


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "openhands",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "openhands",
        "model": adapter.model,
        "ollama_base_url": adapter.ollama_base_url,
    }


@app.post("/chat")
def chat(request: PromptRequest):
    return adapter.chat(
        prompt=request.prompt,
        context=request.context,
        artifacts=request.artifacts,
        workspace=request.workspace,
        previous_results=request.previous_results,
    )
