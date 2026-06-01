import logging
from core.interfaces.whatsapp_provider import IWhatsAppProvider
from core.exceptions.domain_exceptions import NotificationDeliveryError

logger = logging.getLogger(__name__)

class LogoutUseCase:
    """
    Caso de Uso: Efetuar logout do bot.
    """
    def __init__(self, whatsapp_provider: IWhatsAppProvider):
        self._provider = whatsapp_provider

    def execute(self) -> dict:
        """
        Executa a desconexão e limpeza das credenciais do bot.
        """
        try:
            logger.info("Executando LogoutUseCase...")
            self._provider.logout()
            return {
                "success": True,
                "message": "Logout efetuado com sucesso. O bot foi desconectado e as credenciais limpas."
            }
        except Exception as e:
            logger.error(f"Erro no LogoutUseCase: {e}")
            if isinstance(e, NotificationDeliveryError):
                raise e
            raise NotificationDeliveryError(f"Falha não tratada ao efetuar logout: {str(e)}")
