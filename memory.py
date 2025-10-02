import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
import uuid

from models import ContentPackage, ContentBrief, Platform
from config import ollama_config, logger

class ContentMemoryManager:
    """Gerenciador de memória usando Chroma para RAG e histórico"""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        
        # inicializa embeddings via Ollama
        self.embeddings = OllamaEmbeddings(
            base_url=ollama_config.base_url,
            model=ollama_config.model_name
        )
        
        # configurações do Chroma
        self.chroma_settings = Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        )
        
        # inicializa collections
        self._setup_collections()
        
        # text splitter para documentos grandes
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def _setup_collections(self):
        """Configura as collections do Chroma"""
        try:
            # collection para histórico de conteúdo gerado
            self.content_store = Chroma(
                collection_name="content_history",
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # collection para persona e guidelines da marca
            self.brand_store = Chroma(
                collection_name="brand_knowledge",
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # collection para tendências e insights
            self.trends_store = Chroma(
                collection_name="trends_insights",
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            logger.info(f"✅ Collections Chroma inicializadas em {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Chroma: {e}")
            raise
    
    def store_content_package(self, package: ContentPackage) -> str:
        """Armazena um pacote de conteúdo completo na memória"""
        try:
            # prepara metadados
            metadata = {
                "task_id": package.task_id,
                "created_at": package.created_at,
                "status": package.status,
                "topic": package.brief.topic,
                "tonality": package.brief.tonality.value,
                "audience": package.brief.target_audience,
                "platforms": [p.value for p in package.brief.platforms],
                "duration": package.brief.duration,
                "type": "content_package"
            }
            
            # cria documento principal com o brief
            brief_text = f"""
            Tópico: {package.brief.topic}
            Público: {package.brief.target_audience}
            Tom: {package.brief.tonality.value}
            Plataformas: {', '.join([p.value for p in package.brief.platforms])}
            Duração: {package.brief.duration}s
            Contexto adicional: {package.brief.additional_context or 'Nenhum'}
            """
            
            # adiciona resultados se disponíveis
            content_parts = [brief_text]
            
            if package.copywriter_result:
                content_parts.append(f"Título: {package.copywriter_result.title}")
                content_parts.append(f"Script: {package.copywriter_result.script_short}")
                content_parts.append(f"Descrição: {package.copywriter_result.description}")
                content_parts.append(f"Hashtags: {', '.join(package.copywriter_result.hashtags)}")
            
            if package.content_ideas:
                ideas_text = "Ideias geradas: " + "; ".join([
                    f"{idea.title}: {idea.concept}" 
                    for idea in package.content_ideas.content_ideas
                ])
                content_parts.append(ideas_text)
            
            full_content = "\n\n".join(content_parts)
            
            # divide em chunks se necessário
            chunks = self.text_splitter.split_text(full_content)
            
            # armazena cada chunk
            doc_ids = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_id"] = i
                chunk_metadata["total_chunks"] = len(chunks)
                
                doc_id = f"{package.task_id}_chunk_{i}"
                
                self.content_store.add_texts(
                    texts=[chunk],
                    metadatas=[chunk_metadata],
                    ids=[doc_id]
                )
                doc_ids.append(doc_id)
            
            logger.info(f"📝 Conteúdo armazenado: {package.task_id} ({len(chunks)} chunks)")
            return package.task_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar conteúdo: {e}")
            raise
    
    def store_brand_guideline(self, title: str, content: str, category: str = "guideline") -> str:
        """Armazena guideline ou informação da marca"""
        try:
            doc_id = str(uuid.uuid4())
            
            metadata = {
                "title": title,
                "category": category,
                "created_at": datetime.now().isoformat(),
                "type": "brand_guideline"
            }
            
            self.brand_store.add_texts(
                texts=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"📋 Guideline armazenada: {title}")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar guideline: {e}")
            raise
    
    def store_trend_insight(self, trend: str, description: str, platforms: List[Platform]) -> str:
        """Armazena insight sobre tendência"""
        try:
            doc_id = str(uuid.uuid4())
            
            metadata = {
                "trend": trend,
                "platforms": [p.value for p in platforms],
                "created_at": datetime.now().isoformat(),
                "type": "trend_insight"
            }
            
            content = f"Tendência: {trend}\nDescrição: {description}\nPlataformas: {', '.join([p.value for p in platforms])}"
            
            self.trends_store.add_texts(
                texts=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"📈 Tendência armazenada: {trend}")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar tendência: {e}")
            raise
    
    def search_similar_content(self, query: str, platform: Optional[Platform] = None, limit: int = 5) -> List[Dict]:
        """Busca conteúdo similar para RAG"""
        try:
            # prepara filtros
            where_filter = {"type": "content_package"}
            if platform:
                # nota: Chroma tem limitações com filtros em arrays, então fazemos busca mais ampla
                pass
            
            # busca por similaridade
            results = self.content_store.similarity_search_with_score(
                query=query,
                k=limit,
                filter=where_filter
            )
            
            # formata resultados
            formatted_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score,
                    "relevance": "high" if score < 0.3 else "medium" if score < 0.6 else "low"
                }
                formatted_results.append(result)
            
            logger.info(f"🔍 Busca realizada: '{query}' - {len(formatted_results)} resultados")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def get_brand_context(self, query: str, limit: int = 3) -> List[Dict]:
        """Recupera contexto da marca para RAG"""
        try:
            results = self.brand_store.similarity_search_with_score(
                query=query,
                k=limit
            )
            
            formatted_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar contexto da marca: {e}")
            return []
    
    def get_trending_insights(self, platform: Optional[Platform] = None, limit: int = 5) -> List[Dict]:
        """Recupera insights de tendências"""
        try:
            # busca geral por tendências
            query = f"tendências {platform.value}" if platform else "tendências atuais"
            
            results = self.trends_store.similarity_search_with_score(
                query=query,
                k=limit
            )
            
            formatted_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar tendências: {e}")
            return []
    
    def build_rag_context(self, brief: ContentBrief) -> str:
        """Constrói contexto RAG para um brief"""
        try:
            context_parts = []
            
            # busca conteúdo similar
            similar_content = self.search_similar_content(
                query=f"{brief.topic} {brief.target_audience}",
                platform=brief.platforms[0] if brief.platforms else None,
                limit=3
            )
            
            if similar_content:
                context_parts.append("=== CONTEÚDO SIMILAR ANTERIOR ===")
                for content in similar_content:
                    context_parts.append(f"- {content['content'][:200]}...")
            
            # busca contexto da marca
            brand_context = self.get_brand_context(
                query=f"{brief.topic} {brief.tonality.value}",
                limit=2
            )
            
            if brand_context:
                context_parts.append("\n=== DIRETRIZES DA MARCA ===")
                for context in brand_context:
                    context_parts.append(f"- {context['content']}")
            
            # busca tendências relevantes
            trends = self.get_trending_insights(
                platform=brief.platforms[0] if brief.platforms else None,
                limit=2
            )
            
            if trends:
                context_parts.append("\n=== TENDÊNCIAS ATUAIS ===")
                for trend in trends:
                    context_parts.append(f"- {trend['content']}")
            
            return "\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.error(f"❌ Erro ao construir contexto RAG: {e}")
            return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória"""
        try:
            # conta documentos em cada collection
            content_count = len(self.content_store.get()["ids"])
            brand_count = len(self.brand_store.get()["ids"])
            trends_count = len(self.trends_store.get()["ids"])
            
            return {
                "total_documents": content_count + brand_count + trends_count,
                "content_packages": content_count,
                "brand_guidelines": brand_count,
                "trend_insights": trends_count,
                "persist_directory": self.persist_directory,
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def clear_collection(self, collection_name: str) -> bool:
        """Limpa uma collection específica (usar com cuidado!)"""
        try:
            if collection_name == "content_history":
                self.content_store.delete_collection()
                self.content_store = Chroma(
                    collection_name="content_history",
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
            elif collection_name == "brand_knowledge":
                self.brand_store.delete_collection()
                self.brand_store = Chroma(
                    collection_name="brand_knowledge",
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
            elif collection_name == "trends_insights":
                self.trends_store.delete_collection()
                self.trends_store = Chroma(
                    collection_name="trends_insights",
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
            else:
                return False
            
            logger.info(f"🗑️ Collection '{collection_name}' limpa")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar collection: {e}")
            return False

# instância global
memory_manager = ContentMemoryManager()

def get_memory_manager() -> ContentMemoryManager:
    """Retorna instância do gerenciador de memória"""
    return memory_manager