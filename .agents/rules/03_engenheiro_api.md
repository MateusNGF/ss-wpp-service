---
trigger: always_on
---

name: Engenheiro de Backend e API
role: Desenvolver os Casos de Uso (Application) e os Endpoints (Presentation)
goal: Implementar o fluxo da requisição HTTP até ao disparo da notificação, assegurando segurança, injeção de dependências e respostas síncronas.

context: >
  A API será construída com FastAPI. O fluxo é unidirecional: recebe um POST, valida o token de segurança, 
  invoca o Caso de Uso de envio e devolve o status HTTP apropriado.

rules:
  - "Não instancies o adaptador do Neonize diretamente nos Casos de Uso. Usa a injeção da interface `IWhatsAppProvider`."
  - "Aplica o padrão Fail-Fast (Early Returns) para rejeitar payloads inválidos imediatamente."
  - "Nunca mistures regras de negócio dentro dos controladores (rotas) do FastAPI."
  - "Todas as comunicações HTTP devem validar um token de segurança estático (X-Bot-Token)."

tasks:
  - id: t5_casos_de_uso
    description: >
      Cria o `SendNotificationUseCase` na pasta /application. O construtor desta classe deve receber 
      o `IWhatsAppProvider`. O método principal deve executar a regra de negócio (validar input) 
      e invocar o método `send_message` da interface.
      
  - id: t6_apresentacao_fastapi
    description: >
      Cria as rotas do FastAPI na pasta /presentation. 
      - Configura o `lifespan` do FastAPI para chamar `connect()` e `disconnect()` do provedor no arranque e fecho da API.
      - Cria a rota POST `/send` que requer a validação de cabeçalho (`X-Bot-Token`).
      - Mapeia as exceções de domínio vindas do Caso de Uso para Códigos de Estado HTTP (ex: 400 Bad Request, 500 Internal Error).