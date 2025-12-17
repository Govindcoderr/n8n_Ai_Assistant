import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm(
    model: str = "openai/gpt-oss-120b",
    temperature: float = 0.2,
):
    """
    Centralized Groq LLM provider.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise EnvironmentError("GROQ_API_KEY is not set")

    return ChatGroq(
        groq_api_key=groq_api_key,
        model=model,
        temperature=temperature,
    )
