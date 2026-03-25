from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from ai.orchestrator import process_query, get_context_data
from ai.llm_client import stream_response


class ChatMessage(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = []


router = APIRouter(prefix="/api", tags=["query"])


@router.post("/ai/query")
async def ai_query(request: QueryRequest):
    """Non-streaming AI query endpoint"""
    history = [m.model_dump() for m in request.history] if request.history else []
    response = await process_query(request.question, history)
    return {"response": response}


@router.post("/ai/stream")
async def ai_stream(request: QueryRequest):
    """Streaming AI query endpoint using Server-Sent Events"""
    history = [m.model_dump() for m in request.history] if request.history else []
    data = get_context_data(request.question)

    def generate():
        for token in stream_response(str(data), request.question, history):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
