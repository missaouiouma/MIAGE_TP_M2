from fastapi import APIRouter, HTTPException
from models.chat import ChatRequestTP1, ChatRequestTP2, ChatRequestWithContext, ChatResponse, SummaryResponse
from services.llm_service import LLMService
from typing import Dict, List

router = APIRouter()
llm_service = LLMService()

@router.post("/chat/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequestTP1) -> ChatResponse:
    try:
        response = await llm_service.generate_response(request.message, session_id="default_session")
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/with-context", response_model=ChatResponse)
async def chat_with_context(request: ChatRequestWithContext) -> ChatResponse:
    try:
        response = await llm_service.generate_response(
            message=request.message,
            session_id="default_session",
            context=request.context
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequestTP2) -> ChatResponse:
    try:
        response = await llm_service.generate_response(
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[str])
async def get_all_sessions() -> List[str]:
    try:
        sessions = await llm_service.mongo_service.get_all_sessions()
        if not sessions:
            raise HTTPException(status_code=404, detail="Aucune session trouvée.")
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=List[Dict[str, str]])
async def get_history(session_id: str) -> List[Dict[str, str]]:
    try:
        history = await llm_service.get_conversation_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Aucun historique trouvé pour cette session.")
        for msg in history:
            if "timestamp" in msg:
                msg["timestamp"] = msg["timestamp"].isoformat()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{session_id}", response_model=SummaryResponse)
async def get_summary(session_id: str) -> SummaryResponse:
    try:
        summary_text = await llm_service.summarize_conversation(session_id)
        return SummaryResponse(
            full_summary=summary_text,
            bullet_points=[], 
            one_liner="Résumé rapide : " + summary_text[:50]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
