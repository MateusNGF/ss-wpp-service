from pydantic import BaseModel, Field, field_validator
import re

class NotificationPayload(BaseModel):
    """Payload para envio de notificação."""
    phone_number: str = Field(..., description="Número de telefone do destinatário.")
    text: str = Field(..., min_length=1, description="Texto da mensagem a ser enviada.")

    @field_validator('phone_number')
    def validate_phone_number(cls, v: str) -> str:
        # Remove tudo que não for dígito
        cleaned = re.sub(r'\D', '', v)
        if not cleaned:
            raise ValueError("O número de telefone não pode estar vazio e deve conter apenas dígitos.")
        
        # Validação básica de tamanho (mínimo 10: DD + Número)
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("O número de telefone deve ter entre 10 e 15 dígitos numéricos válidos.")
            
        return cleaned
