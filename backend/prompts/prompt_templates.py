from langchain.prompts import PromptTemplate
from backend.mytypes.categorization import TechniqueDescription

EXAMPLE_PROMPTS = """
- Monitor social channels → monitoring, chatbot, content_generation
- Scrape competitor pricing weekly → scheduling, scraping_and_research, data_analysis
- Process uploaded PDF contracts → document_processing, data_extraction, enrichment
"""

def build_prompt_template() -> PromptTemplate:
    technique_list = "\n".join(
        f"- {k}: {v}" for k, v in TechniqueDescription.items()
    )

    template = f"""
Analyze the user prompt and identify the workflow techniques required.

User Prompt:
{{user_prompt}}

Available Techniques:
{technique_list}

Examples:
{EXAMPLE_PROMPTS}

Rules:
- Select max 5 techniques
- Only select if confident
- Return JSON:
{{"techniques": [], "confidence": 0.0}}
"""

    return PromptTemplate(
        input_variables=["user_prompt"],
        template=template,
    )
