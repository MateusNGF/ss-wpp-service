from fastapi import FastAPI
from contextlib import asynccontextmanager

from config.settings import settings
from presentation.api.routers.send import router as send_router
from infrastructure.whatsapp.neonize_adapter import NeonizeAdapter

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    Conecta ao banco e ao Neonize no startup.
    Desconecta no shutdown (Graceful Shutdown).
    """
    # Inicializa o adaptador
    provider = NeonizeAdapter(database_url=settings.database_url)
    
    # Armazena no state da aplicação para injeção manual nos endpoints
    app.state.whatsapp_provider = provider
    
    # Conecta o provedor
    provider.connect()
    
    yield
    
    # Desconecta graciosamente no shutdown
    provider.disconnect()

app = FastAPI(
    title="ss-wpp-service",
    description="Microsserviço de disparo de notificações via WhatsApp (Unidirecional)",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(send_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
