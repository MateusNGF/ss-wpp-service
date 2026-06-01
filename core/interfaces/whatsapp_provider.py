import abc

class IWhatsAppProvider(abc.ABC):
    """
    Interface abstrata para o provedor de envio de mensagens via WhatsApp.
    O sistema não deve depender de uma implementação específica (ex: Neonize),
    mas sim desta interface (Princípio de Inversão de Dependência).
    """

    @abc.abstractmethod
    def connect(self) -> None:
        """Inicializa a conexão com o WhatsApp."""
        pass

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Encerra a conexão com o WhatsApp."""
        pass

    @abc.abstractmethod
    def logout(self) -> None:
        """Desconecta a sessão atual e limpa as credenciais de login."""
        pass

    @abc.abstractmethod
    def send_message(self, phone_number: str, text: str) -> None:
        """
        Envia uma mensagem de texto para o número especificado.
        
        Args:
            phone_number (str): O número de telefone do destinatário.
            text (str): O conteúdo da mensagem.
            
        Raises:
            NotificationDeliveryError: Se ocorrer uma falha ao enviar a mensagem.
        """
        pass

    @abc.abstractmethod
    def get_status(self) -> str:
        """
        Retorna o status atual da conexão com o WhatsApp.
        Ex: 'conectado', 'desconectado', 'deslogado'.
        """
        pass

    @abc.abstractmethod
    def get_qr_code(self) -> Optional[str]:
        """
        Retorna a string bruta do QR code gerado mais recentemente, ou None se indisponível.
        """
        pass

    @abc.abstractmethod
    def request_pairing_code(self, phone_number: str) -> str:
        """
        Solicita um código numérico de pareamento à biblioteca para ser exibido ao usuário.
        
        Args:
            phone_number (str): O número de telefone em que o WhatsApp está instalado.
            
        Returns:
            str: O código de pareamento gerado (ex: ABCD-1234).
        """
        pass
