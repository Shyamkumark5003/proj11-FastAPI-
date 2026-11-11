import logging

from fastapi import APIRouter

from app.errors import AppError
from app.rag_service import answer_question
from app.schemas import AskRequest, AskResponse

logger = logging.getLogger("app.routes")
router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest):
    try:
        result = answer_question(body.question)
    except Exception:
        # full traceback LOG la; client ku safe 503 mattum
        logger.exception("rag failed")
        raise AppError(503, "rag_unavailable", "Answer service is temporarily unavailable")
    return AskResponse(**result)
