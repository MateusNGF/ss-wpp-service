import logging
import threading
from typing import Optional

from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, DisconnectedEv, LoggedOutEv, event
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
        self._status = "desconectado"
        self._qr_code: Optional[str] = None

    def _build_jid(self, phone_number: str):
        """Formata o número de telefone para o padrão JID do WhatsApp usando build_jid do Neonize."""
        # Remove caracteres indesejados caso venham do request
        from neonize.utils import build_jid
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        # Tratamento OBRIGATÓRIO para números do Brasil (55) com 13 dígitos
        # Resolve o erro 400 Bad Request no privacy token e o participant list hash mismatch
        if clean_phone.startswith("55") and len(clean_phone) == 13:
            try:
                ddd = int(clean_phone[2:4])
                # Para DDDs > 27, o WhatsApp exige internamente o JID sem o 9º dígito
                if ddd > 27 and clean_phone[4] == '9':
                    clean_phone = clean_phone[:4] + clean_phone[5:]
                    logger.info(f"Ajuste BR: 9º dígito removido obrigatoriamente para o DDD {ddd}. JID final: {clean_phone}")
            except ValueError:
                pass

        return build_jid(clean_phone)

    def _run_client(self):
        """Executa a conexão do cliente em uma thread separada."""
        logger.info("Iniciando conexão Neonize em background...")
        try:
            self._client.connect()
            event.wait()
        except Exception as e:
            logger.error(f"Erro na thread do Neonize: {e}")
            self._is_connected = False
            self._status = "desconectado"

    def connect(self) -> None:
        """Inicializa a conexão Neonize."""
        if self._is_connected:
            return

        try:
            # Sempre recria o client para evitar deadlocks e estados presos no Go
            if self._client is not None:
                try:
                    self._client.disconnect()
                except:
                    pass
                # Força o Garbage Collector a limpar a instância antiga de CGo
                self._client = None

            self._client = NewClient(self._database_url, uuid="bot_producao")
            
            # Registra eventos
            @self._client.event(ConnectedEv)
            def on_connected(client: NewClient, ev: ConnectedEv):
                logger.info("✅ Bot conectado com sucesso via Neonize Adapter!")
                self._is_connected = True
                self._status = "conectado"
                self._qr_code = None  # Limpa o QR Code pois já conectou

            @self._client.qr
            def on_qr(client: NewClient, qr_bytes: bytes):
                logger.info("Novo QR Code recebido no Neonize Adapter.")
                self._qr_code = qr_bytes.decode('utf-8')
                # Opcional: manter print do QR code no terminal para logs do docker
                try:
                    import segno
                    segno.make_qr(qr_bytes).terminal(compact=True)
                except Exception as e:
                    pass # Suprimido erro do terminal no docker para evitar crash

            @self._client.event(DisconnectedEv)
            def on_disconnected(client: NewClient, ev: DisconnectedEv):
                logger.info("Bot desconectado.")
                self._is_connected = False
                self._status = "desconectado"

            @self._client.event(LoggedOutEv)
            def on_logged_out(client: NewClient, ev: LoggedOutEv):
                logger.info("Bot deslogado remotamente.")
                self._is_connected = False
                self._status = "deslogado"
                self._qr_code = None
                logger.info("Agendando reinício do cliente para permitir novo pareamento...")
                import threading
                threading.Timer(2.0, self.connect).start()

            @self._client.event(MessageEv)
            def on_message(client: NewClient, ev: MessageEv):
                # Opcional: tratar mensagens recebidas
                pass

            # Inicia em thread separada para não bloquear o FastAPI
            def _reconnect_task():
                logger.info("Executando self._client.connect()...")
                try:
                    self._client.connect()
                except Exception as e:
                    logger.error(f"Erro ao conectar cliente Neonize: {e}")
            
            import threading
            t = threading.Thread(target=_reconnect_task, daemon=True)
            t.start()
            
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
                self._status = "desconectado"

    def logout(self) -> None:
        """Desconecta a sessão atual e limpa as credenciais de login."""
        if not self._client:
            raise NotificationDeliveryError("O provedor do WhatsApp não foi inicializado.")
        
        try:
            logger.info("Efetuando logout do bot...")
            self._client.logout()
        except Exception as e:
            logger.error(f"Erro ao efetuar logout: {e}")
            raise NotificationDeliveryError(f"Falha ao realizar logout no Neonize: {str(e)}")
        finally:
            try:
                self._client.disconnect()
            except Exception:
                pass
            self._is_connected = False
            self._status = "deslogado"
            self._qr_code = None
            logger.info("Agendando reinício do cliente para permitir novo pareamento...")
            threading.Timer(2.0, self.connect).start()

    def send_message(self, phone_number: str, text: str) -> None:
        """
        Envia uma mensagem utilizando o Neonize.
        """
        if not self._is_connected or not self._client:
            raise NotificationDeliveryError("O provedor do WhatsApp não está conectado.")

        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        # Mantemos o tratamento BR básico caso o número precise disso
        if clean_phone.startswith("55") and len(clean_phone) == 13:
            try:
                ddd = int(clean_phone[2:4])
                if ddd > 27 and clean_phone[4] == '9':
                    clean_phone = clean_phone[:4] + clean_phone[5:]
                    logger.info(f"Ajuste prévio BR: {clean_phone}")
            except ValueError:
                pass

        logger.info(f"Consultando servidor do WhatsApp para {clean_phone} (evita Erro 463)...")
        try:
            # is_on_whatsapp faz o whatsmeow buscar a identidade primária
            responses = self._client.is_on_whatsapp("+" + clean_phone)
            if not responses or not responses[0].IsIn:
                raise NotificationDeliveryError(f"O número {phone_number} não possui WhatsApp ativo.")
            jid = responses[0].JID
            logger.info(f"JID validado via servidor: {jid.User}")
            
            # Força o carregamento dos tokens de privacidade (tctoken/cstoken) na memória.
            # Ajuda a evitar o Erro 463 mesmo se o PgBouncer do Postgres falhar ao salvar no banco.
            try:
                self._client.subscribe_presence(jid)
                self._client.get_user_info(jid)
                import time
                time.sleep(0.5)  # Pequeno delay para os pacotes XMPP de privacidade chegarem
            except Exception as e_info:
                logger.debug(f"Aviso ao buscar tokens extras (ignorado): {e_info}")

        except Exception as e:
            if isinstance(e, NotificationDeliveryError):
                raise e
            logger.warning(f"Falha ao validar no servidor ({e}). Usando fallback...")
            jid = self._build_jid(phone_number)
            logger.info(f"Enviando mensagem usando JID construído manualmente: {jid.User}")
        
        try:
            # Envia a mensagem
            response = self._client.send_message(jid, text)
            if not response:
                 logger.warning("Nenhuma resposta obtida após envio da mensagem (verifique os logs).")
                 
            logger.info(f"Mensagem enviada com sucesso para {jid.User}.")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Falha no envio Neonize: {error_msg}")
            
            # Tratamento específico para o bloqueio Anti-Spam do WhatsApp (463)
            if "error 463" in error_msg.lower() or "nackcallerreachouttimelocked" in error_msg.lower():
                raise NotificationDeliveryError(
                    f"WhatsApp bloqueou o envio para {phone_number} (Erro 463). "
                    "Motivo: Bloqueio Anti-Spam (Reachout Timelocked) para contatos frios. "
                    "Aguarde o bloqueio expirar ou peça para o contato enviar uma mensagem primeiro."
                )
                
            raise NotificationDeliveryError(f"Erro ao enviar mensagem via Neonize: {error_msg}")

    def get_status(self) -> str:
        """Retorna o status atual da conexão com o WhatsApp."""
        return self._status

    def get_qr_code(self) -> Optional[str]:
        """Retorna a string bruta do QR code gerado mais recentemente."""
        return self._qr_code

    def request_pairing_code(self, phone_number: str) -> str:
        """
        Solicita o código de pareamento para o número fornecido.
        A inicialização deve ter ocorrido antes.
        """
        if not self._client:
            raise NotificationDeliveryError("O provedor do WhatsApp não foi inicializado. Chame connect() primeiro.")
        
        if self._status == "conectado":
            raise NotificationDeliveryError("O bot já está conectado e autenticado. Não é possível gerar código de pareamento para uma sessão ativa.")
        
        try:
            logger.info(f"Solicitando pairing code para o número {phone_number}")
            code = self._client.PairPhone(phone_number, show_push_notification=True)
            return code
        except Exception as e:
            logger.error(f"Erro ao solicitar pairing code: {e}")
            raise NotificationDeliveryError(f"Falha ao gerar o código de pareamento: {str(e)}")
