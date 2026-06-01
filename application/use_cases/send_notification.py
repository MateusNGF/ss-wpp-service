import logging
from core.interfaces.whatsapp_provider import IWhatsAppProvider
from core.models.schemas import NotificationPayload
from core.exceptions.domain_exceptions import NotificationDeliveryError

logger = logging.getLogger(__name__)

class SendNotificationUseCase:
    """
    Caso de Uso: Enviar Notificação.
    
    Responsabilidade Única (SRP):
    - Receber os dados da notificação (payload).
    - Executar as regras de negócio de envio.
    - Utilizar o provedor injetado para a ação técnica.
    """
    def __init__(self, whatsapp_provider: IWhatsAppProvider):
        self._provider = whatsapp_provider

    def execute(self, payload: NotificationPayload) -> dict:
        """
        Executa o envio da notificação.
        
        Args:
            payload (NotificationPayload): Os dados previamente validados (via Pydantic).
            
        Returns:
            dict: Resposta de sucesso padronizada.
            
        Raises:
            NotificationDeliveryError: Se houver falha no envio.
        """
        try:
            logger.info(f"Executando SendNotificationUseCase para o número {payload.phone_number}")
            
            # Chama o provedor abstraído sem saber que é o Neonize (DIP)
            self._provider.send_message(payload.phone_number, payload.text)
            
            # Retorna um formato padronizado de sucesso
            return {
                "success": True,
                "message": "Notificação enviada com sucesso.",
                "phone_number": payload.phone_number
            }
        except Exception as e:
            logger.error(f"Erro no SendNotificationUseCase: {e}")
            # Garante que qualquer erro genérico seja embrulhado em uma exceção de domínio
            if isinstance(e, NotificationDeliveryError):
                raise e
            raise NotificationDeliveryError(f"Falha não tratada ao enviar notificação: {str(e)}")
