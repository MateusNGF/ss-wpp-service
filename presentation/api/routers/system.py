from fastapi import APIRouter, Depends, HTTPException, status, Request
from presentation.api.dependencies import verify_bot_token
from core.models.schemas import PairingPayload
from application.use_cases.get_status import GetConnectionStatusUseCase
from application.use_cases.request_pairing import RequestPairingUseCase
from application.use_cases.get_qrcode import GetQRCodeUseCase
from core.exceptions.domain_exceptions import NotificationDeliveryError

router = APIRouter(
    tags=["sistema"],
    dependencies=[Depends(verify_bot_token)]
)

@router.get("/status", status_code=status.HTTP_200_OK)
def get_system_status(request: Request):
    """
    Retorna o status atual da conexão com o WhatsApp.
    """
    provider = request.app.state.whatsapp_provider
    use_case = GetConnectionStatusUseCase(whatsapp_provider=provider)
    
    return use_case.execute()

@router.get("/qrcode", status_code=status.HTTP_200_OK)
def get_qr_code(request: Request):
    """
    Retorna a string bruta e imagem base64 do QR code gerado.
    """
    provider = request.app.state.whatsapp_provider
    use_case = GetQRCodeUseCase(whatsapp_provider=provider)
    
    return use_case.execute()


@router.post("/pair", status_code=status.HTTP_200_OK)
def request_pairing(payload: PairingPayload, request: Request):
    """
    Solicita um código de pareamento para o número fornecido.
    """
    provider = request.app.state.whatsapp_provider
    use_case = RequestPairingUseCase(whatsapp_provider=provider)
    
    try:
        resultado = use_case.execute(payload)
        return resultado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except NotificationDeliveryError as nde:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(nde))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no servidor.")
