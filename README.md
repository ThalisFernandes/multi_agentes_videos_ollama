# Sistema Multi-Agentes para Geração de Conteúdo

Sistema completo de geração de conteúdo usando FastAPI, CrewAI, LangChain e Ollama para criar conteúdo automatizado para múltiplas plataformas.

## 🏗️ Arquitetura

- **FastAPI**: API REST para orquestração
- **CrewAI**: Framework para agentes especializados
- **LangChain**: Integração com LLMs
- **Ollama**: LLM local (Mistral)
- **ChromaDB**: Vector database para RAG
- **Redis**: Cache e rate limiting
- **Nginx**: Proxy reverso e load balancer
- **Prometheus + Grafana**: Monitoramento

## 🚀 Deploy Rápido

### Pré-requisitos
- Docker e Docker Compose
- 8GB+ RAM (recomendado para Ollama)
- Portas disponíveis: 80, 8000, 11434, 6379, 9090, 3000

### Inicialização

```bash
# clona o repositório
git clone <seu-repo>
cd multi_agentes_conteúdo

# copia configurações
cp .env.example .env

# edita variáveis se necessário
nano .env

# inicia todos os serviços
docker-compose up -d

# verifica status
docker-compose ps
```

### Primeira Configuração

```bash
# baixa modelo Mistral no Ollama (pode demorar)
docker exec multi_agentes_ollama ollama pull mistral:latest

# verifica se modelo foi baixado
docker exec multi_agentes_ollama ollama list
```

## 📋 Endpoints Principais

### Geração de Conteúdo
```bash
# processa brief completo
POST /api/brief
{
  "topic": "Tendências de IA em 2024",
  "target_audience": "Profissionais de tecnologia",
  "tonality": "professional",
  "platforms": ["instagram", "linkedin"],
  "duration": 60,
  "additional_context": "Foco em aplicações práticas"
}

# verifica status da tarefa
GET /api/tasks/{task_id}

# responde comentário público
POST /api/public/comment
{
  "comment": "Que legal! Tem mais dicas?",
  "context": "Post sobre IA",
  "platform": "instagram"
}
```

### Monitoramento
```bash
# health check
GET /health

# estatísticas da memória
GET /api/memory/stats

# métricas do Prometheus
GET /metrics
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=mistral:latest

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Marca/Persona
BRAND_NAME=Sua Marca
BRAND_PERSONA=Inovadora e próxima do público
BRAND_VALUES=Autenticidade,Inovação,Conexão

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Customização de Agentes

Edite `agents.py` para ajustar:
- Prompts dos agentes
- Comportamentos específicos
- Novos tipos de agente

### Adicionando Guidelines da Marca

```python
from memory import get_memory_manager

memory = get_memory_manager()

# adiciona guideline
memory.store_brand_guideline(
    title="Tom de Voz",
    content="Sempre use linguagem acessível e evite jargões técnicos...",
    category="voice"
)

# adiciona tendência
memory.store_trend_insight(
    trend="Vídeos curtos verticais",
    description="Formato dominante em 2024...",
    platforms=[Platform.INSTAGRAM, Platform.TIKTOK]
)
```

## 📊 Monitoramento

### Grafana Dashboards
- **URL**: http://localhost:3000
- **Login**: admin / admin123
- **Dashboards**: Métricas da API, performance dos agentes, uso de recursos

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Targets**: API, Nginx, Redis, Ollama

### Logs
```bash
# logs da API
docker logs multi_agentes_api -f

# logs do Ollama
docker logs multi_agentes_ollama -f

# logs de todos os serviços
docker-compose logs -f
```

## 🛠️ Desenvolvimento

### Ambiente Local
```bash
# instala dependências
pip install -r requirements.txt

# configura Ollama local
ollama serve
ollama pull mistral:latest

# roda API em desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testes
```bash
# testa endpoint de health
curl http://localhost:8000/health

# testa geração de conteúdo
curl -X POST http://localhost:8000/api/brief \
  -H "Content-Type: application/json" \
  -d '{"topic": "Teste", "target_audience": "Desenvolvedores", "tonality": "casual", "platforms": ["instagram"], "duration": 30}'
```

## 🔍 Troubleshooting

### Problemas Comuns

**Ollama não responde**
```bash
# verifica se modelo foi baixado
docker exec multi_agentes_ollama ollama list

# reinicia serviço
docker-compose restart ollama
```

**API retorna erro 500**
```bash
# verifica logs
docker logs multi_agentes_api

# verifica conectividade com Ollama
docker exec multi_agentes_api curl http://ollama:11434/api/tags
```

**ChromaDB com erro de permissão**
```bash
# ajusta permissões
sudo chown -R 1000:1000 ./chroma_db
```

### Performance

**Otimizações recomendadas:**
- Aumente RAM para 16GB+ se usar modelos maiores
- Use SSD para melhor I/O do ChromaDB
- Configure rate limiting adequado para sua carga
- Monitore uso de CPU durante geração

## 📝 Estrutura do Projeto

```
├── agents.py          # Agentes CrewAI especializados
├── config.py          # Configurações e prompts
├── main.py           # API FastAPI principal
├── memory.py         # Vector database e RAG
├── models.py         # Schemas Pydantic
├── docker-compose.yml # Orquestração completa
├── Dockerfile        # Container da API
├── nginx.conf        # Configuração do proxy
├── prometheus.yml    # Configuração de monitoramento
└── requirements.txt  # Dependências Python
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja `LICENSE` para mais detalhes.