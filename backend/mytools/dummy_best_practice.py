# backend/mytools/dummy_best_practice.py

"""
Generic Best Practice Tool
Domain-agnostic. Safe for all intents.
"""

def dummy_best_practice():
    """
    BEST PRACTICE: API-Driven Automation

    Principles:
    - The user intent defines the domain
    - Nodes must be directly related to the intent
    - Do not invent nodes
    - If no native node exists, use HTTP Request

    Techniques:
    - REST API integration
    - OAuth / token-based authentication
    - Data transformation
    - Error handling & retries
    """

    return {
        "toolName": "Generic Automation Best Practice",
        "displayTitle": "API Automation",
        "tool": lambda: dummy_best_practice
    }
