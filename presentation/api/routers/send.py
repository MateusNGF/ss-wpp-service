from fastapi import APIRouter, Depends, HTTPException, status
from presentation.api.dependencies import verify_bot_token
from core.models.schemas import NotificationPayload
from core.exceptions.domain_exceptions import NotificationDeliveryError, InvalidNumberError
from application.use_cases.send_notification import SendNotificationUseCase
from infrastructure.whatsapp.neonize_adapter import NeonizeAdapter
from config.settings import settings

router = APIRouter(
    prefix="/send",
    tags=["notificacoes"],
    dependencies=[Depends(verify_bot_token)]
)

# O provedor (adapter) será instanciado globalmente no lifespan do app e passado para cá.
# Para manter a injeção limpa, buscaremos do state do app.
from fastapi import Request

@router.post("/", status_code=status.HTTP_200_OK)
def send_notification(payload: NotificationPayload, request: Request):
    """
    Endpoint para envio síncrono de mensagem no WhatsApp.
    O Header 'X-Bot-Token' é obrigatório.
    """
    # Recupera o adaptador instanciado no lifespan
    provider = request.app.state.whatsapp_provider
    
    use_case = SendNotificationUseCase(whatsapp_provider=provider)
    
    try:
        resultado = use_case.execute(payload)
        return resultado
    except ValueError as ve:
         # Erros do Pydantic ou validações manuais
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except InvalidNumberError as ine:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ine))
    except NotificationDeliveryError as nde:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(nde))
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no servidor.")
