from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from types.categorization import PromptCategorization

PROMPT = """
You are an expert workflow architect.

Categorize the following user request:
"{prompt}"

Return JSON with:
- techniques: array of required techniques
- confidence: number between 0 and 1
"""

def prompt_categorization_chain(llm, prompt: str) -> PromptCategorization:
    template = ChatPromptTemplate.from_template(PROMPT)
    parser = JsonOutputParser()

    chain = template | llm | parser
    result = chain.invoke({"prompt": prompt})

    return PromptCategorization(
        techniques=result.get("techniques", []),
        confidence=result.get("confidence"),
    )
