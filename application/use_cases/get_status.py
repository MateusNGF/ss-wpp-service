import logging
from core.interfaces.whatsapp_provider import IWhatsAppProvider

logger = logging.getLogger(__name__)

class GetConnectionStatusUseCase:
    """
    Caso de Uso: Obter o status da conexão do WhatsApp.
    """
    def __init__(self, whatsapp_provider: IWhatsAppProvider):
        self._provider = whatsapp_provider

    def execute(self) -> dict:
        """
        Retorna o status atual da conexão encapsulado em um dicionário.
        """
        try:
            status = self._provider.get_status()
            return {
                "success": True,
                "status": status
            }
        except Exception as e:
            logger.error(f"Erro no GetConnectionStatusUseCase: {e}")
            return {
                "success": False,
                "status": "erro",
                "message": str(e)
            }
