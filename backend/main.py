# backend/main.py: govind  - Entry point for the Custom Logic AI Assistant backend API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.llm_config import get_llm
from backend.mytools.categorize_prompt import create_categorize_prompt_tool
from backend.mytools.find_best_practice import create_get_best_practices_tool
from backend.mytypes.technique_normalizer import normalize_techniques


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

    # 1️ Categorization
    categorize_tool = create_categorize_prompt_tool(llm)
    categorize_result = categorize_tool({"prompt": req.prompt})
    categorization = categorize_result.get("data", {}).get("categorization", {})

    raw_techniques = categorization.get("techniques", [])
    print("Raw Techniques:", raw_techniques)
    result = categorize_result

    # Defensive extraction
    if not isinstance(result, dict):
        return {
            "success": False,
            "message": "Unexpected tool response format",
            "data": None
        }

    data = result.get("data", {})
    categorization = data.get("categorization", {})

    # techniques = categorization.get("techniques", [])
    confidence = categorization.get("confidence")
    # print("Confidence:", confidence)

    # 2️ Normalize techniques
    normalized_techniques = normalize_techniques(raw_techniques)
    print("Normalized Techniques:", normalized_techniques)
    # 3️ Best Practices
    best_practice_tool_data = create_get_best_practices_tool()
    best_practice_tool = best_practice_tool_data.get("tool")

    best_practices_result = {}
    if best_practice_tool and normalized_techniques:
        #  invoke with dictionary containing 'techniques'
        best_practices_result = best_practice_tool.invoke({
            "techniques": normalized_techniques
        })

    data = best_practices_result.get("data", {})
    # print("Best Practices Result Data:", data)

    if isinstance(data, dict):
         technique_categories = data.get("message", "")
    elif isinstance(data, str):
        technique_categories = data
    else:
       technique_categories = ""

    # 4️ Response
    return {
        "success": True,
        "message": "Prompt categorized successfully",
        "data": {
            "categorization": {
                "techniques": [t.value for t in normalized_techniques],
                "confidence": confidence
            },
            "techniqueCategories": technique_categories
        }
    }

# # -----------------------------
# # /chat ENDPOINT (MULTI-TURN REFINEMENT)
# # -----------------------------

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ChatSession:
#     def __init__(self):
#         self.history = []


# SESSIONS: Dict[str, ChatSession] = {}


# @app.post("/chat")
# def chat(req: ChatRequest):

#     # Handle DONE button
#     if req.message == "__FINALIZE__":
#         req.message = "done"

#     # Create session if needed
#     if req.session_id not in SESSIONS:
#         SESSIONS[req.session_id] = ChatSession()

#     session = SESSIONS[req.session_id]

#     # Process user input via multi-turn engine
#     result = process_user_prompt(req.message, session.history)

#     # -------------------------------------------------------
#     # FINALIZATION FLOW
#     # -------------------------------------------------------
#     if result.get("finalized"):

#         final_intent = result["clean_prompt"]

#         # Automatically call /analyze API
#         import requests
#         analysis = requests.post(
#             "http://localhost:8000/analyze",
#             json={"prompt": final_intent}
#         ).json()

#         # Remove session
#         del SESSIONS[req.session_id]

#         # Return both final intent and analysis
#         return {
#             "finalized": True,
#             "final_intent": final_intent,
#             "analysis": analysis
#         }

#     # -------------------------------------------------------
#     # CLARIFICATION NEEDED
#     # -------------------------------------------------------
#     if result.get("stop"):
#         return {
#             "finalized": False,
#             "response": result["reply"]
#         }

#     # -------------------------------------------------------
#     # NORMAL CONTINUATION
#     # -------------------------------------------------------
#     return {
#         "finalized": False,
#         "response": result["clean_prompt"]
#     }






# #main.py
 
# # backend/main.py - Entry point for the Custom Logic AI Assistant backend API
 
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from backend.llm_config import get_llm
# from backend.llm import process_user_prompt
# from typing import Dict
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool
# from backend.mytools.find_best_practice import create_get_best_practices_tool
 
 
# app = FastAPI()
 
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
 
# class AnalyzeRequest(BaseModel):
#     prompt: str
# @app.post("/analyze")
# def analyze(req: AnalyzeRequest):
#     llm = get_llm()
#     categorize_prompt = create_categorize_prompt_tool(llm)
 
#     result = categorize_prompt({"prompt": req.prompt})
 
#     # Defensive extraction
#     if not isinstance(result, dict):
#         return {
#             "success": False,
#             "message": "Unexpected tool response format",
#             "data": None
#         }
 
#     data = result.get("data", {})
#     categorization = data.get("categorization", {})
 
#     techniques = categorization.get("techniques", [])
#     confidence = categorization.get("confidence")


#     # Find best practices for identified techniques
#     # 3. Fetch Best Practices --------
#     best_practices_tool_data = create_get_best_practices_tool()
#     best_practices_tool = best_practices_tool_data.get("tool")

#     if best_practices_tool:
#         best_practice_result = best_practices_tool({"techniques": techniques}, config={})
#     else:
#         best_practice_result = {"message": "Best practices tool unavailable", "data": {}}
  

#     return {
#         "success": True,
#         "message": result.get(
#             "message",
#             "Prompt categorized successfully"
#         ),
#         "data": {
#             "categorization": {
#                 "techniques": techniques,
#                 "confidence": confidence
#             },
#             "techniqueCategories": data.get("techniqueCategories", [])
#         },
#          "bestPractices": best_practice_result
#     }
 
 
# # -----------------------------
# # /chat ENDPOINT (MULTI-TURN REFINEMENT)
# # -----------------------------
 
# class ChatRequest(BaseModel):
#     session_id: str
#     message: str
 
 
# class ChatSession:
#     def __init__(self):
#         self.history = []
 
 
# SESSIONS: Dict[str, ChatSession] = {}
 
 
# @app.post("/chat")
# def chat(req: ChatRequest):
 
#     # Handle DONE button
#     if req.message == "__FINALIZE__":
#         req.message = "done"
 
#     # Create session if needed
#     if req.session_id not in SESSIONS:
#         SESSIONS[req.session_id] = ChatSession()
 
#     session = SESSIONS[req.session_id]
 
#     # Process user input via multi-turn engine
#     result = process_user_prompt(req.message, session.history)
 
#     # -------------------------------------------------------
#     # FINALIZATION FLOW
#     # -------------------------------------------------------
#     if result.get("finalized"):
 
#         final_intent = result["clean_prompt"]
 
#         # Automatically call /analyze API
#         import requests
#         analysis = requests.post(
#             "http://localhost:8000/analyze",
#             json={"prompt": final_intent}
#         ).json()
 
#         # Remove session
#         del SESSIONS[req.session_id]
 
#         # Return both final intent and analysis
#         return {
#             "finalized": True,
#             "final_intent": final_intent,
#             "analysis": analysis
#         }
 
#     # -------------------------------------------------------
#     # CLARIFICATION NEEDED
#     # -------------------------------------------------------
#     if result.get("stop"):
#         return {
#             "finalized": False,
#             "response": result["reply"]
#         }
 
#     # -------------------------------------------------------
#     # NORMAL CONTINUATION
#     # -------------------------------------------------------
#     return {
#         "finalized": False,
#         "response": result["clean_prompt"]
#     }
 
 
 


 




# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Dict
# import requests

# from backend.llm_config import get_llm
# from backend.llm import process_user_prompt
# from backend.mytools.categorize_prompt import create_categorize_prompt_tool
# from backend.mytools.find_best_practice import create_get_best_practices_tool


# # -------------------------------------------------
# # APP SETUP
# # -------------------------------------------------

# app = FastAPI(title="Custom Logic AI Assistant")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # -------------------------------------------------
# # REQUEST MODELS
# # -------------------------------------------------

# class AnalyzeRequest(BaseModel):
#     prompt: str


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ChatSession:
#     def __init__(self):
#         self.history = []


# SESSIONS: Dict[str, ChatSession] = {}


# # ANALYZE ENDPOINT


# @app.post("/analyze")
# def analyze(req: AnalyzeRequest):
#     try:
#         # 1. Init LLM
#         llm = get_llm()

#         # 2. Categorize prompt
#         categorize_tool = create_categorize_prompt_tool(llm)
#         categorize_result = categorize_tool({"prompt": req.prompt}) 

#         print("Categorize Result:", categorize_result)

#         if not isinstance(categorize_result, dict):
#             return {
#                 "success": False,
#                 "error": "Invalid categorization response",
#             }

#         categorization = categorize_result.get("data", {}).get("categorization", {})
#         techniques = categorization.get("techniques", [])
#         confidence = categorization.get("confidence")

#         # 3. Best practices
#         best_practices_tool_data = create_get_best_practices_tool()
#         best_practices_tool = best_practices_tool_data.get("tool")

#         if best_practices_tool and techniques:
#             try:
#                 best_practices_result = best_practices_tool(
#                     {"techniques": techniques},
#                     config={}
#                 )
#             except Exception as e:
#                 best_practices_result = {
#                     "success": False,
#                     "error": str(e)
#                 }
#         else:
#             best_practices_result = {
#                 "success": False,
#                 "message": "No techniques or tool unavailable"
#             }

#         return {
#             "success": True,
#             "data": {
#                 "prompt": req.prompt,
#                 "categorization": {
#                     "techniques": techniques,
#                     "confidence": confidence,
#                 },
#                 "bestPractices": best_practices_result
#             }
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "type": type(e).__name__
#         }


# # -------------------------------------------------
# # CHAT ENDPOINT
# # -------------------------------------------------

# @app.post("/chat")
# def chat(req: ChatRequest):
#     try:
#         if req.message == "__FINALIZE__":
#             req.message = "done"

#         if req.session_id not in SESSIONS:
#             SESSIONS[req.session_id] = ChatSession()

#         session = SESSIONS[req.session_id]
#         result = process_user_prompt(req.message, session.history)

#         # -------- FINALIZED --------
#         if result.get("finalized"):
#             final_intent = result["clean_prompt"]

#             try:
#                 response = requests.post(
#                     "http://localhost:8000/analyze",
#                     json={"prompt": final_intent},
#                     timeout=30
#                 )
#                 analysis = response.json()
#             except Exception as e:
#                 analysis = {
#                     "success": False,
#                     "error": f"Analyze call failed: {str(e)}"
#                 }

#             del SESSIONS[req.session_id]

#             return {
#                 "finalized": True,
#                 "final_intent": final_intent,
#                 "analysis": analysis
#             }

#         # -------- CLARIFICATION --------
#         if result.get("stop"):
#             return {
#                 "finalized": False,
#                 "response": result["reply"]
#             }

#         # -------- CONTINUE --------
#         return {
#             "finalized": False,
#             "response": result["clean_prompt"]
#         }

#     except Exception as e:
#         return {
#             "finalized": False,
#             "error": str(e)
#         }
