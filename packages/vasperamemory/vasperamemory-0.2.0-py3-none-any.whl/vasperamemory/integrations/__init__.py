"""VasperaMemory integrations with popular AI frameworks."""

try:
    from .langchain import VasperaMemoryRetriever, VasperaMemoryChatHistory
except ImportError:
    pass  # LangChain not installed

try:
    from .llamaindex import VasperaMemoryVectorStore
except ImportError:
    pass  # LlamaIndex not installed
