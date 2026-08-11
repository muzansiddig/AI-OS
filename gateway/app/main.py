from fastapi import FastAPI
from app.artifacts.manager import artifacts
from app.memory.session import memory
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.services.client import client
from app.services.registry import service_registry
from app.supervisor.supervisor import supervisor
from app.workspace import WORKSPACE

app = FastAPI(
    title="AI-OS Gateway",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "gateway",
    }


@app.get("/services")
def list_services():
    services_info = {}
    for name, config in service_registry.services.items():
        services_info[name] = {
            "name": config.name,
            "port": config.port,
            "url": config.url,
            "workspace": config.workspace,
            "capabilities": config.capabilities,
            "description": config.description,
        }
    return {
        "services": services_info,
    }


@app.get("/services/health")
async def services_health():
    health_results = {}
    for name, config in service_registry.services.items():
        res = await client.check_health(config.url)
        health_results[name] = res
    return {
        "services_health": health_results,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await supervisor.execute(
        prompt=request.prompt,
        session_id=request.session_id,
        request_context=request.context,
    )
    return result


@app.get("/memory")
def get_memory():
    return memory.history()


@app.delete("/memory")
def clear_memory():
    memory.clear()
    return {
        "success": True,
        "message": "Memory cleared",
    }


@app.get("/workspace")
def workspace():
    return {
        "workspace": str(WORKSPACE),
    }


@app.get("/artifacts")
def get_artifacts():
    return {
        "artifacts": artifacts.all(),
    }
