"""
Enums for Progress Observability Instrumentation

Provides granular control over AI agent tracing.
"""

from enum import Enum
from traceloop.sdk.instruments import Instruments


class ObservabilityInstruments(Enum):
    """Progress Observability instruments enum that maps to Traceloop instruments"""
    # LLM Providers
    OPENAI = Instruments.OPENAI
    ANTHROPIC = Instruments.ANTHROPIC
    COHERE = Instruments.COHERE
    BEDROCK = Instruments.BEDROCK
    VERTEXAI = Instruments.VERTEXAI
    SAGEMAKER = Instruments.SAGEMAKER
    OLLAMA = Instruments.OLLAMA
    GROQ = Instruments.GROQ
    MISTRAL = Instruments.MISTRAL
    TOGETHER = Instruments.TOGETHER
    REPLICATE = Instruments.REPLICATE
    ALEPHALPHA = Instruments.ALEPHALPHA
    GOOGLE_GENERATIVEAI = Instruments.GOOGLE_GENERATIVEAI
    TRANSFORMERS = Instruments.TRANSFORMERS
    WATSONX = Instruments.WATSONX
    
    # Agent and Chain Frameworks
    LANGCHAIN = Instruments.LANGCHAIN
    LLAMA_INDEX = Instruments.LLAMA_INDEX
    CREW = Instruments.CREW
    HAYSTACK = Instruments.HAYSTACK
    OPENAI_AGENTS = Instruments.OPENAI_AGENTS
    MCP = Instruments.MCP
    
    # Vector Databases
    PINECONE = Instruments.PINECONE
    CHROMA = Instruments.CHROMA
    WEAVIATE = Instruments.WEAVIATE
    QDRANT = Instruments.QDRANT
    MILVUS = Instruments.MILVUS
    LANCEDB = Instruments.LANCEDB
    MARQO = Instruments.MARQO
    REDIS = Instruments.REDIS
    PYMYSQL = Instruments.PYMYSQL
    
    # Tools and Infrastructure
    REQUESTS = Instruments.REQUESTS
    URLLIB3 = Instruments.URLLIB3
