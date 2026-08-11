from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.schemas import PromptRequest
from app.adapter import adapter
from app import config

app = FastAPI(
    title="Open Interpreter Service",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "service": "open_interpreter",
            "error": "internal_server_error",
            "message": str(exc),
        },
    )


@app.get("/")
def root():
    return {
        "service": "open_interpreter",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "open_interpreter",
        "model": getattr(config, "MODEL_NAME", "ollama/qwen3:8b"),
        "ollama_base_url": getattr(config, "OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
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
