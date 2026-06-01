import logging
from core.interfaces.whatsapp_provider import IWhatsAppProvider
from core.models.schemas import PairingPayload
from core.exceptions.domain_exceptions import NotificationDeliveryError

logger = logging.getLogger(__name__)

class RequestPairingUseCase:
    """
    Caso de Uso: Solicitar Código de Pareamento (Pairing Code).
    """
    def __init__(self, whatsapp_provider: IWhatsAppProvider):
        self._provider = whatsapp_provider

    def execute(self, payload: PairingPayload) -> dict:
        """
        Solicita o código de pareamento para o número fornecido.
        """
        try:
            code = self._provider.request_pairing_code(payload.phone_number)
            return {
                "success": True,
                "pairing_code": code,
                "phone_number": payload.phone_number
            }
        except Exception as e:
            logger.error(f"Erro no RequestPairingUseCase: {e}")
            if isinstance(e, NotificationDeliveryError):
                raise e
            raise NotificationDeliveryError(f"Falha não tratada ao gerar pairing code: {str(e)}")
