# import os
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from fastapi.middleware.cors import CORSMiddleware

# from categorizer import PromptCategorizer
# from best_practices import BestPracticesRetriever
# from node_search import NodeSearcher
# from node_ranking import NodeRanker
# from llm_interface import LLMInterface
# from utils import display_workflow_summary

# # Load environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# if not OPENAI_API_KEY:
#     raise ValueError("OpenAI API key not found in .env file. Please set OPENAI_API_KEY.")

# # Initialize modules
# categorizer = PromptCategorizer("data/example_prompts.json")
# best_practices_retriever = BestPracticesRetriever("data/workflow_best_practices.json")
# node_searcher = NodeSearcher("data/nodes_catalog.json")
# node_ranker = NodeRanker(node_searcher.get_all_nodes())
# llm = LLMInterface(OPENAI_API_KEY)

# # FastAPI app
# app = FastAPI(title="Custom Logic AI Assistant API")

# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # allow all origins for simplicity
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Request schema
# class WorkflowRequest(BaseModel):
#     prompt: str

# # Endpoint
# @app.post("/generate_workflow")
# def generate_workflow(request: WorkflowRequest):
#     try:
#         user_prompt = request.prompt

#         # Step 1: Categorize
#         techniques = categorizer.categorize(user_prompt)

#         # Step 2: Retrieve best practices
#         best_practices = best_practices_retriever.get_best_practices(techniques)

#         # Step 3: Search nodes
#         nodes = node_searcher.search_nodes(techniques)

#         # Step 4: Rank nodes
#         ranked_nodes = node_ranker.rank_nodes(techniques)

#         # Step 5: Summarize workflow
#         summary = display_workflow_summary(techniques, best_practices, nodes, ranked_nodes)

#         # Step 6: Ask LLM for detailed guide
#         llm_prompt = f"User wants to automate a workflow.\nDetails:\n{summary}\nProvide a step-by-step actionable guide."
#         llm_response = llm.ask(llm_prompt)

#         return {
#             "summary": summary,
#             "llm_guide": llm_response
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# from fastapi import FastAPI
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# from categorizer import PromptCategorizer
# from best_practices import BestPracticesRetriever
# from node_search import NodeSearcher
# from node_ranking import NodeRanker
# from utils import display_workflow_summary
# from llm_interface import LLMInterface

# from fastapi import FastAPI
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware

# from backend.categorizer import PromptCategorizer
# from backend.best_practices import BestPracticesRetriever
# from backend.node_search import NodeSearcher
# from backend.node_ranking import NodeRanker
# from backend.utils import display_workflow_summary
# from backend.llm_interface import LLMInterface

# app = FastAPI(title="Custom Logic AI Assistant")

# # Enable frontend calls
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Init modules once
# categorizer = PromptCategorizer("data/example_prompts.json")
# best_practices = BestPracticesRetriever("data/workflow_best_practices.json")
# node_searcher = NodeSearcher("data/nodes_catalog.json")
# node_ranker = NodeRanker(node_searcher.get_all_nodes())
# llm = LLMInterface()

# class PromptRequest(BaseModel):
#     prompt: str

# @app.post("/analyze")
# def analyze_workflow(req: PromptRequest):
#     techniques = categorizer.categorize(req.prompt)
#     practices = best_practices.get_best_practices(techniques)
#     nodes = node_searcher.search_nodes(techniques)
#     ranked_nodes = node_ranker.rank_nodes(techniques)

#     summary = display_workflow_summary(
#         techniques, practices, nodes, ranked_nodes
#     )

#     llm_prompt = f"""
# User wants to build an automation workflow.

# {summary}

# Provide a step-by-step actionable guide.
# """

#     guide = llm.ask(llm_prompt)

#     return {
#         "techniques": techniques,
#         "summary": summary,
#         "guide": guide
#     }







from fastapi import FastAPI
from backend.schemas import UserRequest
from backend.intent import extract_intent
from backend.techniques import detect_techniques
from backend.best_practices import BestPractices
from backend.node_catalog import NodeCatalog
from backend.workflow_builder import build_workflow
from backend.llm import ask_llm

app = FastAPI()

bp = BestPractices()
catalog = NodeCatalog()

@app.post("/analyze")
def analyze(req: UserRequest):
    intent = extract_intent(req.prompt)
    techniques = detect_techniques(intent)
    practices = bp.get(techniques)
    workflow = build_workflow(techniques, catalog)

    context = f"""
User goal: {intent['goal']}

Workflow:
{workflow}

Best practices:
{practices}

Explain clearly and step-by-step.
"""

    explanation = ask_llm(context)

    return {
        "intent": intent,
        "techniques": techniques,
        "workflow": workflow,
        "explanation": explanation
    }
