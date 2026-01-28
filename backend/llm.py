
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

    # ================================================================
    # NEW: Universal finalization (DONE button support)
    # ================================================================
    if user_wants_to_finalize(user_input):
        final = last_intent_message or (
            history[-2]["content"] if len(history) >= 2 else user_input
        )
        is_refining = False
        return {
            "stop": False,
            "finalized": True,
            "clean_prompt": final,
            "intent": None,
            "confidence": 1.0
        }

    # ================================================================
    # NEW: Semantic workflow detection (allows complex workflow inputs)
    # ================================================================
    workflow_keywords = [
        "workflow", "node", "trigger", "api", "http", "update",
        "metadata", "caption", "youtube", "slack", "telegram",
        "transcript", "append", "set", "extract", "google",
        "batch", "process", "automation", "video", "split"
    ]
    user_lower = user_input.lower()
    contains_workflow = any(k in user_lower for k in workflow_keywords)
    long_instruction = len(user_input.split()) >= 12
    semantic_accept = contains_workflow or long_instruction

    # 1. Finalization
    if is_refining and user_wants_to_finalize(user_input):
        if last_intent_message:
            final = last_intent_message
        else:
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

    # ================================================================
    # NEW: Bypass guard IF workflow detected
    # ================================================================
    if guard_result and not is_refining and not semantic_accept:
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

    # ================================================================
    # NEW: allow unclear classification IF workflow-like input
    # ================================================================
    if result.categorization.intent_status != "clear" and not semantic_accept:
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

