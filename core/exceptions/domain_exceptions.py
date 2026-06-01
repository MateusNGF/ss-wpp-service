class DomainException(Exception):
    """Exceção base para o domínio da aplicação."""
    pass

class InvalidNumberError(DomainException):
    """Lançada quando um número de telefone é inválido ou mal formatado."""
    pass

class NotificationDeliveryError(DomainException):
    """Lançada quando ocorre um erro na entrega da mensagem (ex: falha no provedor)."""
    pass

class UnauthorizedError(DomainException):
    """Lançada quando uma requisição falha na validação de segurança."""
    pass
