Visão geral (objetivo)

Sistema para gerar e publicar conteúdo (TikTok, YouTube, LinkedIn, Facebook, Instagram) com vários agentes especializados e um manager que coordena: geração de ideias, copywriting, revisão, prompts para imagens, suporte a produção de vídeo, e atendimento ao público com identidade específica.

Principais componentes:

Manager (orquestrador) — decide tarefas, prioriza canais, delega aos agentes.

Copywriter — gera títulos, descrições, scripts e CTAs por plataforma.

Editor de texto — valida e refina o texto do copywriter (gramática, tom, concisão).

Agente_para_o_publico — responde comentários/DMs com identidade definida.

Agente_criacao_imagens — gera prompts para Diffusion/Imagem (Stable Diffusion, Midjourney etc).

Agente_auxiliar_producao — dá sugestões técnicas de vídeo: backgrounds, cenas, sequência de cortes, guia de fala.

Agente_de_conteudo — sugere temas e ângulos que o usuário não pediu (prospecção criativa).

Banco de Memória/Contexto (vector DB) — histórico de posts, persona, guidelines, assets.

Runner local (Ollama) — modelo Mistral rodando localmente via Ollama.

LangChain — “colagens” e chains que chamam LLMs, tools, e vetores.

CrewAI (opcional/alternativa) — orquestra multi-agente com flows e observability; útil se quiser “deploy” do crew com API. 
docs.crewai.com
+1

Arquitetura proposta (resumida)

Frontend/UX (painel): kickoff de brief, revisão de outputs, approval.

API Layer (Flask/FastAPI): recebe pedido, guarda brief, chama Manager.

Manager (service): roda a lógica de orquestração (pode ser um fluxo LangChain/async Python ou um CrewAI crew).

Agents: cada agente é um módulo/chain independente que aceita inputs e retorna um objeto JSON padronizado (texto, metadata, assets).

Vector DB: Chroma/FAISS/Weaviate para embeddings + RAG (memória de marca e histórico).

Ollama local: hospeda Mistral (o LLM local). Integra via LangChain Ollama LLM wrapper. 
python.langchain.com
+1

Image generation: serviço separado (local ou cloud) que recebe prompts gerados por Agente_criacao_imagens.

Observability / Logs: traces de cada tarefa (task_id), métricas, rate limits.

Deploy: Docker compose para Ollama + API + CrewAI (se usar).

Fluxo de execução (exemplo de uso)

Usuário submete brief (ex: “vídeo sobre produtividade para devs, 60s, tom humorístico”).

API cria task, chama Manager.

Manager chama em paralelo:

Agente_de_conteúdo → sugere 5 temas / hooks.

Copywriter → gera roteiro curto + descrição por plataforma.

Agente_criacao_imagens → gera 3 prompts de imagem/thumbnail.

Editor_de_texto valida e refina o copy gerado.

Agente_auxiliar_producao sugere plano de filmagem, planos de câmera, falas.

Manager agrega respostas, cria pacotes (script + assets + prompts) e retorna ao painel para revisão.

Após publicação, Agente_para_o_publico usa identidade única para responder comentários/DMs (com regras/macro prompts).

Histórico e feedback vão para o vector DB para melhorar futuras sugestões (RAG).

Padronização de mensagens (JSON)

Cada agente deve retornar um JSON padronizado, por exemplo:

{
  "agent": "copywriter",
  "output": {
    "title": "3 Hacks de Produtividade para Devs",
    "script_short": "Hook: Você sabia que 80%... -> dica 1 -> call to action",
    "description": "Vídeo de 60s sobre...",
    "hashtags": ["#produtividade","#dev"]
  },
  "metadata": {"confidence": 0.88, "tokens_used": 1200}
}

Exemplos práticos de prompts (templates)

Vou dar um template por agente — esses prompts vão direto para o LLM (via LangChain prompt templates).

Manager (system prompt resumido)
Você é o Manager. Recebe um brief, decide quais agentes chamar e com que prioridade. Retorne uma lista de chamadas no formato: [{agent: 'copywriter', input: {...}}, ...]. Seja conciso e priorize versões para TikTok e Instagram Reels.

Copywriter
Sistema: Você é um copywriter de social media, tom: {tonality}, público: {audience}. Produza: 1 título, 3 hooks de 3-7s, script de 45-60s, descrição para plataforma {platform}, 5 hashtags. Respeite o limite de caracteres do platform. Seja persuasivo e direto.

Editor de texto
Sistema: Você é um editor. Recebe o script do Copywriter. Ajuste para clareza, diminuir palavras redundantes, manter tom e otimizar para voz (fala natural). Retorne versão A (conservadora) e versão B (concisa/high-energy).

Agente_para_o_publico
Sistema: Você é a voz oficial da marca 'BRAND X'. Persona: {persona_desc}. Regras: 1) nunca prometer serviços; 2) ser educado; 3) encaminhar reclamações para suporte. Para cada comentário, gere resposta curta e, se necessário, uma mensagem de follow-up.

Agente_criacao_imagens
Sistema: Baseado no script e na plataforma, produza 3 prompts de imagem para Stable Diffusion / Midjourney e 3 recomendações de composição (close-up, color palette, focal point). Inclua instruções para upscaling/crop para thumbnail.

Agente_auxiliar_producao
Sistema: Sugira 5 planos de filmagem (ex: close, meia-distância), backgrounds (real/virtual), sugestões de iluminação e 6 falas curtas para o apresentador. Se for TikTok, sugira cortes para 3 segundos de ritmo.

Agente_de_conteúdo
Sistema: Gere 7 ideias de conteúdo que NÃO foram pedidas diretamente no brief e que se alinham com a persona e tendências atuais (sem buscar web por hora). Priorize formato de alta probabilidade de viralização.