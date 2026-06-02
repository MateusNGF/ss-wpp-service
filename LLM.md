# 🤖 Guia de Integração Ponta a Ponta (LLM.md)

Este documento atua como o **Master Prompt** e **Guia de Integração** para Large Language Models (LLMs) e desenvolvedores. Ele define como entender, evoluir e integrar sistemas externos com o **ss-wpp-service**.

---

## 🎯 1. O que é este Microsserviço?
O **ss-wpp-service** é uma API RESTful desenvolvida em Python (FastAPI) destinada ao **envio unidirecional de notificações via WhatsApp**. Ele opera em background com a biblioteca `neonize`, gerenciando as sessões criptografadas do WhatsApp (usando PostgreSQL/SQLite para persistência de estado).

---

## 🏗️ 2. Arquitetura e Padrões (Para Evolução do Código)

Se você (LLM) for solicitado a adicionar funcionalidades **neste** repositório, obedeça rigidamente aos seguintes padrões:

- **Clean Architecture & SOLID:** O código é estritamente dividido.
  - `/core`: Contratos (Interfaces), Exceções, Models (Pydantic). **Zero dependências externas** além de Pydantic.
  - `/application`: Casos de Uso. Regras de negócio puras (ex: `SendNotificationUseCase`). Injeta dependências via interfaces.
  - `/infrastructure`: Adaptadores externos (PostgreSQL, NeonizeAdapter). Único lugar onde a complexidade do banco e lib do WhatsApp habita.
  - `/presentation`: Endpoints FastAPI. Não pode conter lógica de negócio. Apenas delega aos Casos de Uso e formata a resposta.
- **ACID & Banco de Dados:** Nunca deixe transações órfãs. Proteja a integridade dos dados usando tratamento de exceções adequado.
- **Fail-Fast (Early Returns):** Rejeite payloads e tokens inválidos logo no início do fluxo. Sem if-elses aninhados (Hadouken code).
- **Tipagem Diamante:** Uso estrito de *Type Hints* do Python. Odiamos `Any`.
- **Nomes Intencionais:** Sem abreviações genéricas (`x`, `res`, `data`). Use `pairing_code_response`, `notification_payload`.

---

## 🚀 3. Fluxo de Integração (Para Sistemas Clientes)

Se você (LLM) for encarregado de escrever código em um **outro repositório** (ex: Frontend, CRM, ERP) que consumirá esta API, siga o ciclo de vida abaixo:

### 3.1. Autenticação (A Porta de Entrada)
Todas as requisições (exceto `/docs`) devem trafegar um Header de segurança.
- **Header:** `X-Bot-Token`
- **Validação:** Se ausente ou inválido, a API retorna `HTTP 401 Unauthorized`.
- **Regra:** Nunca exponha o token em frontends públicos. O cliente deve chamar a API através de um backend proxy ou Server Action.

### 3.2. Consulta de Status (`GET /status`)
Antes de iniciar disparos, o sistema cliente deve verificar se o bot está conectado.
- O cliente deve realizar *polling* (ou consulta lazy) neste endpoint.
- Respostas possíveis: `conectado`, `desconectado` ou `deslogado`.
- **Regra de UI:** Se diferente de `conectado`, o sistema integrador deve renderizar a tela de pareamento.

### 3.3. Fluxo de Pareamento
O sistema suporta duas formas de conectar o número de envio.

#### Opção A: Headless via Código (Recomendado)
Para UIs modernas. O usuário não precisa escanear QR Code com a câmera.
1. O cliente envia `POST /pair` enviando `{"phone_number": "5511999999999"}`.
2. A API devolve um `pairing_code` (ex: `ABCD-1234`).
3. O cliente exibe esse código.
4. O usuário abre o WhatsApp em seu dispositivo, vai em "Aparelhos Conectados", escolhe parear por telefone e digita o código.

#### Opção B: Tradicional via QR Code
1. O cliente chama `GET /qrcode`.
2. A API devolve um PNG base64 em `qr_image`.
3. O frontend cliente injeta na tela: `<img src="data:image/png;base64,..." />`.
4. O usuário aponta o celular.

### 3.4. Disparo de Notificação (`POST /send`)
Após validar o `/status` como conectado.
- **Payload:** `{"phone_number": "5511999999999", "text": "Sua mensagem aqui."}`
- **Formatação Automática:** O integrador **NÃO DEVE** se preocupar com formatos do WhatsApp (ex: `@s.whatsapp.net` ou regras do 9º dígito no BR). O microsserviço já lida com a sanitização.
- **Tratamento de Erro (Cliente):** 
  - `HTTP 400`: Erro de formatação do payload.
  - `HTTP 401`: Token inválido.
  - `HTTP 500`: Timeout, falha do Neonize ou falha de rede do WhatsApp. O integrador deve aplicar *retries* (ex: exponencial backoff) caso crucial.

### 3.5. Encerramento / Troca de Bot (`POST /logout`)
Se o integrador quiser desvincular a máquina atual para colocar um novo número.
- Esvazia os dados de sessão criptografados do banco e derruba a conexão. O sistema fica pronto para um novo `GET /qrcode` ou `POST /pair`.

---

## 🛡️ Dicas para Solução de Problemas (Troubleshooting)

- **Falhas de Conexão SSL (ex: cURL no Windows - `CRYPT_E_NO_REVOCATION_CHECK`):**
  Ao testar a API localmente ou contra um host com certificados estritos usando ferramentas nativas do Windows, adicione as flags para ignorar revogação caso haja bloqueios no ambiente:
  `curl -k --ssl-no-revoke ...`
  *Isto é estritamente para testes locais em terminais.*
- **Mensagem Enviada mas Não Entregue:** O `POST /send` confirma o enfileiramento na lib. A entrega depende de bateria/sinal do aparelho host se não for uma conta WhatsApp Business oficial (API da Meta). O integrador não deve assumir leitura garantida.
