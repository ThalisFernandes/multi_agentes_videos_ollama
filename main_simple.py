from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import datetime

app = FastAPI(
    title="Multi-Agent Content System",
    description="Sistema de geração de conteúdo com múltiplos agentes",
    version="1.0.0"
)

# configuração CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# monta arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Sistema Multi-Agentes funcionando!", "status": "online"}

@app.get("/app")
async def serve_frontend():
    """Serve o frontend da aplicação"""
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "multi-agent-content-system"}

# armazenamento temporário dos briefs (em produção usar banco de dados)
brief_storage = {}

@app.post("/brief")
async def process_brief(brief_data: dict):
    # gera ID único para o brief
    brief_id = f"brief-{uuid.uuid4().hex[:8]}-{int(datetime.now().timestamp())}"
    
    # armazena o brief para usar na personalização
    brief_storage[brief_id] = brief_data
    
    return {
        "message": "Brief recebido com sucesso",
        "brief_id": brief_id,
        "status": "processing",
        "data": brief_data
    }

@app.get("/brief/{brief_id}/status")
async def get_brief_status(brief_id: str):
    # busca dados do brief armazenado
    brief_data = brief_storage.get(brief_id, {})
    
    # extrai informações do brief para personalização
    topic = brief_data.get('topic', 'Marketing Digital')
    target_audience = brief_data.get('target_audience', 'Público geral')
    tonality = brief_data.get('tonality', 'casual')
    platforms = brief_data.get('platforms', ['instagram'])
    additional_info = brief_data.get('additional_info', '')
    
    # personaliza o conteúdo baseado no brief
    mock_result = {
        "brief": {
            "topic": topic,
            "target_audience": target_audience,
            "tonality": tonality,
            "platforms": platforms,
            "additional_info": additional_info
        },
        "copywriter_result": {
            "scripts": [
                {
                    "platform": platforms[0] if platforms else "instagram",
                    "script": f"Oi pessoal! Hoje vou falar sobre {topic.lower()} para {target_audience.lower()}! 🚀",
                    "hook": f"Você sabia que {topic.lower()} pode transformar completamente seu negócio?",
                    "cta": f"Salva esse post sobre {topic.lower()} e me conta nos comentários o que você achou!"
                }
            ],
            "hashtags": [f"#{topic.lower().replace(' ', '')}", "#dicas", "#conteudo"],
            "posting_schedule": "Segunda às 19h, Quarta às 15h"
        },
        "editor_result": {
            "improvements": [
                f"Adicionar mais energia na introdução sobre {topic}",
                f"Incluir exemplo prático relacionado a {topic}",
                f"Reforçar CTA direcionado para {target_audience}"
            ],
            "final_script": f"Oi pessoal! 🔥 Hoje vou ensinar sobre {topic} especialmente para {target_audience}!",
            "engagement_score": 8.5
        },
        "images_result": {
            "prompts": [
                f"Professional content about {topic}, modern style, bright lighting, targeting {target_audience}",
                f"Social media concept for {topic}, vibrant colors, digital marketing style",
                f"Success visualization for {topic}, minimalist design, engaging for {target_audience}"
            ],
            "composition_tips": ["Use close-up shots", "Bright color palette", "Focus on target audience connection"],
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        },
        "production_result": {
            "filming_plans": [
                {"shot_type": "close-up", "background": "ambiente profissional", "lighting": "luz natural + ring light"},
                {"shot_type": "plano médio", "background": "cenário relacionado ao tema", "lighting": "softbox lateral"},
                {"shot_type": "detalhe", "background": "elementos do tema", "lighting": "luz difusa"}
            ],
            "presenter_lines": [
                f"E aí, {target_audience.lower()}!",
                f"Vamos falar sobre {topic.lower()}",
                "Isso vai mudar sua perspectiva!",
                "Agora vem a parte mais importante",
                "Não esquece de salvar!",
                "Comenta aqui embaixo o que achou!"
            ],
            "editing_rhythm": f"Cortes dinâmicos para {target_audience}, transições rápidas, música {tonality}"
        },
        "content_ideas": {
            "content_ideas": [
                {
                    "title": f"5 Segredos sobre {topic} que {target_audience} precisa saber",
                    "concept": f"Dicas específicas de {topic} para {target_audience}",
                    "viral_potential": 0.85,
                    "platform_fit": platforms
                },
                {
                    "title": f"Antes vs Depois: Transformação com {topic}",
                    "concept": f"Case real de transformação usando {topic}",
                    "viral_potential": 0.78,
                    "platform_fit": platforms
                }
            ],
            "trending_topics": [topic.lower(), target_audience.lower(), "dicas", "conteudo"]
        },
        "task_id": brief_id,
        "created_at": datetime.now().isoformat(),
        "status": "completed"
    }
    
    return {
        "brief_id": brief_id,
        "status": "completed",
        "progress": 100,
        "result": mock_result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)