# backend/main.py - Entry point for the Custom Logic AI Assistant backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.llm_config import get_llm
from backend.mytools.categorize_prompt import create_categorize_prompt_tool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    prompt: str

@app.post("/analyze")
def analyze(req: AnalyzeRequest):

    llm = get_llm()
    categorize_prompt = create_categorize_prompt_tool(llm)

    result = categorize_prompt({
        "prompt": req.prompt
    })

    techniques = []
    confidence = None

    #  Case 1: dict output
    if isinstance(result, dict):
        categorization = result.get("categorization", {})
        techniques = categorization.get("techniques", [])
        confidence = categorization.get("confidence")

    # Case 2: object output (older version)
    else:
        techniques = result.categorization.techniques
        confidence = result.categorization.confidence

    return {
        "intent": "workflow_automation",
        "techniques": techniques,
        "confidence": confidence,
        "workflow": None,
        "explanation": "Prompt categorized successfully"
    }




















# from llm_config import get_llm
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool

# llm = get_llm()
# categorize_tool = create_categorize_prompt_tool(llm)

# result = categorize_tool({
#     "prompt": "Create an n8n form with a lead generation form I can embed on my website homepage. Build an automation that processes form submissions, uses AI to qualify the lead, sends data to an n8n data table. For high-score leads, it should also email them to offer to schedule a 15-min call in a free slot in my calendar."
# })

# print(result)
