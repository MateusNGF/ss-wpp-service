from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Configurações da aplicação.
    Carrega variáveis de ambiente validando tipos e provendo fallbacks para dev.
    """
    database_url: str = Field("sqlite:///db.sqlite3", description="URL de conexão com o banco de dados PostgreSQL.")
    bot_token: str = Field("dev-token-123", description="Token de autorização para consumir a API (X-Bot-Token).")

    # Configuração do pydantic para ler de um possível .env (opcional)
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

# Instância única das configurações
settings = Settings()
