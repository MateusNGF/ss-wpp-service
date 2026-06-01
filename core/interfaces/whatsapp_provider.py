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
