from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Multi-Agent Content System",
    description="Sistema de geração de conteúdo com múltiplos agentes",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Sistema Multi-Agentes funcionando!", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "multi-agent-content-system"}

@app.post("/brief")
async def process_brief(brief_data: dict):
    # versao simplificada sem dependencias complexas
    return {
        "message": "Brief recebido com sucesso",
        "brief_id": "test-123",
        "status": "processing",
        "data": brief_data
    }

@app.get("/brief/{brief_id}/status")
async def get_brief_status(brief_id: str):
    # simulando resultado completo dos agentes
    mock_result = {
        "brief": {
            "topic": "Marketing Digital",
            "target_audience": "Jovens 18-25",
            "tonality": "casual",
            "platforms": ["tiktok", "instagram"]
        },
        "copywriter_result": {
            "scripts": [
                {
                    "platform": "tiktok",
                    "script": "Oi pessoal! Hoje vou ensinar 3 dicas de marketing que vão bombar seu negócio! 🚀",
                    "hook": "Você sabia que 90% das pessoas fazem isso errado?",
                    "cta": "Salva esse post e me conta nos comentários qual dica você vai testar primeiro!"
                }
            ],
            "hashtags": ["#marketingdigital", "#dicas", "#empreendedorismo"],
            "posting_schedule": "Segunda às 19h, Quarta às 15h"
        },
        "editor_result": {
            "improvements": [
                "Adicionar mais energia na introdução",
                "Incluir exemplo prático na dica 2",
                "Reforçar CTA no final"
            ],
            "final_script": "Oi pessoal! 🔥 Hoje vou ensinar 3 dicas INFALÍVEIS de marketing que vão BOMBAR seu negócio!",
            "engagement_score": 8.5
        },
        "images_result": {
            "prompts": [
                "Young entrepreneur working on laptop, modern office, bright lighting, professional but casual",
                "Social media icons floating around smartphone, vibrant colors, digital marketing concept",
                "Success graph trending upward, minimalist design, blue and orange gradient"
            ],
            "composition_tips": ["Use close-up shots", "Bright color palette", "Focus on facial expressions"],
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        },
        "production_result": {
            "filming_plans": [
                {"shot_type": "close-up", "background": "escritório moderno", "lighting": "luz natural + ring light"},
                {"shot_type": "plano médio", "background": "parede branca", "lighting": "softbox lateral"},
                {"shot_type": "detalhe", "background": "mesa organizada", "lighting": "luz difusa"}
            ],
            "presenter_lines": [
                "E aí, galera!",
                "Primeira dica é essa aqui ó",
                "Isso mudou minha vida!",
                "Agora vem a parte mais importante",
                "Não esquece de salvar!",
                "Comenta aqui embaixo!"
            ],
            "editing_rhythm": "Cortes a cada 3 segundos, transições rápidas, música upbeat"
        },
        "content_ideas": {
            "content_ideas": [
                {
                    "title": "5 Erros que Matam seu Marketing",
                    "concept": "Mostrar erros comuns e como corrigir",
                    "viral_potential": 0.85,
                    "platform_fit": ["tiktok", "instagram"]
                },
                {
                    "title": "Antes vs Depois: Transformação Digital",
                    "concept": "Case real de transformação",
                    "viral_potential": 0.78,
                    "platform_fit": ["instagram", "youtube"]
                }
            ],
            "trending_topics": ["marketing digital", "empreendedorismo", "redes sociais"]
        },
        "task_id": brief_id,
        "created_at": "2024-01-15T10:30:00",
        "status": "completed"
    }
    
    return {
        "brief_id": brief_id,
        "status": "completed",
        "progress": 100,
        "result": mock_result  # ← AQUI estão os resultados dos agentes!
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)