from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class Platform(str, Enum):
    """Plataformas suportadas pelo sistema"""
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"

class Tonality(str, Enum):
    """Tons de voz disponíveis"""
    HUMORISTICO = "humoristico"
    PROFISSIONAL = "profissional"
    CASUAL = "casual"
    EDUCATIVO = "educativo"
    INSPIRACIONAL = "inspiracional"

class AgentType(str, Enum):
    """Tipos de agentes no sistema"""
    MANAGER = "manager"
    COPYWRITER = "copywriter"
    EDITOR = "editor"
    PUBLICO = "agente_para_o_publico"
    IMAGENS = "agente_criacao_imagens"
    PRODUCAO = "agente_auxiliar_producao"
    CONTEUDO = "agente_de_conteudo"

# modelos de entrada (brief)
class ContentBrief(BaseModel):
    """Brief inicial do usuário para geração de conteúdo"""
    topic: str = Field(..., description="Tópico principal do conteúdo")
    duration: Optional[int] = Field(60, description="Duração em segundos")
    tonality: Tonality = Field(Tonality.CASUAL, description="Tom de voz desejado")
    target_audience: str = Field("público geral", description="Público-alvo")
    platforms: List[Platform] = Field([Platform.TIKTOK], description="Plataformas de destino")
    additional_context: Optional[str] = Field(None, description="Contexto adicional")

# modelos de saída padronizados
class AgentMetadata(BaseModel):
    """Metadados padrão de resposta dos agentes"""
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nível de confiança na resposta")
    tokens_used: int = Field(..., description="Tokens utilizados na geração")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento em segundos")

class CopywriterOutput(BaseModel):
    """Saída padronizada do agente Copywriter"""
    title: str = Field(..., description="Título principal")
    hooks: List[str] = Field(..., min_items=3, max_items=3, description="3 hooks de 3-7 segundos")
    script_short: str = Field(..., description="Script de 45-60 segundos")
    description: str = Field(..., description="Descrição para a plataforma")
    hashtags: List[str] = Field(..., min_items=5, max_items=5, description="5 hashtags relevantes")
    cta: str = Field(..., description="Call to action")

class EditorOutput(BaseModel):
    """Saída padronizada do agente Editor"""
    version_a: str = Field(..., description="Versão conservadora")
    version_b: str = Field(..., description="Versão concisa/high-energy")
    improvements: List[str] = Field(..., description="Lista de melhorias aplicadas")

class PublicoOutput(BaseModel):
    """Saída padronizada do agente para público"""
    response: str = Field(..., description="Resposta principal")
    follow_up: Optional[str] = Field(None, description="Mensagem de follow-up se necessário")
    escalate_to_support: bool = Field(False, description="Se deve escalar para suporte")

class ImagePrompt(BaseModel):
    """Prompt individual para geração de imagem"""
    prompt: str = Field(..., description="Prompt para Stable Diffusion/Midjourney")
    style: str = Field(..., description="Estilo da imagem")
    composition: str = Field(..., description="Composição recomendada")

class ImagensOutput(BaseModel):
    """Saída padronizada do agente de criação de imagens"""
    image_prompts: List[ImagePrompt] = Field(..., min_items=3, max_items=3)
    thumbnail_recommendations: List[str] = Field(..., description="Recomendações para thumbnail")
    color_palette: List[str] = Field(..., description="Paleta de cores sugerida")

class ProductionSuggestion(BaseModel):
    """Sugestão individual de produção"""
    shot_type: str = Field(..., description="Tipo de plano (close, meio, etc)")
    background: str = Field(..., description="Fundo sugerido")
    lighting: str = Field(..., description="Sugestão de iluminação")

class ProducaoOutput(BaseModel):
    """Saída padronizada do agente auxiliar de produção"""
    filming_plans: List[ProductionSuggestion] = Field(..., min_items=5, max_items=5)
    presenter_lines: List[str] = Field(..., min_items=6, max_items=6, description="6 falas curtas")
    editing_rhythm: str = Field(..., description="Ritmo de edição sugerido")

class ContentIdea(BaseModel):
    """Ideia individual de conteúdo"""
    title: str = Field(..., description="Título da ideia")
    concept: str = Field(..., description="Conceito da ideia")
    viral_potential: float = Field(..., ge=0.0, le=1.0, description="Potencial viral (0-1)")
    platform_fit: List[Platform] = Field(..., description="Plataformas mais adequadas")

class ConteudoOutput(BaseModel):
    """Saída padronizada do agente de conteúdo"""
    content_ideas: List[ContentIdea] = Field(..., min_items=7, max_items=7)
    trending_topics: List[str] = Field(..., description="Tópicos em alta identificados")

# resposta padronizada de qualquer agente
class AgentResponse(BaseModel):
    """Resposta padronizada de qualquer agente"""
    agent: AgentType = Field(..., description="Tipo do agente que gerou a resposta")
    output: Dict[str, Any] = Field(..., description="Saída específica do agente")
    metadata: AgentMetadata = Field(..., description="Metadados da resposta")
    task_id: str = Field(..., description="ID único da tarefa")

# modelo para orquestração do manager
class ManagerTask(BaseModel):
    """Tarefa individual para um agente"""
    agent: AgentType = Field(..., description="Agente responsável")
    input_data: Dict[str, Any] = Field(..., description="Dados de entrada para o agente")
    priority: int = Field(1, ge=1, le=5, description="Prioridade da tarefa (1=alta, 5=baixa)")

class ManagerPlan(BaseModel):
    """Plano de execução do Manager"""
    tasks: List[ManagerTask] = Field(..., description="Lista de tarefas a executar")
    execution_order: List[str] = Field(..., description="Ordem de execução (task_ids)")
    estimated_time: int = Field(..., description="Tempo estimado em segundos")

# modelo final agregado
class ContentPackage(BaseModel):
    """Pacote final de conteúdo gerado"""
    brief: ContentBrief = Field(..., description="Brief original")
    copywriter_result: Optional[CopywriterOutput] = None
    editor_result: Optional[EditorOutput] = None
    images_result: Optional[ImagensOutput] = None
    production_result: Optional[ProducaoOutput] = None
    content_ideas: Optional[ConteudoOutput] = None
    task_id: str = Field(..., description="ID único do pacote")
    created_at: str = Field(..., description="Timestamp de criação")
    status: str = Field("processing", description="Status do processamento")