FROM python:3.11-slim

# define diretório de trabalho
WORKDIR /app

# instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# copia requirements primeiro para cache de layers
COPY requirements.txt .

# instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# copia código da aplicação
COPY . .

# cria diretórios necessários
RUN mkdir -p /app/chroma_db /app/logs

# define variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# expõe porta da API
EXPOSE 8000

# comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]