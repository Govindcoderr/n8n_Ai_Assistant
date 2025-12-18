# # # llm.py - Smart Continuous Chat with Contextual Prompt Improvement (using Groq)

# # import os
# # import certifi

# # # Fix common Windows SSL issue
# # os.environ["SSL_CERT_FILE"] = certifi.where()

# # from groq import Groq
# # from dotenv import load_dotenv
# # load_dotenv()
# # # === REPLACE WITH YOUR REAL GROQ API KEY ===
# # GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# # client = Groq(api_key=GROQ_API_KEY)

# # # Conversation history to maintain context across messages
# # history = [
# #     {"role": "system", "content": """
# # You are a helpful, friendly AI assistant. Respond naturally and conversationally.
# # Always answer based on the full context of the conversation so far.
# # """}
# # ]

# # def improve_and_classify_prompt(user_input: str, conversation_history: list) -> tuple[str, bool]:
# #     """
# #     Uses Groq to:
# #     1. Determine if the new input is continuing the previous topic or starting a new unrelated one.
# #     2. Improve the raw input into a clear, concise prompt/question.
# #     Returns: (improved_prompt, is_continuation)
# #     """
# #     # Build a short summary of recent history for context
# #     recent_history = conversation_history[-6:]  # Last 3 exchanges (user + assistant)
# #     history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent_history])

# #     classification_prompt = f"""
# #         You are an expert at understanding conversation flow and prompt refinement.

# #         Previous conversation (if any):
# #         {history_text}

# #         New user input: "{user_input}"

# #         Task:
# #         1. Determine if this new input is:
# #         - Continuing the previous topic/conversation (e.g., follow-up question, correction, more details about the same subject)
# #         - OR starting a completely new, unrelated topic

# #         2. Improve the raw user input into a clear, concise, standalone prompt/question that the AI can answer directly:
# #         - Fix spelling, grammar, capitalization, and make it polite/natural.
# #         - Turn fragments/statements into proper questions if needed.
# #         - For continuations: Incorporate obvious context from previous messages to make it self-contained (e.g., restate the main topic like app or action if implied).
# #         - Only add what is clearly implied — do not invent new details.
# #         - Keep it concise.

# #         Output exactly in this format (nothing else, no extra text):
# #         CONTINUATION: yes/no
# #         IMPROVED: [the improved prompt/question here]
# #     """

# #     res = client.chat.completions.create(
# #         model="openai/gpt-oss-120b",
# #         messages=[{"role": "user", "content": classification_prompt}],
# #         temperature=0.1,
# #         max_tokens=512
# #     )
    
# #     output = res.choices[0].message.content.strip()
    
# #     # Parse the output
# #     lines = output.splitlines()
# #     continuation = "no"
# #     improved = user_input  # fallback
    
# #     for line in lines:
# #         if line.startswith("CONTINUATION:"):
# #             continuation = line.split(":", 1)[1].strip().lower()
# #         elif line.startswith("IMPROVED:"):
# #             improved = line.split(":", 1)[1].strip()
    
# #     is_continuation = continuation == "yes"
# #     return improved, is_continuation

# # # def ask_llm(messages: list) -> str:
# # #     res = client.chat.completions.create(
# # #         model="llama-3.3-70b-versatile",
# # #         messages=messages,
# # #         temperature=0.7,  # More natural responses
# # #         max_tokens=1024
# # #     )
# # #     return res.choices[0].message.content

# # print("Smart Continuous Chat with Prompt Improvement (using Groq)")
# # print("Type your message naturally. The system will improve it if needed and remember context.")
# # print("Type 'exit' or 'quit' to stop.\n")

# # while True:
# #     user_input = input("You: ").strip()
    
# #     if user_input.lower() in {"exit", "quit", ""}:
# #         print("Goodbye!")
# #         break
    
# #     if not user_input:
# #         continue
    
# #     try:
# #         # Step 1: Improve and classify the input
# #         improved_prompt, is_continuation = improve_and_classify_prompt(user_input, history)
        
# #         print(f"\n[Improved input sent]: {improved_prompt}\n")
# #         print("-" * 80)
        
# #         # Step 2: Add to history appropriately
# #         if is_continuation:
# #             # Just add as user message (context already there)
# #             history.append({"role": "user", "content": improved_prompt})
# #         else:
# #             # Optional: you could clear or summarize old history for truly new topics
# #             # Here we keep everything for simplicity
# #             history.append({"role": "user", "content": improved_prompt})
        
        
# #     except Exception as e:
# #         print(f"Error: {e}")



# # llm.py - Smart n8n Workflow Assistant with Greeting & Intent Understanding
# import os
# from groq import Groq
# from dotenv import load_dotenv
# import certifi
# # Fix common Windows SSL issue
# os.environ["SSL_CERT_FILE"] = certifi.where()
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     raise ValueError("GROQ_API_KEY not found. Set it in .env file.")

# client = Groq(api_key=GROQ_API_KEY)

# # Best models for accuracy
# IMPROVER_MODEL = "openai/gpt-oss-120b"   # Great for reasoning & correction
# CHAT_MODEL = "llama-3.3-70b-versatile"        # Natural responses

# # Global conversation history
# history = [
#     {"role": "system", "content": """
#     You are n8n AI — a friendly, expert assistant that helps users build automation workflows in n8n.
#     You understand natural language, fix typos, and clarify intent.
#     Be warm, encouraging, and professional.
#     """
#     }
# ]

# def improve_and_classify_prompt(user_input: str) -> tuple[str, str]:
#     """
#     Returns: (improved_prompt, response_type)
#     response_type can be: "greeting", "vague", "clear"
#     """
#     user_input = user_input.strip()
#     lower = user_input.lower()

#     # === 1. Greeting Detection ===
#     greetings = ["hi", "hello", "hey", "hii", "hiii", "good morning", "good afternoon", "good evening", "sup", "yo", "what's up"]
#     if any(lower.startswith(g) or lower == g for g in greetings):
#         welcome_msg = (
#             "Hello! 👋 Welcome! I'm n8n AI — your personal workflow builder.\n\n"
#             "I can help you create:\n"
#             "• WhatsApp auto-replies & messaging\n"
#             "• Microsoft Teams notifications\n"
#             "• Google Forms → any app automation\n"
#             "• Chatbots\n"
#             "• Scheduled tasks\n"
#             "• Web scraping\n\n"
#             "What would you like to build today?"
#         )
#         return user_input, "greeting", welcome_msg

#     # === 2. Vague / Incomplete Detection ===
#     vague_starts = ["i want to", "i want", "help", "build", "make", "workflow", "automate", "can you"]
#     if any(lower.startswith(v) for v in vague_starts) and len(user_input.split()) <= 8:
#         clarification = (
#             "I'm ready to help you build something awesome! 🚀\n\n"
#             "Please tell me more — for example:\n"
#             "• \"Auto-reply on WhatsApp when someone messages me\"\n"
#             "• \"Send email via Gmail when a form is submitted\"\n"
#             "• \"Post to Microsoft Teams channel daily\"\n\n"
#             "What automation do you have in mind?"
#         )
#         return user_input, "vague", clarification

#     # === 3. Clear Request → Improve with LLM (typos, intent, follow-ups) ===
#     recent_history = history[-10:]
#     history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])

#     improvement_prompt = f"""
#         You are an expert intent clarifier and text corrector for an n8n workflow assistant.

#         Conversation so far:
#         {history_text}

#         User's new message: "{user_input}"

#         Your task:
#         - Fix all typos/spelling (workfloew → workflow, msg → message, whatsapp → WhatsApp, gmail → Gmail)
#         - Correct grammar and formatting
#         - Understand follow-ups ("instead of X use Y" means change from previous)
#         - Clarify intent while keeping original meaning
#         - Output a clear, natural, standalone workflow request

#         Respond ONLY with:
#         IMPROVED: [final improved prompt here]
#     """

#     try:
#         res = client.chat.completions.create(
#             model=IMPROVER_MODEL,
#             messages=[{"role": "user", "content": improvement_prompt}],
#             temperature=0.0,  # Perfect consistency
#             max_tokens=150
#         )
#         output = res.choices[0].message.content.strip()
#         improved = output.split("IMPROVED:", 1)[-1].strip() if "IMPROVED:" in output else user_input
#     except Exception as e:
#         print(f"[Improvement error: {e}] Using fallback.")
        

#     return improved, "clear", None


# print("🤖 n8n AI Assistant – Smart Workflow Builder")
# print("I understand greetings, fix typos, and follow your intent!\n")
# print("Type 'exit' or 'quit' to stop.\n")

# while True:
#     try:
#         user_input = input("You: ").strip()

#         if user_input.lower() in {"exit", "quit", "bye"}:
#             print("\n👋 Goodbye! Happy automating! Come back anytime.\n")
#             break

#         if not user_input:
#             continue

#         improved_prompt, msg_type, special_response = improve_and_classify_prompt(user_input)

#         print(f"\n[Improved]: {improved_prompt}")

#         if msg_type == "greeting" or msg_type == "vague":
#             print(f"\n{special_response}\n")
#         else:
#             print("\n(Ready for workflow analysis — connect to your main logic here)\n")

#         # Always add to history for context
#         history.append({"role": "user", "content": improved_prompt})

#     except KeyboardInterrupt:
#         print("\n\n👋 Goodbye!")
#         break
#     except Exception as e:
#         print(f"\nError: {e}\n")


# 

import os
import json
import re
from dataclasses import dataclass
from typing import List, Optional, Literal
from difflib import SequenceMatcher
from dotenv import load_dotenv
from groq import Groq
import certifi

# -------------------------------------------------------------------------
# ENV + CLIENT INITIALIZATION
# -------------------------------------------------------------------------

os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing in .env")

client = Groq(api_key=GROQ_API_KEY)

INTENT_MODEL = "openai/gpt-oss-120b"
FOLLOWUP_MODEL = "openai/gpt-oss-120b"


# -------------------------------------------------------------------------
# DATA CONTRACTS
# -------------------------------------------------------------------------

IntentStatus = Literal["greeting", "vague", "clear"]

@dataclass
class PromptCategorization:
    intent_status: IntentStatus
    intent_label: Optional[str]
    confidence: float

@dataclass
class CategorizePromptOutput:
    categorization: PromptCategorization
    improved_prompt: str
    followup_question: Optional[str]


# -------------------------------------------------------------------------
# GLOBAL STATE
# -------------------------------------------------------------------------

last_intent_message: Optional[str] = None
is_refining: bool = False


# -------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------------------------------------

def semantic_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def safe_json_extract(llm_output: str) -> Optional[dict]:
    match = re.search(r"\{[\s\S]*\}", llm_output)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None


def llm_is_followup(previous: str, current: str) -> bool:
    """Tiny LLM classifier that returns only yes/no."""
    prompt = f"""
Determine if the second message is a refinement of the first.

FIRST: "{previous}"
SECOND: "{current}"

Respond ONLY with: yes or no
"""

    try:
        res = client.chat.completions.create(
            model=FOLLOWUP_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=2
        )
        return res.choices[0].message.content.strip().lower() == "yes"
    except Exception:
        return False


def user_wants_to_finalize(user_input: str) -> bool:
    finalize_keywords = [
        "done", "final", "finish", "finalize", "generate",
        "ok finalize", "create it", "that's it", "proceed", "ready"
    ]
    text = user_input.strip().lower()
    return any(text == k or text.endswith(k) for k in finalize_keywords)


# -------------------------------------------------------------------------
# GUARD LAYER (NO LLM)
# -------------------------------------------------------------------------

def guard_input(user_input: str, history: List[dict]) -> Optional[CategorizePromptOutput]:
    text = user_input.strip().lower()

    greetings = {
        "hi", "hello", "hey", "hii", "hiii",
        "good morning", "good afternoon", "good evening"
    }

    # 1. Greeting detection
    if text in greetings:
        return CategorizePromptOutput(
            categorization=PromptCategorization("greeting", None, 1.0),
            improved_prompt=user_input,
            followup_question="What would you like to automate today?"
        )

    # 2. Follow-up detection — skip if refining mode
    if history and not user_wants_to_finalize(text):
        prev_msgs = [h["content"] for h in history if h["role"] == "user"]

        if len(prev_msgs) >= 2:
            prev = prev_msgs[-2].lower()
            curr = text

            # A: short follow-ups with typical refinement keywords
            if len(curr.split()) <= 5:
                keywords = [
                    "using", "with", "via", "from", "into", "to",
                    "powerbi", "excel", "sheet", "sql",
                    "instead", "teams", "whatsapp", "dashboard",
                    "daily", "refresh", "compress", "send",
                    "yes", "ok"
                ]
                if any(k in curr for k in keywords):
                    return None

            # B: semantic continuation
            if semantic_similarity(prev, curr) > 0.45:
                return None

            # C: LLM follow-up check
            if llm_is_followup(prev, curr):
                return None

    # 3. Vague fallback
    if len(text.split()) <= 5:
        return CategorizePromptOutput(
            categorization=PromptCategorization("vague", None, 0.3),
            improved_prompt=user_input,
            followup_question=(
                "Could you describe the workflow more clearly?\n\n"
                "Examples:\n"
                "• Send an email every morning at 9 AM\n"
                "• Notify me on Teams when a Google Form is submitted"
            )
        )

    return None


# -------------------------------------------------------------------------
# INTENT CLASSIFIER
# -------------------------------------------------------------------------

def llm_classify_and_improve(user_input: str, history: List[dict]) -> CategorizePromptOutput:
    history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history[-8:])

    prompt = f"""
You are an intent classifier for a workflow automation assistant.

STRICT RULES:
- Output ONLY valid JSON.
- JSON must begin with '{{' and end with '}}'.
- No explanations or surrounding text.

Conversation History:
{history_text}

User message: "{user_input}"

Return JSON exactly in this structure:
{{
  "intent_status": "greeting" | "vague" | "clear",
  "intent_label": null | "email" | "schedule" | "webhook" |
                   "scrape" | "chatbot" | "database" | "notification",
  "confidence": number,
  "improved_prompt": string,
  "followup_question": null | string
}}
"""

    res = client.chat.completions.create(
        model=INTENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=400
    )

    parsed = safe_json_extract(res.choices[0].message.content)
    if not parsed:
        return CategorizePromptOutput(
            categorization=PromptCategorization("vague", None, 0.1),
            improved_prompt=user_input,
            followup_question="I couldn't understand that. Can you clarify the workflow?"
        )

    return CategorizePromptOutput(
        categorization=PromptCategorization(
            parsed.get("intent_status", "vague"),
            parsed.get("intent_label"),
            parsed.get("confidence", 0.5)
        ),
        improved_prompt=parsed.get("improved_prompt", user_input),
        followup_question=parsed.get("followup_question")
    )


# -------------------------------------------------------------------------
# MAIN INTENT PROCESSOR
# -------------------------------------------------------------------------

def process_user_prompt(user_input: str, history: List[dict]) -> dict:
    global last_intent_message, is_refining

    history.append({"role": "user", "content": user_input})

    # 1. Finalization
    if is_refining and user_wants_to_finalize(user_input):
           # Use the last refined intent if exists
        if last_intent_message:
            final = last_intent_message
        else:
            # fallback: previous user message
            final = history[-2]["content"] if len(history) >= 2 else user_input

        is_refining = False

        return {
            "stop": False,
            "finalized": True,
            "clean_prompt": final,
            "intent": None,
            "confidence": 1.0
        }

    # 2. Guard Layer
    guard_result = guard_input(user_input, history)
    if guard_result and not is_refining:
        history.append({"role": "assistant", "content": guard_result.followup_question})
        return {"stop": True, "reply": guard_result.followup_question}

    # 3. Follow-up merging
    if last_intent_message is not None:
        if llm_is_followup(last_intent_message, user_input):
            merged = f"{last_intent_message}. Modify it as follows: {user_input}"
            result = llm_classify_and_improve(merged, history)

            if result.categorization.intent_status == "clear":
                last_intent_message = result.improved_prompt
                is_refining = True
                return {
                    "stop": False,
                    "refining": True,
                    "clean_prompt": result.improved_prompt,
                    "intent": result.categorization.intent_label,
                    "confidence": result.categorization.confidence
                }

    # 4. Standard intent creation
    result = llm_classify_and_improve(user_input, history)

    if result.categorization.intent_status != "clear":
        history.append({"role": "assistant", "content": result.followup_question})
        return {"stop": True, "reply": result.followup_question}

    # 5. Start refining mode
    last_intent_message = result.improved_prompt
    is_refining = True

    return {
        "stop": False,
        "refining": True,
        "clean_prompt": result.improved_prompt,
        "intent": result.categorization.intent_label,
        "confidence": result.categorization.confidence
    }


# -------------------------------------------------------------------------
# CLI LOOP
# -------------------------------------------------------------------------

# if __name__ == "__main__":
#     history = []

#     print("n8n Workflow AI Assistant — Multi-Turn Refinement Mode Enabled")
#     print("Type your message. Ctrl+C to exit.\n")

#     while True:
#         try:
#             user_input = input("You: ").strip()
#             result = process_user_prompt(user_input, history)

#             if result.get("finalized"):
#                 print("\n--- FINALIZED INTENT ---")
#                 print(result["clean_prompt"])
#                 print("------------------------\n")
#                 break

#             if result["stop"]:
#                 print(f"\nAssistant: {result['reply']}\n")
#             else:
#                 print("\n--- INTENT UPDATED ---")
#                 print("Refining Mode:", result.get("refining", False))
#                 print("Improved Prompt:", result["clean_prompt"])
#                 print("Confidence:", result["confidence"])
#                 print("----------------------\n")

#         except KeyboardInterrupt:
#             print("\nGoodbye!\n")
#             break
