from fastapi import APIRouter
from app.api.models import MessageRequest, MessageResponse
from app.api.services import process_message

router = APIRouter(prefix="/api", tags=["Endpoints"])

@router.post("/procesar", response_model=MessageResponse)
def procesar_dato(request: MessageRequest):
    result = process_message(request.text)
    return MessageResponse(response=result)
