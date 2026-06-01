# 📱 ss-wpp-service

**Microsserviço de Notificações Unidirecionais via WhatsApp**

Um microsserviço de alta disponibilidade focado em disparo síncrono e assíncrono de notificações de texto pelo WhatsApp. Construído em **Python (FastAPI)** sob os rígidos padrões de **Clean Architecture**, **SOLID**, **Clean Code** e **ACID**.

---

## 🎯 Arquitetura (Clean Architecture)

O projeto foi meticulosamente desacoplado em camadas para garantir máxima manutenibilidade, testabilidade e respeito ao Princípio da Inversão de Dependência (DIP).

- 📂 **`/core`**: Coração do sistema. Contém os contratos (Interfaces), regras estritas e schemas de dados validados (Pydantic). Totalmente agnóstico de infraestrutura.
- 📂 **`/application`**: Casos de uso (`SendNotificationUseCase`). Orquestra a regra de negócio sem saber se o dado vem via HTTP ou qual biblioteca dispara o WhatsApp.
- 📂 **`/infrastructure`**: Adaptadores para o mundo externo. Contém a integração com o banco de dados (PostgreSQL) e o adaptador concreto para a biblioteca `neonize`.
- 📂 **`/presentation`**: Camada de entrada/saída HTTP. Gerencia a API FastAPI, controllers, validações de tokens de segurança (`X-Bot-Token`) e o ciclo de vida (Graceful Shutdown) da aplicação.
- 📂 **`/config`**: Ponto único de verdade para injeção de variáveis de ambiente seguras (com `pydantic-settings`).

---

## 🚀 Como Executar (Docker Compose)

A maneira mais rápida e resiliente de inicializar o projeto é via Docker. A infraestrutura já provisionará a API e um banco de dados **PostgreSQL** dedicado para gerenciar as sessões criptografadas do WhatsApp.

### 1. Inicialize a Stack

```bash
docker-compose up -d --build
```

### 2. Autentique o WhatsApp (Headless via API - Recomendado)

O microsserviço agora opera em modo **Headless**. Você pode conectar o bot sem precisar abrir o terminal para escanear um QR Code:

1. Chame o endpoint `/pair` informando o seu telefone:
   ```bash
   curl -X POST http://localhost:8000/pair \
     -H "Content-Type: application/json" \
     -H "X-Bot-Token: dev-token-123" \
     -d '{"phone_number": "5511999999999"}'
   ```
2. O endpoint responderá com um código de pareamento de 8 dígitos (ex: `ABCD-1234`).
3. No seu celular com WhatsApp, uma notificação solicitará o pareamento. Insira o código exibido pela API.
4. Verifique o status da conexão fazendo polling no endpoint `/status`.

---

### 3. Alternativa: Autentique via QR Code (Terminal)

Se preferir o fluxo tradicional, o Neonize imprimirá o QR Code no terminal.

Verifique os logs interativos do container:
```bash
docker-compose logs -f bot
```

*Pegue o seu celular, abra o WhatsApp, vá em Aparelhos Conectados > Conectar um aparelho, e aponte para o QR Code gerado no terminal.*

---

## 📖 Documentação da API

Quando o serviço estiver rodando, a documentação interativa Swagger do FastAPI estará disponível em:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

### Endpoints de Integração

#### 1. Enviar Notificação
**`POST /send`**

**Body (JSON Payload):**
```json
{
  "phone_number": "5511999999999",
  "text": "Olá! Esta é uma notificação disparada pelo ss-wpp-service!"
}
```
*Nota: O `phone_number` é automaticamente sanitizado e formatado para o padrão JID do WhatsApp.*

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -H "X-Bot-Token: dev-token-123" \
  -d '{"phone_number": "5511999999999", "text": "Teste de envio de mensagem via API!"}'
```

#### 2. Consultar Status da Conexão
**`GET /status`**

Retorna o estado atual da conexão com o WhatsApp. Útil para fazer polling e exibir o estado atual no seu dashboard frontend.

**Exemplo de Resposta:**
```json
{
  "success": true,
  "status": "desconectado"
}
```
*(Os valores de status possíveis são `conectado`, `desconectado` ou `deslogado`)*

#### 3. Solicitar Código de Pareamento (Pairing Code)
**`POST /pair`**

Gera um código alfanumérico para parear a conta com o celular através do número de telefone, permitindo conexão 100% headless.

**Body (JSON Payload):**
```json
{
  "phone_number": "5511999999999"
}
```

**Exemplo de Resposta:**
```json
{
  "success": true,
  "pairing_code": "ABCD-1234",
  "phone_number": "5511999999999"
}
```

#### 4. Consultar QR Code
**`GET /qrcode`**

Retorna a string bruta do QR Code gerado pelo WhatsApp (caso esteja no fluxo de autenticação via QR Code) juntamente com a representação em imagem codificada em Base64 (PNG), permitindo que você a renderize diretamente em uma tag `<img>` no seu frontend.

**Exemplo de Resposta:**
```json
{
  "success": true,
  "qr_code": "2@...",
  "qr_image": "data:image/png;base64,iVBORw0KGgoAAA..."
}
```

---

## 🛠️ Configuração e Variáveis de Ambiente

As principais variáveis da aplicação podem ser alteradas criando um arquivo `.env` na raiz ou atualizando a seção `environment` no `docker-compose.yml`:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `BOT_TOKEN` | `dev-token-123` | Token de segurança validado no Header HTTP. |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | URL de conexão com o banco para salvar o estado do Neonize. No Docker, utiliza-se a URL do Postgres embutido. |

---

## 🧑‍💻 Desenvolvimento Local

Caso queira executar e debugar fora do Docker:

1. Requer **Python 3.11+**.
2. Instale as dependências:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```
3. Execute o servidor HTTP via Uvicorn:
   ```bash
   uvicorn presentation.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
