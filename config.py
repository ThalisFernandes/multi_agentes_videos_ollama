import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import httpx
from typing import Optional

# carrega variáveis de ambiente
load_dotenv()

class OllamaConfig:
    """Configuração centralizada para Ollama e LangChain"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "mistral")
        self.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "2000"))
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        
        # configurações de callback para streaming (opcional)
        self.enable_streaming = os.getenv("OLLAMA_STREAMING", "false").lower() == "true"
        
    def create_llm(self, streaming: bool = None) -> OllamaLLM:
        """Cria instância do LLM Ollama configurado"""
        
        # usa configuração padrão se não especificado
        if streaming is None:
            streaming = self.enable_streaming
            
        # configura callbacks se streaming habilitado
        callback_manager = None
        if streaming:
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        return OllamaLLM(
            base_url=self.base_url,
            model=self.model_name,
            temperature=self.temperature,
            callback_manager=callback_manager,
            # configurações adicionais
            num_predict=self.max_tokens,
            timeout=self.timeout
        )
    
    async def check_ollama_health(self) -> dict:
        """Verifica se o Ollama está rodando e acessível"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [model.get("name", "") for model in models]
                    
                    return {
                        "status": "healthy",
                        "url": self.base_url,
                        "available_models": model_names,
                        "configured_model": self.model_name,
                        "model_available": any(self.model_name in name for name in model_names)
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"HTTP {response.status_code}",
                        "url": self.base_url
                    }
                    
        except httpx.ConnectError:
            return {
                "status": "connection_error",
                "message": "Não foi possível conectar ao Ollama",
                "url": self.base_url,
                "suggestion": "Verifique se o Ollama está rodando com: ollama serve"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "url": self.base_url
            }
    
    def get_model_info(self) -> dict:
        """Retorna informações sobre o modelo configurado"""
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "streaming": self.enable_streaming
        }

class LangChainConfig:
    """Configurações específicas do LangChain"""
    
    def __init__(self):
        self.verbose = os.getenv("LANGCHAIN_VERBOSE", "false").lower() == "true"
        self.debug = os.getenv("LANGCHAIN_DEBUG", "false").lower() == "true"
        
        # configurações de cache (se necessário)
        self.enable_cache = os.getenv("LANGCHAIN_CACHE", "false").lower() == "true"
        
        # configurações de rate limiting
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
        
    def get_chain_config(self) -> dict:
        """Retorna configurações para chains do LangChain"""
        return {
            "verbose": self.verbose,
            "debug": self.debug,
            "enable_cache": self.enable_cache,
            "rate_limit": self.max_requests_per_minute
        }

# instâncias globais (singleton pattern)
ollama_config = OllamaConfig()
langchain_config = LangChainConfig()

def get_configured_llm(streaming: bool = False) -> OllamaLLM:
    """Função helper para obter LLM configurado"""
    return ollama_config.create_llm(streaming=streaming)

async def verify_ollama_setup() -> dict:
    """Verifica se todo o setup do Ollama está correto"""
    health = await ollama_config.check_ollama_health()
    
    if health["status"] == "healthy":
        # verifica se o modelo específico está disponível
        if not health.get("model_available", False):
            health["warning"] = f"Modelo '{ollama_config.model_name}' não encontrado"
            health["suggestion"] = f"Execute: ollama pull {ollama_config.model_name}"
    
    return health

def get_system_prompts() -> dict:
    """Retorna os prompts de sistema para cada agente"""
    return {
        "manager": """Você é o Manager responsável por coordenar a criação de conteúdo. 
        Recebe um brief e decide quais agentes chamar e com que prioridade. 
        Seja conciso e priorize versões para TikTok e Instagram Reels.
        Retorne sempre em formato JSON válido.""",
        
        "copywriter": """Você é um copywriter especialista em social media. 
        Tom: {tonality}, público: {audience}. 
        Produza: 1 título, 3 hooks de 3-7s, script de 45-60s, descrição para plataforma {platform}, 5 hashtags. 
        Respeite o limite de caracteres da plataforma. Seja persuasivo e direto.
        Retorne sempre em formato JSON válido.""",
        
        "editor": """Você é um editor experiente. Recebe o script do Copywriter. 
        Ajuste para clareza, diminuir palavras redundantes, manter tom e otimizar para voz (fala natural). 
        Retorne versão A (conservadora) e versão B (concisa/high-energy).
        Retorne sempre em formato JSON válido.""",
        
        "publico": """Você é a voz oficial da marca '{brand_name}'. Persona: {persona_desc}. 
        Regras: 1) nunca prometer serviços; 2) ser educado; 3) encaminhar reclamações para suporte. 
        Para cada comentário, gere resposta curta e, se necessário, uma mensagem de follow-up.
        Retorne sempre em formato JSON válido.""",
        
        "imagens": """Baseado no script e na plataforma, produza 3 prompts de imagem para Stable Diffusion / Midjourney 
        e 3 recomendações de composição (close-up, color palette, focal point). 
        Inclua instruções para upscaling/crop para thumbnail.
        Retorne sempre em formato JSON válido.""",
        
        "producao": """Sugira 5 planos de filmagem (ex: close, meia-distância), backgrounds (real/virtual), 
        sugestões de iluminação e 6 falas curtas para o apresentador. 
        Se for TikTok, sugira cortes para 3 segundos de ritmo.
        Retorne sempre em formato JSON válido.""",
        
        "conteudo": """Gere 7 ideias de conteúdo que NÃO foram pedidas diretamente no brief 
        e que se alinham com a persona e tendências atuais (sem buscar web por hora). 
        Priorize formato de alta probabilidade de viralização.
        Retorne sempre em formato JSON válido."""
    }

# configurações de logging
import logging

def setup_logging():
    """Configura logging para o sistema"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('multi_agentes.log') if os.getenv("LOG_TO_FILE", "false").lower() == "true" else logging.NullHandler()
        ]
    )
    
    # configura logs específicos
    if langchain_config.debug:
        logging.getLogger("langchain").setLevel(logging.DEBUG)
        logging.getLogger("crewai").setLevel(logging.DEBUG)
    
    return logging.getLogger(__name__)

# inicializa logging
logger = setup_logging()