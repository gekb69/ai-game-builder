"""
AI Tool Integrations
LangChain, LlamaIndex, Vector DBs, LLM Providers
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from langchain.llms import OpenAI, Anthropic, HuggingFaceHub
from langchain.vectorstores import Weaviate, Qdrant, FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.agents import initialize_agent, Tool
from llama_index import (
    GPTVectorStoreIndex,
    SimpleDirectoryReader,
    LLMPredictor,
    ServiceContext
)
from llama_index.vector_stores import WeaviateVectorStore
import weaviate
from qdrant_client import QdrantClient

class LangChainManager:
    """Manages LangChain integrations"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("LangChainManager")
        self.llm = None
        self.vector_store = None
        self.agent = None

    async def initialize(self):
        """Initialize LangChain components"""
        self.logger.info("🔗 Initializing LangChain...")

        # Initialize LLM
        provider = self.config.langchain.model_provider
        if provider == "openai":
            self.llm = OpenAI(
                api_key=self.config.llm_providers.openai.api_key,
                model=self.config.llm_providers.openai.model,
                max_tokens=self.config.langchain.max_tokens,
                temperature=self.config.langchain.temperature
            )

        # Initialize vector store
        vector_type = self.config.langchain.vector_store
        if vector_type == "weaviate":
            client = weaviate.Client(
                url=self.config.vector_db.weaviate.url,
                auth_client_secret=weaviate.auth.AuthApiKey(
                    self.config.vector_db.weaviate.api_key
                ) if self.config.vector_db.weaviate.api_key else None
            )
            self.vector_store = Weaviate(client, "Document", "content")

        elif vector_type == "qdrant":
            qdrant_client = QdrantClient(
                url=self.config.vector_db.qdrant.url,
                api_key=self.config.vector_db.qdrant.api_key
            )
            embeddings = HuggingFaceEmbeddings(
                model_name=self.config.llama_index.embedding_model
            )
            self.vector_store = Qdrant(qdrant_client, "documents", embeddings)

        self.logger.info("✅ LangChain initialized")

    async def create_agent(self, tools: List[Tool]):
        """Create LangChain agent"""
        self.agent = initialize_agent(
            tools,
            self.llm,
            agent="zero-shot-react-description",
            verbose=True
        )
        return self.agent

    async def query_vector_store(self, query: str, k: int = 5) -> List[Dict]:
        """Query vector store"""
        if not self.vector_store:
            return []

        return self.vector_store.similarity_search(query, k=k)

class LlamaIndexManager:
    """Manages LlamaIndex components"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("LlamaIndexManager")
        self.index = None
        self.service_context = None

    async def initialize(self):
        """Initialize LlamaIndex"""
        self.logger.info("📚 Initializing LlamaIndex...")

        # Setup LLM predictor
        llm_predictor = LLMPredictor(
            llm=OpenAI(
                api_key=self.config.llm_providers.openai.api_key,
                model=self.config.llm_providers.openai.model
            )
        )

        # Setup service context
        self.service_context = ServiceContext.from_defaults(
            llm_predictor=llm_predictor
        )

        # Initialize vector store if configured
        if self.config.vector_db.weaviate.enabled:
            vector_store = WeaviateVectorStore(
                weaviate_client=weaviate.Client(self.config.vector_db.weaviate.url),
                index_name="LlamaIndex"
            )
            self.index = GPTVectorStoreIndex(
                vector_store=vector_store,
                service_context=self.service_context
            )

        self.logger.info("✅ LlamaIndex initialized")

    async def build_index_from_documents(self, documents_path: str):
        """Build index from documents"""
        if not self.service_context:
            await self.initialize()

        documents = SimpleDirectoryReader(documents_path).load_data()
        self.index = GPTVectorStoreIndex.from_documents(
            documents,
            service_context=self.service_context
        )

        return self.index

    async def query_index(self, query: str) -> str:
        """Query the index"""
        if not self.index:
            return "Index not initialized"

        query_engine = self.index.as_query_engine(
            service_context=self.service_context
        )

        response = query_engine.query(query)
        return str(response)

class VectorDBManager:
    """Manages vector database operations"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("VectorDBManager")
        self.weaviate_client = None
        self.qdrant_client = None
        self.faiss_index = None
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=self.config.llama_index.embedding_model
        )

    async def initialize(self):
        """Initialize all vector DBs"""
        self.logger.info("🗄️ Initializing Vector DBs...")

        # Weaviate
        if self.config.vector_db.weaviate.enabled:
            self.weaviate_client = weaviate.Client(
                url=self.config.vector_db.weaviate.url,
                additional_headers={
                    "X-OpenAI-Api-Key": self.config.llm_providers.openai.api_key
                }
            )
            await self._create_weaviate_schema()

        # Qdrant
        if self.config.vector_db.qdrant.enabled:
            self.qdrant_client = QdrantClient(
                url=self.config.vector_db.qdrant.url,
                api_key=self.config.vector_db.qdrant.api_key
            )

        self.logger.info("✅ Vector DBs initialized")

    async def _create_weaviate_schema(self):
        """Create Weaviate schema"""
        if not self.weaviate_client:
            return

        schema_config = {
            "class": "Document",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "modelVersion": "002",
                    "type": "text"
                }
            },
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                },
                {
                    "name": "source",
                    "dataType": ["string"],
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True
                        }
                    }
                }
            ]
        }

        try:
            self.weaviate_client.schema.create_class(schema_config)
        except Exception as e:
            self.logger.debug(f"Weaviate schema may exist: {e}")

    async def store_document(self, content: str, metadata: Dict):
        """Store document in vector DBs"""
        # Store in Weaviate
        if self.weaviate_client:
            self.weaviate_client.data_object.create({
                "content": content,
                "source": metadata.get("source", "unknown"),
                "timestamp": metadata.get("timestamp")
            }, "Document")

        # Store in Qdrant
        if self.qdrant_client:
            self.qdrant_client.upsert(
                collection_name="documents",
                points=[
                    {
                        "id": metadata.get("id", content[:20]),
                        "payload": {
                            "content": content,
                            "source": metadata.get("source", "unknown"),
                        },
                        "vector": self.embedding_function.embed_query(content),
                    }
                ],
            )

    async def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """Search similar documents"""
        results = []

        if self.weaviate_client:
            response = (
                self.weaviate_client.query
                .get("Document", ["content", "source"])
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .do()
            )

            results = response.get("data", {}).get("Get", {}).get("Document", [])

        if self.qdrant_client:
            hits = self.qdrant_client.search(
                collection_name="documents",
                query_vector=self.embedding_function.embed_query(query),
                limit=limit,
            )
            for hit in hits:
                results.append(hit.payload)

        return results
