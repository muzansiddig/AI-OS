from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.schemas import PromptRequest
from app.adapter import adapter
from app import config

app = FastAPI(
    title="AutoGPT Service",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "service": "autogpt",
            "error": "internal_server_error",
            "message": str(exc),
        },
    )


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "autogpt",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "autogpt",
        "model": config.MODEL_NAME,
        "ollama_base_url": config.OLLAMA_BASE_URL,
    }


@app.post("/chat")
async def chat(request: PromptRequest):
    return await adapter.chat(
        prompt=request.prompt,
        context=request.context,
        artifacts=request.artifacts,
        workspace=request.workspace,
        previous_results=request.previous_results,
    )
