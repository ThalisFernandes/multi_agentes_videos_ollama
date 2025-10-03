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
        "content_creator_result": {
            "full_content": [
                {
                    "type": "post_completo",
                    "title": f"Guia Completo: {topic} para {target_audience}",
                    "content": f"""
🎯 **{topic.upper()} PARA {target_audience.upper()}**

Olá, {target_audience.lower()}! Hoje vou compartilhar tudo que você precisa saber sobre {topic.lower()}.

📍 **Por que isso é importante?**
{topic} tem se tornado cada vez mais relevante para {target_audience.lower()}, especialmente porque pode transformar completamente a forma como você trabalha e se relaciona com seu público.

🔥 **Principais benefícios:**
• Maior engajamento com seu público
• Resultados mais consistentes
• Economia de tempo e recursos
• Diferenciação no mercado

💡 **Dica prática:**
Comece implementando {topic.lower()} de forma gradual. Teste uma estratégia por vez e meça os resultados antes de expandir.

📈 **Próximos passos:**
1. Defina seus objetivos claros
2. Escolha as ferramentas certas
3. Crie um cronograma realista
4. Monitore e ajuste constantemente

Salva esse post e me conta nos comentários: qual sua maior dificuldade com {topic.lower()}?

#{topic.lower().replace(' ', '')} #{target_audience.lower().replace(' ', '')} #dicas #conteudo #estrategia
                    """,
                    "platform": platforms[0] if platforms else "instagram",
                    "estimated_reach": "5k-15k",
                    "engagement_prediction": "alto"
                },
                {
                    "type": "carrossel",
                    "title": f"7 Passos para Dominar {topic}",
                    "slides": [
                        f"Slide 1: Introdução ao {topic}",
                        f"Slide 2: Primeiro passo - Planejamento",
                        f"Slide 3: Segundo passo - Execução",
                        f"Slide 4: Terceiro passo - Monitoramento",
                        f"Slide 5: Quarto passo - Otimização",
                        f"Slide 6: Quinto passo - Expansão",
                        f"Slide 7: Sexto passo - Automação",
                        f"Slide 8: Sétimo passo - Resultados"
                    ],
                    "platform": "instagram",
                    "design_notes": f"Use cores vibrantes, fonte legível, elementos visuais relacionados a {topic}"
                }
            ],
            "content_pillars": [
                f"Educação sobre {topic}",
                f"Cases de sucesso em {topic}",
                f"Dicas práticas para {target_audience}",
                f"Tendências em {topic}",
                "Bastidores e processos"
            ],
            "content_calendar": {
                "segunda": f"Dica rápida sobre {topic}",
                "terca": f"Case de sucesso com {target_audience}",
                "quarta": f"Tutorial prático de {topic}",
                "quinta": f"Tendências em {topic}",
                "sexta": f"Reflexão sobre {topic}",
                "sabado": "Conteúdo mais descontraído",
                "domingo": "Inspiração e motivação"
            },
            "tone_guidelines": f"Tom {tonality}, linguagem acessível para {target_audience}, sempre educativo e prático"
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