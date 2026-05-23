FROM python:3.12-slim

# Evitar gravação de ficheiros pyc no disco e buffers em stdin/stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências essenciais do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar requisitos primeiro para melhor caching de layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código fonte do backend
COPY . .

# Dar permissões de execução para o script de arranque
RUN chmod +x start.sh

# Porta padrão exposta do FastAPI
EXPOSE 8000

# Script de arranque inteligente
CMD ["./start.sh"]
