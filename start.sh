#!/bin/bash
set -e

echo "=================================================="
echo "          VOXFATURA AI - BOOTSTRAP                "
echo "=================================================="

echo "A aguardar pelo arranque da base de dados PostgreSQL..."

# Script Python inline para verificar se a porta do PostgreSQL está aberta
python -c "
import socket
import time
import sys
import os
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL', 'postgresql://ansebast:voxfatura_secret@db:5432/voxfatura')
url = urlparse(db_url)
host = url.hostname
port = url.port or 5432

print(f'A testar ligação TCP a {host}:{port}...')
for i in range(45):
    try:
        with socket.create_connection((host, port), timeout=2):
            print('PostgreSQL está ativo e aceita conexões!')
            sys.exit(0)
    except OSError:
        time.sleep(1)
print('Erro crítico: PostgreSQL não ficou pronto a tempo (timeout de 45 segundos).')
sys.exit(1)
"

echo "A verificar integridade e inicializar tabelas (se base de dados vazia)..."
python db_init.py --if-empty

echo "A iniciar o servidor FastAPI Uvicorn em produção..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
