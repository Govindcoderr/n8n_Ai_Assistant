# backend/main.py - Entry point for the Custom Logic AI Assistant backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.llm_config import get_llm
from backend.llm import process_user_prompt
from typing import Dict
from backend.mytools.categorize_prompt import create_categorize_prompt_tool
from backend.mytools.find_best_practice import create_get_best_practices_tool

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
     
    findbest = create_get_best_practices_tool(result)

    # Defensive extraction
    if not isinstance(findbest, dict):
        return {
            "success": False,
            "message": "Unexpected tool response format",
            "data": None
        }

    data = findbest.get("data", {})
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




















# from llm_config import get_llm
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool

# llm = get_llm()
# categorize_tool = create_categorize_prompt_tool(llm)

# result = categorize_tool({
#     "prompt": "Create an n8n form with a lead generation form I can embed on my website homepage. Build an automation that processes form submissions, uses AI to qualify the lead, sends data to an n8n data table. For high-score leads, it should also email them to offer to schedule a 15-min call in a free slot in my calendar."
# })

# print(result)






# # backend/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# from backend.llm_config import get_llm
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool
# from backend.mytools.find_best_practice import create_get_best_practices_tool

# app = FastAPI(title="Custom Logic AI Assistant")

# # ---------------- CORS ----------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------- Request Model ----------------
# class AnalyzeRequest(BaseModel):
#     prompt: str

# # ---------------- API ----------------
# @app.post("/analyze")
# def analyze(req: AnalyzeRequest):
#     """
#     Analyze user prompt:
#     1. Categorize prompt
#     2. Fetch best practices
#     3. Return preview-friendly response
#     """

#     # -------- 1. Initialize LLM --------
#     llm = get_llm()

#     # -------- 2. Categorize Prompt --------
#     categorize_tool = create_categorize_prompt_tool(llm)

#     categorize_result = categorize_tool({
#         "prompt": req.prompt
#     })

#     if not categorize_result.get("success"):
#         return categorize_result

#     categorization = categorize_result["data"]["categorization"]
#     techniques = categorization.get("techniques", [])

#     # -------- 3. Fetch Best Practices --------
#     best_practice_tool_data = create_get_best_practices_tool()
#     best_practice_tool = best_practice_tool_data["tool"]

#     best_practice_result = best_practice_tool(
#         {
#             "techniques": techniques
#         },
#         config={}
#     )

#     # -------- 4. Response for Frontend --------
#     return {
#         "success": True,
#         "message": "Prompt analyzed successfully",
#         "data": {
#             "prompt": req.prompt,

#             "categorization": {
#                 "techniques": techniques,
#                 "confidence": categorization.get("confidence"),
#                 "techniqueCategories": categorization.get("techniqueCategories", [])
#             },

#             "bestPractices": {
#                 "preview": best_practice_result.get("message"),
#                 "raw": best_practice_result
#             }
#         }
#     }
