FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para psycopg2-binary e outros
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY src/ ./src/

# Criar diretório de uploads e garantir permissões
RUN mkdir -p /app/src/static/uploads
RUN chmod -R 777 /app/src/static/uploads

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.main:app"]

