from backend.n8n_worflow.node_connection_types   import NodeConnectionTypes


# Create this once (can be static, JSON, or DB later).

sample_nodes = [
    {
        "name": "cron",
        "displayName": "Cron",
        "description": "Triggers the workflow at a specific time interval",
        "version": [1],
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "httpRequest",
        "displayName": "HTTP Request",
        "description": "Make HTTP requests",
        "version": [1, 2, 3],
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "openAi",
        "displayName": "OpenAI",
        "description": "Generate text using OpenAI models",
        "version": [1],
        "inputs": [NodeConnectionTypes.AiLanguageModel],
        "outputs": [NodeConnectionTypes.Main],
    },
    # AI LANGUAGE MODELS
    {
        "name": "openai.chat",
        "displayName": "OpenAI Chat Model",
        "description": "Generate text using OpenAI GPT models",
        "version": [1, 2],
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },
    {
        "name": "anthropic.chat",
        "displayName": "Anthropic Claude",
        "description": "Claude LLM for content generation and reasoning",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },
    {
        "name": "google.gemini",
        "displayName": "Google Gemini",
        "description": "Gemini language model by Google",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },
    # AI TOOLS
    {
        "name": "tool.calculator",
        "displayName": "Calculator Tool",
        "description": "Perform math calculations",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiTool],
        "outputs": [NodeConnectionTypes.AiTool],
    },
    {
        "name": "tool.code",
        "displayName": "Code Interpreter",
        "description": "Execute Python/JS code",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiTool],
        "outputs": [NodeConnectionTypes.AiTool],
    },
    {
        "name": "tool.http",
        "displayName": "HTTP Tool",
        "description": "Call external APIs",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiTool],
    },
    # MEMORY
    {
        "name": "memory.buffer",
        "displayName": "Window Buffer Memory",
        "description": "Short-term conversation memory",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiMemory],
        "outputs": [NodeConnectionTypes.AiMemory],
    },
    {
        "name": "memory.summary",
        "displayName": "Conversation Summary Memory",
        "description": "Summarize long conversations",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiMemory],
        "outputs": [NodeConnectionTypes.AiMemory],
    },
    # EMBEDDINGS
    {
        "name": "embedding.openai",
        "displayName": "OpenAI Embeddings",
        "description": "Generate vector embeddings",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiEmbedding],
    },
    {
        "name": "embedding.cohere",
        "displayName": "Cohere Embeddings",
        "description": "Embedding generation using Cohere",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiEmbedding],
    },
    # VECTOR STORES
    {
        "name": "vector.qdrant",
        "displayName": "Qdrant Vector Store",
        "description": "Store and search embeddings",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiVectorStore],
        "outputs": [NodeConnectionTypes.AiVectorStore],
    },
    {
        "name": "vector.faiss",
        "displayName": "FAISS Vector Store",
        "description": "Local vector search using FAISS",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiVectorStore],
        "outputs": [NodeConnectionTypes.AiVectorStore],
    },
    # DOCUMENT LOADERS
    {
        "name": "doc.pdf",
        "displayName": "PDF Loader",
        "description": "Load PDF documents",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiDocument],
    },
    {
        "name": "doc.web",
        "displayName": "Web Page Loader",
        "description": "Load content from URLs",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiDocument],
    },
    # TEXT SPLITTERS
    {
        "name": "splitter.recursive",
        "displayName": "Recursive Text Splitter",
        "description": "Split text into chunks",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiTextSplitter],
        "outputs": [NodeConnectionTypes.AiTextSplitter],
    },
    {
        "name": "splitter.token",
        "displayName": "Token Text Splitter",
        "description": "Split text by tokens",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiTextSplitter],
        "outputs": [NodeConnectionTypes.AiTextSplitter],
    },
    # NOTIFICATION / ACTIONS
    {
        "name": "email.send",
        "displayName": "Send Email",
        "description": "Send emails via SMTP",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "slack.send",
        "displayName": "Send Slack Message",
        "description": "Send message to Slack",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "telegram.send",
        "displayName": "Send Telegram Message",
        "description": "Send Telegram notifications",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    # SCRAPING / RESEARCH

    {
        "name": "http.request",
        "displayName": "HTTP Request",
        "description": "Fetch data from APIs or websites",
        "version": [1, 2],
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "html.extract",
        "displayName": "HTML Extract",
        "description": "Extract data from HTML",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    
    # EMAIL & SMS
    {
        "name": "email.smtp",
        "displayName": "SMTP Email",
        "description": "Send emails using SMTP",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "email.gmail",
        "displayName": "Gmail",
        "description": "Send Gmail emails",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "sms.twilio",
        "displayName": "Twilio SMS",
        "description": "Send SMS using Twilio",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # CHAT APPS
    {
        "name": "slack.trigger",
        "displayName": "Slack Trigger",
        "description": "Trigger workflow from Slack events",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "discord.send",
        "displayName": "Discord Message",
        "description": "Send message to Discord",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "whatsapp.send",
        "displayName": "WhatsApp Message",
        "description": "Send WhatsApp messages",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # PUSH / MOBILE
    {
        "name": "push.firebase",
        "displayName": "Firebase Push",
        "description": "Send push notifications",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "push.onesignal",
        "displayName": "OneSignal Push",
        "description": "Send OneSignal notifications",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    # TRIGGERS
    {
        "name": "trigger.cron",
        "displayName": "Cron Trigger",
        "description": "Run workflow on schedule",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "trigger.webhook",
        "displayName": "Webhook Trigger",
        "description": "Trigger workflow via HTTP webhook",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    # DATA / UTILITIES
    {
        "name": "util.set",
        "displayName": "Set Data",
        "description": "Set or modify JSON data",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "util.if",
        "displayName": "IF Condition",
        "description": "Conditional branching",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "util.merge",
        "displayName": "Merge",
        "description": "Merge multiple data streams",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    # FILES & STORAGE
    {
        "name": "file.read",
        "displayName": "Read File",
        "description": "Read file from disk",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "file.write",
        "displayName": "Write File",
        "description": "Write file to disk",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "storage.s3",
        "displayName": "AWS S3",
        "description": "Upload and download files from S3",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    # DATABASES
    {
        "name": "db.mysql",
        "displayName": "MySQL",
        "description": "Run MySQL queries",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "db.postgres",
        "displayName": "PostgreSQL",
        "description": "Run PostgreSQL queries",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "db.mongo",
        "displayName": "MongoDB",
        "description": "MongoDB operations",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    # AI + TEXT
    {
        "name": "ai.sentiment",
        "displayName": "Sentiment Analysis",
        "description": "Analyze sentiment of text",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiLanguageModel],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "ai.translate",
        "displayName": "Translate Text",
        "description": "Translate text to other languages",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiLanguageModel],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "ai.summarize",
        "displayName": "Summarize Text",
        "description": "Summarize long text",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiLanguageModel],
        "outputs": [NodeConnectionTypes.Main],
    },   
    # MONITORING / OPS
    {
        "name": "ops.healthcheck",
        "displayName": "Health Check",
        "description": "Monitor service health",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "ops.alert",
        "displayName": "Alert Manager",
        "description": "Send alerts on failures",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    # ───────────── TRIGGERS ─────────────
    {
        "name": "trigger.cron",
        "displayName": "Cron Trigger",
        "description": "Run workflow on a schedule",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "trigger.webhook",
        "displayName": "Webhook Trigger",
        "description": "Trigger workflow via HTTP webhook",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "trigger.chat",
        "displayName": "Chat Trigger",
        "description": "Receive chat messages",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ───────────── CORE N8N NODES ─────────────
    {
        "name": "n8n.httpRequest",
        "displayName": "HTTP Request",
        "description": "Make HTTP requests",
        "version": [1, 2, 3],
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "n8n.if",
        "displayName": "IF",
        "description": "Conditional branching",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "n8n.set",
        "displayName": "Set",
        "description": "Set or modify JSON data",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "n8n.merge",
        "displayName": "Merge",
        "description": "Merge multiple data streams",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ───────────── AI AGENT ─────────────
    {
        "name": "langchain.agent",
        "displayName": "AI Agent",
        "description": "Orchestrates tools, memory, and LLM calls",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ───────────── CHAT MODELS ─────────────
    {
        "name": "langchain.lmChatOpenAi",
        "displayName": "OpenAI Chat Model",
        "description": "GPT chat models",
        "version": [1, 2],
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },
    {
        "name": "langchain.lmChatGoogleGemini",
        "displayName": "Google Gemini Chat Model",
        "description": "Gemini multimodal chat model",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },
    {
        "name": "langchain.lmChatAnthropic",
        "displayName": "Anthropic Claude Chat Model",
        "description": "Claude LLM",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },

    # ───────────── AI TOOLS ─────────────
    {
        "name": "langchain.tool.calculator",
        "displayName": "Calculator Tool",
        "description": "Perform math calculations",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiTool],
        "outputs": [NodeConnectionTypes.AiTool],
    },
    {
        "name": "langchain.tool.codeInterpreter",
        "displayName": "Code Interpreter Tool",
        "description": "Execute Python or JS code",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiTool],
        "outputs": [NodeConnectionTypes.AiTool],
    },
    {
        "name": "langchain.tool.http",
        "displayName": "HTTP Tool",
        "description": "Call external APIs",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiTool],
    },

    # ───────────── MEMORY ─────────────
    {
        "name": "langchain.memoryBufferWindow",
        "displayName": "Buffer Window Memory",
        "description": "Short-term conversation memory",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiMemory],
        "outputs": [NodeConnectionTypes.AiMemory],
    },
    {
        "name": "langchain.memorySummary",
        "displayName": "Summary Memory",
        "description": "Summarize long conversations",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiMemory],
        "outputs": [NodeConnectionTypes.AiMemory],
    },

    # ───────────── EMBEDDINGS ─────────────
    {
        "name": "langchain.embeddingOpenAi",
        "displayName": "OpenAI Embeddings",
        "description": "Generate vector embeddings",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiEmbedding],
    },

    # ───────────── VECTOR STORES ─────────────
    {
        "name": "langchain.vectorQdrant",
        "displayName": "Qdrant Vector Store",
        "description": "Store and search embeddings",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiVectorStore],
        "outputs": [NodeConnectionTypes.AiVectorStore],
    },
    {
        "name": "langchain.vectorFaiss",
        "displayName": "FAISS Vector Store",
        "description": "Local vector search",
        "version": 1,
        "inputs": [NodeConnectionTypes.AiVectorStore],
        "outputs": [NodeConnectionTypes.AiVectorStore],
    },

    # ───────────── COMMUNICATION ─────────────
    {
        "name": "n8n.emailSend",
        "displayName": "Send Email",
        "description": "Send email via SMTP or Gmail",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "n8n.slackSend",
        "displayName": "Slack Message",
        "description": "Send Slack messages",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    {
        "name": "n8n.telegramSend",
        "displayName": "Telegram Message",
        "description": "Send Telegram notifications",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
     # ─────────────────────────────
    # DATA INGESTION & PREPARATION
    # ─────────────────────────────

    {
        "name": "n8n.spreadsheetFile",
        "displayName": "Spreadsheet File",
        "description": "Parse CSV or Excel files into JSON",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.filter",
        "displayName": "Filter",
        "description": "Remove items based on conditions (nulls, subsets)",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # DATA TRANSFORMATION & ANALYSIS
    # ─────────────────────────────

    {
        "name": "n8n.code",
        "displayName": "Code",
        "description": "Custom JavaScript for whole-dataset analysis",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.aggregate",
        "displayName": "Aggregate",
        "description": "Group, count, sum, average values by key",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # LARGE DATASET HANDLING
    # ─────────────────────────────

    {
        "name": "n8n.splitInBatches",
        "displayName": "Split In Batches",
        "description": "Process large datasets in chunks to avoid memory issues",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # OUTPUT & REPORTING
    # ─────────────────────────────

    {
        "name": "n8n.html",
        "displayName": "HTML",
        "description": "Generate HTML reports",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.markdown",
        "displayName": "Markdown",
        "description": "Format text as Markdown or HTML",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # STORAGE & HISTORY
    # ─────────────────────────────

    {
        "name": "n8n.googleSheets",
        "displayName": "Google Sheets",
        "description": "Read and write spreadsheet data",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # DATABASES (ANALYSIS HISTORY)
    # ─────────────────────────────

    {
        "name": "n8n.postgres",
        "displayName": "Postgres",
        "description": "Store and query analysis results",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.mySql",
        "displayName": "MySQL",
        "description": "Run MySQL queries",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.mongoDb",
        "displayName": "MongoDB",
        "description": "MongoDB operations",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # AI-POWERED ANALYSIS
    # ─────────────────────────────

    {
        "name": "langchain.agent",
        "displayName": "AI Agent",
        "description": "AI-powered reasoning, analysis, and tool orchestration",
        "version": 1,
        "inputs": [
            NodeConnectionTypes.Main,
            NodeConnectionTypes.AiMemory,
            NodeConnectionTypes.AiTool,
        ],
        "outputs": [NodeConnectionTypes.Main],
    },
     {
        "name": "langchain.openAi",
        "displayName": "OpenAI",
        "description": "Text, image, audio, and video generation using OpenAI (GPT, DALL·E, Sora, TTS)",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "langchain.lmChatXAiGrok",
        "displayName": "xAI Grok Chat Model",
        "description": "Conversational AI using xAI Grok",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },

    {
        "name": "langchain.lmChatGoogleGemini",
        "displayName": "Google Gemini Chat Model",
        "description": "Multimodal chat, image and video generation (Nano Banana, Imagen)",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.AiLanguageModel],
    },

    # ─────────────────────────────
    # IMAGE GENERATION & EDITING
    # ─────────────────────────────

    {
        "name": "langchain.imageGenerate",
        "displayName": "AI Image Generation",
        "description": "Generate images using models like DALL·E, Imagen, Stable Diffusion",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Binary],
    },

    {
        "name": "n8n.editImage",
        "displayName": "Edit Image",
        "description": "Resize, crop, rotate, and convert images",
        "version": 1,
        "inputs": [NodeConnectionTypes.Binary],
        "outputs": [NodeConnectionTypes.Binary],
    },

    # ─────────────────────────────
    # VIDEO GENERATION & PROCESSING
    # ─────────────────────────────

    {
        "name": "langchain.videoGenerate",
        "displayName": "AI Video Generation",
        "description": "Generate videos using Sora, Veo, Runway, Pika",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Binary],
    },

    {
        "name": "n8n.wait",
        "displayName": "Wait",
        "description": "Pause workflow execution for async processing or rate limits",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # AUDIO / VOICE GENERATION
    # ─────────────────────────────

    {
        "name": "langchain.audioGenerate",
        "displayName": "AI Audio Generation",
        "description": "Text-to-speech, voice synthesis, narration",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Binary],
    },

    {
        "name": "integration.elevenLabs",
        "displayName": "ElevenLabs Voice",
        "description": "Natural-sounding AI voice generation (TTS, voice cloning)",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Binary],
    },

    # ─────────────────────────────
    # FORMATTING & CONTENT OUTPUT
    # ─────────────────────────────

    {
        "name": "n8n.markdown",
        "displayName": "Markdown",
        "description": "Format text into Markdown or HTML",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # SOCIAL / MEDIA PUBLISHING
    # ─────────────────────────────

    {
        "name": "n8n.facebookGraphApi",
        "displayName": "Facebook Graph API",
        "description": "Upload videos and images to Facebook and Instagram",
        "version": 1,
        "inputs": [NodeConnectionTypes.Binary],
        "outputs": [NodeConnectionTypes.Main],
    },
      # ─────────────────────────────
    # FILE & BINARY DATA HANDLING
    # ─────────────────────────────

    {
        "name": "n8n.extractFromFile",
        "displayName": "Extract From File",
        "description": "Convert binary CSV, Excel, PDF, or text files into JSON",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.splitOut",
        "displayName": "Split Out",
        "description": "Split arrays into individual items for sequential processing",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # HTML & WEB EXTRACTION
    # ─────────────────────────────

    {
        "name": "n8n.htmlExtract",
        "displayName": "HTML Extract",
        "description": "Extract structured data from HTML using CSS selectors",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # DATA STRUCTURE NORMALIZATION
    # ─────────────────────────────

    {
        "name": "n8n.set",
        "displayName": "Edit Fields (Set)",
        "description": "Normalize, map, and clean JSON structure",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # AI-POWERED EXTRACTION
    # ─────────────────────────────

    {
        "name": "langchain.informationExtractor",
        "displayName": "Information Extractor",
        "description": "Extract structured data from unstructured text using AI",
        "version": 1,
        "inputs": [
            NodeConnectionTypes.Main,
            NodeConnectionTypes.AiLanguageModel,
        ],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "langchain.chainSummarization",
        "displayName": "Summarization Chain",
        "description": "Summarize large text blocks using AI",
        "version": 1,
        "inputs": [
            NodeConnectionTypes.Main,
            NodeConnectionTypes.AiLanguageModel,
        ],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # BINARY-SAFE CODE EXECUTION
    # ─────────────────────────────

    {
        "name": "n8n.code",
        "displayName": "Code",
        "description": "Custom logic for complex transformations (binary-safe if configured)",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
    # ─────────────────────────────
    # FIELD / DATA TRANSFORMATION
    # ─────────────────────────────

    {
        "name": "n8n.set",
        "displayName": "Edit Fields (Set)",
        "description": "Create, modify, rename fields and convert data types",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.if",
        "displayName": "IF",
        "description": "Conditional routing and validation",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [
            NodeConnectionTypes.Main,  # true
            NodeConnectionTypes.Main,  # false
        ],
    },

    {
        "name": "n8n.filter",
        "displayName": "Filter",
        "description": "Filter items based on conditions",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # MERGING & RESTRUCTURING
    # ─────────────────────────────

    {
        "name": "n8n.merge",
        "displayName": "Merge",
        "description": "Merge data streams by key, index, or append",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main, NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.splitOut",
        "displayName": "Split Out",
        "description": "Split array fields into multiple items",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.aggregate",
        "displayName": "Aggregate",
        "description": "Aggregate multiple items into one",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.summarize",
        "displayName": "Summarize",
        "description": "Pivot-style summarization (count, sum, avg, min, max)",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.removeDuplicates",
        "displayName": "Remove Duplicates",
        "description": "Remove duplicate items based on fields",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.sort",
        "displayName": "Sort",
        "description": "Sort items alphabetically or numerically",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.limit",
        "displayName": "Limit",
        "description": "Limit number of items",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # CODE / CUSTOM LOGIC
    # ─────────────────────────────

    {
        "name": "n8n.code",
        "displayName": "Code",
        "description": "Custom JavaScript for complex transformations",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # BATCH & SCALE
    # ─────────────────────────────

    {
        "name": "n8n.splitInBatches",
        "displayName": "Split In Batches",
        "description": "Process large datasets in chunks",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # WORKFLOW ORCHESTRATION
    # ─────────────────────────────

    {
        "name": "n8n.executeWorkflow",
        "displayName": "Execute Workflow",
        "description": "Run a sub-workflow for modular design",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "trigger.error",
        "displayName": "Error Trigger",
        "description": "Catch and handle workflow execution errors",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    # ───────────── DOCUMENT INPUT TRIGGERS ─────────────

    {
     "name": "n8n.gmailTrigger",
     "displayName": "Gmail Trigger",
     "description": "Watch Gmail for new emails with attachments",
     "version": 1,
     "inputs": [],
     "outputs": [NodeConnectionTypes.Main],
    },

    {
     "name": "n8n.emailReadImap",
     "displayName": "Email Read (IMAP)",
     "description": "Fetch emails and attachments via IMAP",
     "version": 1,
     "inputs": [],
     "outputs": [NodeConnectionTypes.Main],
    },
   { 
     "name": "n8n.googleDriveTrigger",
     "displayName": "Google Drive Trigger",
     "description": "Watch Google Drive folders for new files",
     "version": 1,
     "inputs": [],
     "outputs": [NodeConnectionTypes.Main],
    },
    # ─────────────────────────────
    # TRIGGERS (NOTIFICATION-SPECIFIC)
    # ─────────────────────────────

   {
        "name": "n8n.webhook",
        "displayName": "Webhook",
        "description": "Trigger workflow from external events",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.scheduleTrigger",
        "displayName": "Schedule Trigger",
        "description": "Trigger workflow on a schedule (cron-based)",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.emailReadImap",
        "displayName": "Email Trigger (IMAP)",
        "description": "Trigger workflow when new emails arrive",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # NOTIFICATION CHANNELS
    # ─────────────────────────────

    {
        "name": "n8n.slack",
        "displayName": "Slack",
        "description": "Send messages to Slack channels or users",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.telegram",
        "displayName": "Telegram",
        "description": "Send Telegram bot messages",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.twilio",
        "displayName": "WhatsApp",
        "description": "Send SMS or WhatsApp messages via WhatsApp",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # LOGIC & ROUTING
    # ─────────────────────────────

    {
        "name": "n8n.switch",
        "displayName": "Switch",
        "description": "Route workflow based on multiple conditions",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # RATE LIMITING & COOLDOWN
    # ─────────────────────────────

    {
        "name": "n8n.wait",
        "displayName": "Wait",
        "description": "Pause workflow execution for a defined time",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # ERROR HANDLING & OPS
    # ─────────────────────────────

    {
        "name": "n8n.errorTrigger",
        "displayName": "Error Trigger",
        "description": "Catch workflow execution errors",
        "version": 1,
        "inputs": [],
        "outputs": [NodeConnectionTypes.Main],
    },
    
    # ─────────────────────────────
    # MESSAGING INTEGRATIONS (Monitoring-specific)
    # ─────────────────────────────

    {
        "name": "n8n.microsoftTeams",
        "displayName": "Microsoft Teams",
        "description": "Send real-time notifications to Microsoft Teams channels",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.discord",
        "displayName": "Discord",
        "description": "Send real-time notifications to Discord channels",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # SYSTEM / NON-HTTP MONITORING
    # ─────────────────────────────

    {
        "name": "n8n.executeCommand",
        "displayName": "Execute Command",
        "description": "Run system commands or scripts for monitoring purposes",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
     # ─────────────────────────────
    # DATA EXTRACTION / SCRAPING NODES
    # ─────────────────────────────

    {
        "name": "n8n.htmlExtract",
        "displayName": "HTML Extract",
        "description": "Parse HTML and extract data using CSS selectors for web scraping",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.splitOut",
        "displayName": "Split Out",
        "description": "Processes lists of items one by one for sequential operations",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.microsoftExcel",
        "displayName": "Microsoft Excel 365",
        "description": "Stores and retrieves data in Microsoft Excel 365 files",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    {
        "name": "n8n.airtable",
        "displayName": "Airtable",
        "description": "Saves structured data to Airtable database with rich data types and relationships",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },

    # ─────────────────────────────
    # SCRAPING AUTOMATION PROVIDERS
    # ─────────────────────────────

    {
        "name": "n8n.phantombuster",
        "displayName": "Phantombuster",
        "description": "Automated web scraping and data extraction from social networks and websites",
        "version": 1,
        "inputs": [NodeConnectionTypes.Main],
        "outputs": [NodeConnectionTypes.Main],
    },
]
