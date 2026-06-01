from fastapi import Header, HTTPException, status
from config.settings import settings

def verify_bot_token(x_bot_token: str = Header(..., description="Token de segurança da API")):
    """
    Dependência do FastAPI para validar o token de segurança em cada requisição.
    """
    if x_bot_token != settings.bot_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API inválido ou ausente."
        )
    return x_bot_token
