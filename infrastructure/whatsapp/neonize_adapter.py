import logging
import threading
from typing import Optional

from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, event
from neonize.utils import log as neonize_log
from neonize.types import MessageServerID

from core.interfaces.whatsapp_provider import IWhatsAppProvider
from core.exceptions.domain_exceptions import NotificationDeliveryError

# Configura o log do neonize
neonize_log.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

class NeonizeAdapter(IWhatsAppProvider):
    """
    Adaptador concreto para a biblioteca Neonize.
    Isola os detalhes técnicos (threads, loops, JID) do restante da aplicação.
    """
    def __init__(self, database_url: str):
        self._database_url = database_url
        self._client: Optional[NewClient] = None
        self._thread: Optional[threading.Thread] = None
        self._is_connected = False

    def _build_jid(self, phone_number: str) -> str:
        """Formata o número de telefone para o padrão JID do WhatsApp."""
        if not phone_number.endswith("@s.whatsapp.net"):
            return f"{phone_number}@s.whatsapp.net"
        return phone_number

    def _run_client(self):
        """Executa a conexão do cliente em uma thread separada."""
        logger.info("Iniciando conexão Neonize em background...")
        try:
            self._client.connect()
            event.wait()
        except Exception as e:
            logger.error(f"Erro na thread do Neonize: {e}")
            self._is_connected = False

    def connect(self) -> None:
        """Inicializa a conexão Neonize."""
        if self._is_connected:
            return

        try:
            self._client = NewClient(self._database_url, uuid="bot_producao")
            
            # Registra eventos
            @self._client.event(ConnectedEv)
            def on_connected(client: NewClient, ev: ConnectedEv):
                logger.info("✅ Bot conectado com sucesso via Neonize Adapter!")
                self._is_connected = True

            @self._client.event(MessageEv)
            def on_message(client: NewClient, ev: MessageEv):
                # Opcional: tratar mensagens recebidas
                pass

            # Inicia em thread separada para não bloquear o FastAPI
            self._thread = threading.Thread(target=self._run_client, daemon=True)
            self._thread.start()
        except Exception as e:
            logger.error(f"Falha ao iniciar Neonize: {e}")
            raise NotificationDeliveryError(f"Falha ao inicializar o provedor do WhatsApp: {e}")

    def disconnect(self) -> None:
        """Encerra a conexão com o WhatsApp."""
        if self._client and self._is_connected:
            logger.info("Desconectando cliente Neonize...")
            try:
                self._client.disconnect()
            except Exception as e:
                logger.error(f"Erro ao desconectar Neonize: {e}")
            finally:
                self._is_connected = False

    def send_message(self, phone_number: str, text: str) -> None:
        """
        Envia uma mensagem utilizando o Neonize.
        """
        if not self._is_connected or not self._client:
            raise NotificationDeliveryError("O provedor do WhatsApp não está conectado.")

        jid = self._build_jid(phone_number)
        logger.info(f"Enviando mensagem para {jid}")
        
        try:
            # Envia a mensagem (o Neonize pode lançar exceções se falhar)
            response = self._client.send_message(jid, text)
            # O Neonize retorna um MessageServerID ou similar.
            if not response:
                 logger.warning("Nenhuma resposta obtida após envio da mensagem (verifique os logs).")
                 
            logger.info(f"Mensagem enviada com sucesso para {jid}.")
        except Exception as e:
            logger.error(f"Falha no envio Neonize: {e}")
            raise NotificationDeliveryError(f"Erro ao enviar mensagem via Neonize: {str(e)}")
