from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
import asyncio
from typing import Dict, List
import uuid
from datetime import datetime

from models import *
from agents import ContentCreationAgents, ContentCreationCrew

# carrega variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="Multi-Agentes Conteúdo API",
    description="Sistema para gerar conteúdo com múltiplos agentes especializados",
    version="1.0.0"
)

# configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# storage em memória para tasks (em produção usar Redis/DB)
active_tasks: Dict[str, ContentPackage] = {}
task_status: Dict[str, str] = {}

# inicializa agentes (singleton)
agents = None
crew = None

@app.on_event("startup")
async def startup_event():
    """Inicializa os agentes na startup da aplicação"""
    global agents, crew
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "mistral")
    
    try:
        agents = ContentCreationAgents(ollama_url, model_name)
        crew = ContentCreationCrew(agents)
        print(f"✅ Agentes inicializados com sucesso - Ollama: {ollama_url}")
    except Exception as e:
        print(f"❌ Erro ao inicializar agentes: {e}")

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Multi-Agentes Conteúdo API",
        "version": "1.0.0",
        "status": "running",
        "agents_ready": agents is not None,
        "endpoints": {
            "create_content": "/content/create",
            "get_task": "/content/task/{task_id}",
            "list_tasks": "/content/tasks",
            "respond_public": "/public/respond",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_initialized": agents is not None,
        "ollama_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    }

@app.post("/content/create", response_model=Dict[str, str])
async def create_content(brief: ContentBrief, background_tasks: BackgroundTasks):
    """
    Endpoint principal para criação de conteúdo
    Recebe um brief e inicia o processamento em background
    """
    if not crew:
        raise HTTPException(status_code=503, detail="Agentes não inicializados")
    
    task_id = str(uuid.uuid4())
    
    # marca task como em processamento
    task_status[task_id] = "processing"
    
    # adiciona task em background
    background_tasks.add_task(process_content_task, task_id, brief)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Conteúdo sendo gerado. Use /content/task/{task_id} para acompanhar"
    }

async def process_content_task(task_id: str, brief: ContentBrief):
    """Processa a criação de conteúdo em background"""
    try:
        # executa o crew de agentes
        result = crew.process_brief(brief)
        
        # salva resultado
        active_tasks[task_id] = result
        task_status[task_id] = "completed"
        
    except Exception as e:
        # marca como erro
        task_status[task_id] = f"error: {str(e)}"
        
        # cria pacote de erro
        error_package = ContentPackage(
            brief=brief,
            task_id=task_id,
            created_at=datetime.now().isoformat(),
            status=f"error: {str(e)}"
        )
        active_tasks[task_id] = error_package

@app.get("/content/task/{task_id}")
async def get_task_status(task_id: str):
    """Retorna o status e resultado de uma task específica"""
    
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    status = task_status[task_id]
    
    response = {
        "task_id": task_id,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    # se completada, inclui o resultado
    if task_id in active_tasks:
        response["result"] = active_tasks[task_id]
    
    return response

@app.get("/content/tasks")
async def list_tasks():
    """Lista todas as tasks ativas"""
    tasks = []
    
    for task_id, status in task_status.items():
        task_info = {
            "task_id": task_id,
            "status": status
        }
        
        if task_id in active_tasks:
            task_info["created_at"] = active_tasks[task_id].created_at
            task_info["brief_topic"] = active_tasks[task_id].brief.topic
        
        tasks.append(task_info)
    
    return {
        "total_tasks": len(tasks),
        "tasks": tasks
    }

class PublicComment(BaseModel):
    """Modelo para comentários do público"""
    comment: str
    platform: Platform
    post_id: Optional[str] = None

@app.post("/public/respond", response_model=PublicoOutput)
async def respond_to_public(comment_data: PublicComment):
    """
    Endpoint para responder comentários/DMs do público
    Usa o agente especializado para manter identidade da marca
    """
    if not crew:
        raise HTTPException(status_code=503, detail="Agentes não inicializados")
    
    brand_persona = os.getenv("BRAND_PERSONA", "Marca jovem e descontraída")
    
    try:
        response = crew.respond_to_public(comment_data.comment, brand_persona)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar resposta: {str(e)}")

class ContentIdeasRequest(BaseModel):
    """Request para geração de ideias criativas"""
    topic: str
    audience: str = "público geral"
    tonality: Tonality = Tonality.CASUAL

@app.post("/content/ideas", response_model=ConteudoOutput)
async def generate_content_ideas(request: ContentIdeasRequest):
    """
    Endpoint para gerar ideias criativas de conteúdo
    Usa apenas o agente de conteúdo para sugestões rápidas
    """
    if not agents:
        raise HTTPException(status_code=503, detail="Agentes não inicializados")
    
    # cria brief simplificado para o agente de conteúdo
    brief = ContentBrief(
        topic=request.topic,
        target_audience=request.audience,
        tonality=request.tonality,
        platforms=[Platform.TIKTOK]  # padrão
    )
    
    try:
        task = agents.create_conteudo_task(brief)
        # aqui executaria apenas este agente
        # por simplicidade, retornando estrutura mock
        
        ideas = []
        for i in range(7):
            idea = ContentIdea(
                title=f"Ideia {i+1} sobre {request.topic}",
                concept=f"Conceito criativo relacionado a {request.topic}",
                viral_potential=0.7 + (i * 0.05),  # mock
                platform_fit=[Platform.TIKTOK, Platform.INSTAGRAM]
            )
            ideas.append(idea)
        
        return ConteudoOutput(
            content_ideas=ideas,
            trending_topics=[request.topic, "tendência 1", "tendência 2"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ideias: {str(e)}")

@app.delete("/content/task/{task_id}")
async def delete_task(task_id: str):
    """Remove uma task do sistema"""
    
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    # remove da memória
    if task_id in task_status:
        del task_status[task_id]
    if task_id in active_tasks:
        del active_tasks[task_id]
    
    return {"message": f"Task {task_id} removida com sucesso"}

@app.get("/stats")
async def get_stats():
    """Estatísticas do sistema"""
    
    completed_tasks = sum(1 for status in task_status.values() if status == "completed")
    error_tasks = sum(1 for status in task_status.values() if "error" in status)
    processing_tasks = sum(1 for status in task_status.values() if status == "processing")
    
    return {
        "total_tasks": len(task_status),
        "completed": completed_tasks,
        "errors": error_tasks,
        "processing": processing_tasks,
        "agents_ready": agents is not None,
        "uptime": "calculado em implementação real"
    }

if __name__ == "__main__":
    # configurações do servidor
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"🚀 Iniciando servidor em {host}:{port}")
    print(f"📝 Debug mode: {debug}")
    print(f"🤖 Ollama URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )