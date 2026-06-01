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

# Comando para rodar o bot (o -u garante que os logs apareçam em tempo real)
CMD ["python", "-u", "bot.py"]