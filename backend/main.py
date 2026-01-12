# # backend/main.py: govind  - Entry point for the Custom Logic AI Assistant backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import traceback
import json
import re
from backend.llm_config import get_llm
from backend.mytools.categorize_prompt import create_categorize_prompt_tool
from backend.mytools.find_best_practice import create_get_best_practices_tool
from backend.mytypes.technique_normalizer import normalize_techniques
from backend.llm import process_user_prompt

app = FastAPI()  # Entry point for Custom Logic AI Assistant backend

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
    categorize_tool = create_categorize_prompt_tool(llm)
    categorize_result = categorize_tool({"prompt": req.prompt})

    if not isinstance(categorize_result, dict):
        return {"success": False, "message": "Invalid categorization response", "data": None}

    categorization = categorize_result.get("data", {}).get("categorization", {})
    raw_techniques = categorization.get("techniques", [])
    confidence = categorization.get("confidence")

    normalized_techniques = normalize_techniques(raw_techniques)

    best_practices = ""
    best_practice_tool_data = create_get_best_practices_tool()
    best_practice_tool = best_practice_tool_data.get("tool")

    if best_practice_tool and normalized_techniques:
        bp_result = best_practice_tool.invoke({"techniques": normalized_techniques})
        data = bp_result.get("data")
        if isinstance(data, dict):
            best_practices = data.get("message", "")
        elif isinstance(data, str):
            best_practices = data

    return {
        "success": True,
        "message": "Prompt categorized successfully",
        "data": {
            "categorization": {
                "techniques": [t.value for t in normalized_techniques],
                "confidence": confidence
            },
            "techniqueCategories": best_practices
        }
    }

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatSession:
    def __init__(self):
        self.history = []

SESSIONS: Dict[str, ChatSession] = {}

@app.post("/chat")
def chat(req: ChatRequest):
    """Enhanced chat endpoint with full workflow generation."""
    try:
        if req.message == "__FINALIZE__":
            req.message = "done"

        if req.session_id not in SESSIONS:
            SESSIONS[req.session_id] = ChatSession()

        session = SESSIONS[req.session_id]
        result = process_user_prompt(req.message, session.history)

        if result.get("finalized"):
            final_intent = result["clean_prompt"]
            
            # Generate complete workflow
            workflow_result = generate_workflow(
                GenerateWorkflowRequest(
                    prompt=final_intent,
                    include_n8n_json=True,
                    include_parsed_details=True
                )
            )
            
            # Get analysis
            analysis = None
            try:
                analysis = analyze(AnalyzeRequest(prompt=final_intent))
            except Exception as e:
                print(f"Error getting analysis: {e}")
                analysis = {"success": False, "error": str(e)}
            
            # Clean up session
            if req.session_id in SESSIONS:
                del SESSIONS[req.session_id]
            
            return {
                "finalized": True,
                "final_intent": final_intent,
                "analysis": analysis,
                "workflow": workflow_result.get("workflow") if workflow_result.get("success") else None,
                "n8nWorkflow": workflow_result.get("n8nWorkflow") if workflow_result.get("success") else None,
                "parsedBestPractices": workflow_result.get("parsedBestPractices") if workflow_result.get("success") else None,
                "error": workflow_result.get("error") if not workflow_result.get("success") else None
            }

        if result.get("stop"):
            return {"finalized": False, "response": result["reply"]}

        return {"finalized": False, "response": result["clean_prompt"]}
        
    except Exception as e:
        print(f"Error in /chat: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

