import logging
import io
import base64
from typing import Optional
from core.interfaces.whatsapp_provider import IWhatsAppProvider

logger = logging.getLogger(__name__)

class GetQRCodeUseCase:
    """
    Caso de Uso: Obter o QR Code atual para pareamento.
    """
    def __init__(self, whatsapp_provider: IWhatsAppProvider):
        self._provider = whatsapp_provider

    def execute(self) -> dict:
        """
        Retorna a string bruta do QR code e a representação em imagem Base64 (PNG).
        """
        try:
            qr_string = self._provider.get_qr_code()
            if not qr_string:
                return {
                    "success": False,
                    "message": "QR Code não disponível (bot já conectado ou ainda não gerado)."
                }

            # Gera a imagem PNG do QR code em base64 usando a biblioteca segno
            qr_base64 = None
            try:
                import segno
                buff = io.BytesIO()
                # Cria o QR code e salva em memória no formato PNG
                segno.make_qr(qr_string).save(buff, kind='png', scale=5)
                qr_base64 = f"data:image/png;base64,{base64.b64encode(buff.getvalue()).decode('utf-8')}"
            except Exception as e:
                logger.error(f"Erro ao converter QR Code para base64 com segno: {e}")

            return {
                "success": True,
                "qr_code": qr_string,
                "qr_image": qr_base64
            }
        except Exception as e:
            logger.error(f"Erro no GetQRCodeUseCase: {e}")
            return {
                "success": False,
                "message": f"Erro interno ao processar QR Code: {str(e)}"
            }
