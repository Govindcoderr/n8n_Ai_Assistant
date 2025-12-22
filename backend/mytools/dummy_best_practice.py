"""
Dummy Best Practice Tool
Used to validate node-generation and selection logic.
"""

def dummy_best_practice():
    """
    BEST PRACTICE: YouTube Chapter Automation Workflow

    Backend Nodes:
    - YouTube Get a Video
    - YouTube Captions
    - AI Agent
    - HTTP Request

    Frontend Nodes:
    - Chat Trigger
    - Respond to Chat

    Techniques:
    - API Fetching
    - Transcript Extraction
    - AI Semantic Analysis
    - Metadata Enrichment
    - Idempotent Updates

    Guidelines:
    - Always fetch video metadata first
    - Extract captions before AI analysis
    - Use AI Agent to detect topic changes
    - Append chapters, do not overwrite description
    """

    return {
        "toolName": "Dummy YouTube Best Practice",
        "displayTitle": "YouTube Chapter Generation",
        "tool": lambda: dummy_best_practice
    }
