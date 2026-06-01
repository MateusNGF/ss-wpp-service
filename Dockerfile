FROM python:3.11-slim

# Instala dependências do sistema necessárias para compilação de pacotes
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

EXPOSE 8000

# Comando para rodar a API (FastAPI + uvicorn)
CMD ["uvicorn", "presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]