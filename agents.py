from crewai import Agent, Task, Crew
from langchain_ollama import OllamaLLM
from models import *
import json
import uuid
from datetime import datetime
from typing import Dict, Any

class ContentCreationAgents:
    """Classe que gerencia todos os agentes especializados do sistema"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434", model_name: str = "mistral"):
        # inicializa o LLM local via Ollama
        self.llm = OllamaLLM(
            base_url=ollama_base_url,
            model=model_name,
            temperature=0.7
        )
        
        # inicializa todos os agentes
        self._setup_agents()
    
    def _setup_agents(self):
        """Configura todos os agentes especializados"""
        
        # agente manager - orquestrador principal
        self.manager_agent = Agent(
            role="Content Manager",
            goal="Orquestrar a criação de conteúdo delegando tarefas aos agentes especializados",
            backstory="""Você é o Manager responsável por coordenar a criação de conteúdo. 
            Recebe um brief e decide quais agentes chamar e com que prioridade. 
            Seja conciso e priorize versões para TikTok e Instagram Reels.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
        
        # agente copywriter - criação de textos
        self.copywriter_agent = Agent(
            role="Social Media Copywriter",
            goal="Criar títulos, hooks, scripts e descrições otimizados para cada plataforma",
            backstory="""Você é um copywriter especialista em social media. 
            Produz conteúdo persuasivo e direto respeitando os limites de cada plataforma.
            Sempre gera: 1 título, 3 hooks de 3-7s, script de 45-60s, descrição e 5 hashtags.""",
            llm=self.llm,
            verbose=True
        )
        
        # agente editor - refinamento de textos
        self.editor_agent = Agent(
            role="Content Editor",
            goal="Refinar e otimizar textos para clareza e impacto",
            backstory="""Você é um editor experiente que recebe scripts do copywriter.
            Ajusta para clareza, remove redundâncias, mantém o tom e otimiza para fala natural.
            Sempre retorna versão A (conservadora) e versão B (concisa/high-energy).""",
            llm=self.llm,
            verbose=True
        )
        
        # agente para público - atendimento
        self.publico_agent = Agent(
            role="Brand Voice Representative",
            goal="Responder comentários e DMs mantendo a identidade da marca",
            backstory="""Você é a voz oficial da marca. Persona jovem e descontraída.
            Regras: 1) nunca prometer serviços; 2) ser educado; 3) encaminhar reclamações.
            Gera respostas curtas e mensagens de follow-up quando necessário.""",
            llm=self.llm,
            verbose=True
        )
        
        # agente criação de imagens - prompts para AI
        self.imagens_agent = Agent(
            role="AI Image Prompt Creator",
            goal="Gerar prompts otimizados para Stable Diffusion e Midjourney",
            backstory="""Você é especialista em criação de prompts para IA de imagens.
            Baseado no script e plataforma, produz 3 prompts detalhados e recomendações
            de composição incluindo instruções para thumbnail e upscaling.""",
            llm=self.llm,
            verbose=True
        )
        
        # agente auxiliar produção - sugestões técnicas
        self.producao_agent = Agent(
            role="Video Production Assistant",
            goal="Fornecer sugestões técnicas para produção de vídeo",
            backstory="""Você é um assistente de produção de vídeo experiente.
            Sugere planos de filmagem, backgrounds, iluminação e falas para o apresentador.
            Para TikTok, foca em cortes de 3 segundos de ritmo.""",
            llm=self.llm,
            verbose=True
        )
        
        # agente de conteúdo - ideias criativas
        self.conteudo_agent = Agent(
            role="Creative Content Strategist", 
            goal="Gerar ideias de conteúdo viral não solicitadas diretamente",
            backstory="""Você é um estrategista criativo que identifica tendências.
            Gera 7 ideias de conteúdo que NÃO foram pedidas no brief mas se alinham
            com a persona e têm alta probabilidade de viralização.""",
            llm=self.llm,
            verbose=True
        )

    def create_copywriter_task(self, brief: ContentBrief) -> Task:
        """Cria tarefa para o copywriter"""
        return Task(
            description=f"""
            Crie conteúdo para o tópico: {brief.topic}
            Tom: {brief.tonality.value}
            Público: {brief.target_audience}
            Plataformas: {[p.value for p in brief.platforms]}
            Duração: {brief.duration}s
            
            Produza:
            1. Um título impactante
            2. Três hooks de 3-7 segundos cada
            3. Script completo de {brief.duration} segundos
            4. Descrição otimizada para as plataformas
            5. Cinco hashtags relevantes
            6. Call to action persuasivo
            
            Retorne no formato JSON seguindo o schema CopywriterOutput.
            """,
            agent=self.copywriter_agent,
            expected_output="JSON com título, hooks, script, descrição, hashtags e CTA"
        )
    
    def create_editor_task(self, copywriter_output: str) -> Task:
        """Cria tarefa para o editor"""
        return Task(
            description=f"""
            Refine o seguinte script do copywriter:
            {copywriter_output}
            
            Ajuste para:
            - Maior clareza e concisão
            - Remover palavras redundantes
            - Otimizar para fala natural
            - Manter o tom original
            
            Retorne:
            - Versão A: conservadora (mantém estrutura)
            - Versão B: concisa/high-energy (mais dinâmica)
            - Lista de melhorias aplicadas
            
            Formato JSON seguindo EditorOutput schema.
            """,
            agent=self.editor_agent,
            expected_output="JSON com versão A, versão B e lista de melhorias"
        )
    
    def create_publico_task(self, comment: str, brand_persona: str) -> Task:
        """Cria tarefa para resposta ao público"""
        return Task(
            description=f"""
            Responda ao seguinte comentário/DM:
            "{comment}"
            
            Persona da marca: {brand_persona}
            
            Regras:
            1. Nunca prometer serviços específicos
            2. Ser educado e prestativo
            3. Encaminhar reclamações para suporte quando necessário
            4. Manter tom jovem e descontraído
            
            Gere resposta principal e follow-up se necessário.
            Formato JSON seguindo PublicoOutput schema.
            """,
            agent=self.publico_agent,
            expected_output="JSON com resposta, follow-up opcional e flag de escalação"
        )
    
    def create_imagens_task(self, script: str, platform: Platform) -> Task:
        """Cria tarefa para geração de prompts de imagem"""
        return Task(
            description=f"""
            Baseado no script: {script}
            Plataforma: {platform.value}
            
            Crie:
            1. Três prompts detalhados para Stable Diffusion/Midjourney
            2. Três recomendações de composição (close-up, paleta, foco)
            3. Instruções para upscaling/crop para thumbnail
            4. Paleta de cores sugerida
            
            Considere o formato e proporções da plataforma {platform.value}.
            Formato JSON seguindo ImagensOutput schema.
            """,
            agent=self.imagens_agent,
            expected_output="JSON com prompts, recomendações e paleta de cores"
        )
    
    def create_producao_task(self, script: str, platform: Platform) -> Task:
        """Cria tarefa para sugestões de produção"""
        return Task(
            description=f"""
            Para o script: {script}
            Plataforma: {platform.value}
            
            Sugira:
            1. Cinco planos de filmagem (close, meio, geral, etc.)
            2. Backgrounds adequados (real/virtual)
            3. Sugestões de iluminação
            4. Seis falas curtas para o apresentador
            5. Ritmo de edição (especialmente para TikTok: cortes de 3s)
            
            Formato JSON seguindo ProducaoOutput schema.
            """,
            agent=self.producao_agent,
            expected_output="JSON com planos, backgrounds, iluminação e falas"
        )
    
    def create_conteudo_task(self, brief: ContentBrief) -> Task:
        """Cria tarefa para ideias de conteúdo"""
        return Task(
            description=f"""
            Baseado no contexto:
            Tópico original: {brief.topic}
            Público: {brief.target_audience}
            Tom: {brief.tonality.value}
            
            Gere 7 ideias de conteúdo que NÃO foram pedidas diretamente no brief
            mas se alinham com a persona e tendências atuais.
            
            Priorize formatos com alta probabilidade de viralização.
            Para cada ideia inclua:
            - Título atrativo
            - Conceito resumido
            - Potencial viral (0-1)
            - Plataformas mais adequadas
            
            Formato JSON seguindo ConteudoOutput schema.
            """,
            agent=self.conteudo_agent,
            expected_output="JSON com 7 ideias criativas e análise de potencial viral"
        )

class ContentCreationCrew:
    """Crew principal que orquestra todos os agentes"""
    
    def __init__(self, agents: ContentCreationAgents):
        self.agents = agents
    
    def process_brief(self, brief: ContentBrief) -> ContentPackage:
        """Processa um brief completo usando todos os agentes necessários"""
        
        task_id = str(uuid.uuid4())
        
        # cria as tarefas principais
        tasks = []
        
        # tarefa do copywriter (sempre necessária)
        copywriter_task = self.agents.create_copywriter_task(brief)
        tasks.append(copywriter_task)
        
        # tarefa de ideias criativas (sempre executada)
        conteudo_task = self.agents.create_conteudo_task(brief)
        tasks.append(conteudo_task)
        
        # tarefas para cada plataforma
        for platform in brief.platforms:
            # prompts de imagem por plataforma
            imagens_task = self.agents.create_imagens_task("", platform)  # será preenchido após copywriter
            tasks.append(imagens_task)
            
            # sugestões de produção por plataforma  
            producao_task = self.agents.create_producao_task("", platform)  # será preenchido após copywriter
            tasks.append(producao_task)
        
        # cria o crew com as tarefas
        crew = Crew(
            agents=[
                self.agents.copywriter_agent,
                self.agents.editor_agent,
                self.agents.imagens_agent,
                self.agents.producao_agent,
                self.agents.conteudo_agent
            ],
            tasks=tasks,
            verbose=True
        )
        
        # executa o crew
        try:
            results = crew.kickoff()
            
            # processa os resultados e monta o pacote final
            package = ContentPackage(
                brief=brief,
                task_id=task_id,
                created_at=datetime.now().isoformat(),
                status="completed"
            )
            
            # aqui você processaria os results e preencheria os campos específicos
            # por simplicidade, deixando como None por enquanto
            # em implementação real, faria parsing dos JSONs retornados
            
            return package
            
        except Exception as e:
            # retorna pacote com erro
            return ContentPackage(
                brief=brief,
                task_id=task_id,
                created_at=datetime.now().isoformat(),
                status=f"error: {str(e)}"
            )
    
    def respond_to_public(self, comment: str, brand_persona: str) -> PublicoOutput:
        """Responde a comentário/DM do público"""
        
        task = self.agents.create_publico_task(comment, brand_persona)
        
        crew = Crew(
            agents=[self.agents.publico_agent],
            tasks=[task],
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            # aqui faria parsing do JSON retornado
            # por simplicidade, retornando estrutura básica
            return PublicoOutput(
                response="Obrigado pelo seu comentário! Vamos analisar sua sugestão.",
                follow_up=None,
                escalate_to_support=False
            )
        except Exception as e:
            return PublicoOutput(
                response="Desculpe, tivemos um problema técnico. Tente novamente em alguns minutos.",
                follow_up="Se o problema persistir, entre em contato com nosso suporte.",
                escalate_to_support=True
            )