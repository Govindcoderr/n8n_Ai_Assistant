# backend/main.py - Entry point for the Custom Logic AI Assistant backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.llm_config import get_llm
from backend.llm import process_user_prompt
from typing import Dict
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

    result = categorize_prompt({"prompt": req.prompt})

    # Defensive extraction
    if not isinstance(result, dict):
        return {
            "success": False,
            "message": "Unexpected tool response format",
            "data": None
        }

    data = result.get("data", {})
    categorization = data.get("categorization", {})

    techniques = categorization.get("techniques", [])
    confidence = categorization.get("confidence")

    return {
        "success": True,
        "message": result.get(
            "message",
            "Prompt categorized successfully"
        ),
        "data": {
            "categorization": {
                "techniques": techniques,
                "confidence": confidence
            },
            "techniqueCategories": data.get("techniqueCategories", [])
        }
    }



# -----------------------------
# /chat ENDPOINT (MULTI-TURN REFINEMENT)
# -----------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatSession:
    def __init__(self):
        self.history = []


SESSIONS: Dict[str, ChatSession] = {}


@app.post("/chat")
def chat(req: ChatRequest):

    # Handle DONE button
    if req.message == "__FINALIZE__":
        req.message = "done"

    # Create session if needed
    if req.session_id not in SESSIONS:
        SESSIONS[req.session_id] = ChatSession()

    session = SESSIONS[req.session_id]

    # Process user input via multi-turn engine
    result = process_user_prompt(req.message, session.history)

    # -------------------------------------------------------
    # FINALIZATION FLOW
    # -------------------------------------------------------
    if result.get("finalized"):

        final_intent = result["clean_prompt"]

        # Automatically call /analyze API
        import requests
        analysis = requests.post(
            "http://localhost:8000/analyze",
            json={"prompt": final_intent}
        ).json()

        # Remove session
        del SESSIONS[req.session_id]

        # Return both final intent and analysis
        return {
            "finalized": True,
            "final_intent": final_intent,
            "analysis": analysis
        }

    # -------------------------------------------------------
    # CLARIFICATION NEEDED
    # -------------------------------------------------------
    if result.get("stop"):
        return {
            "finalized": False,
            "response": result["reply"]
        }

    # -------------------------------------------------------
    # NORMAL CONTINUATION
    # -------------------------------------------------------
    return {
        "finalized": False,
        "response": result["clean_prompt"]
    }















# from llm_config import get_llm
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool

# llm = get_llm()
# categorize_tool = create_categorize_prompt_tool(llm)

# result = categorize_tool({
#     "prompt": "Create an n8n form with a lead generation form I can embed on my website homepage. Build an automation that processes form submissions, uses AI to qualify the lead, sends data to an n8n data table. For high-score leads, it should also email them to offer to schedule a 15-min call in a free slot in my calendar."
# })

# print(result)
