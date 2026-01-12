class NodeConnectionTypes:
    # Core
    Main = "main"
    Action = "action"
    Trigger = "trigger"

    # AI
    AiLanguageModel = "ai_languageModel"
    AiTool = "ai_tool"
    AiMemory = "ai_memory"
    AiEmbedding = "ai_embedding"
    AiVectorStore = "ai_vectorStore"
    AiDocument = "ai_document"
    AiTextSplitter = "ai_textSplitter"
    

    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.Main,
            cls.Action,
            cls.Trigger,
            cls.AiLanguageModel,
            cls.AiTool,
            cls.AiMemory,
            cls.AiEmbedding,
            cls.AiVectorStore,
            cls.AiDocument,
            cls.AiTextSplitter,
        ]

    @classmethod
    def is_ai_type(cls, value: str) -> bool:
        return value.startswith("ai_")

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.all()

