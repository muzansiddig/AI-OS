from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.supervisor.supervisor import supervisor

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # استخدام الـ supervisor بدلاً من client.chat المباشر
        result = await supervisor.execute(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
