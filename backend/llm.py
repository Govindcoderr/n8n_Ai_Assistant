# # llm.py - Smart Continuous Chat with Contextual Prompt Improvement (using Groq)

# import os
# import certifi

# # Fix common Windows SSL issue
# os.environ["SSL_CERT_FILE"] = certifi.where()

# from groq import Groq
# from dotenv import load_dotenv
# load_dotenv()
# # === REPLACE WITH YOUR REAL GROQ API KEY ===
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# client = Groq(api_key=GROQ_API_KEY)

# # Conversation history to maintain context across messages
# history = [
#     {"role": "system", "content": """
# You are a helpful, friendly AI assistant. Respond naturally and conversationally.
# Always answer based on the full context of the conversation so far.
# """}
# ]

# def improve_and_classify_prompt(user_input: str, conversation_history: list) -> tuple[str, bool]:
#     """
#     Uses Groq to:
#     1. Determine if the new input is continuing the previous topic or starting a new unrelated one.
#     2. Improve the raw input into a clear, concise prompt/question.
#     Returns: (improved_prompt, is_continuation)
#     """
#     # Build a short summary of recent history for context
#     recent_history = conversation_history[-6:]  # Last 3 exchanges (user + assistant)
#     history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent_history])

#     classification_prompt = f"""
#         You are an expert at understanding conversation flow and prompt refinement.

#         Previous conversation (if any):
#         {history_text}

#         New user input: "{user_input}"

#         Task:
#         1. Determine if this new input is:
#         - Continuing the previous topic/conversation (e.g., follow-up question, correction, more details about the same subject)
#         - OR starting a completely new, unrelated topic

#         2. Improve the raw user input into a clear, concise, standalone prompt/question that the AI can answer directly:
#         - Fix spelling, grammar, capitalization, and make it polite/natural.
#         - Turn fragments/statements into proper questions if needed.
#         - For continuations: Incorporate obvious context from previous messages to make it self-contained (e.g., restate the main topic like app or action if implied).
#         - Only add what is clearly implied — do not invent new details.
#         - Keep it concise.

#         Output exactly in this format (nothing else, no extra text):
#         CONTINUATION: yes/no
#         IMPROVED: [the improved prompt/question here]
#     """

#     res = client.chat.completions.create(
#         model="openai/gpt-oss-120b",
#         messages=[{"role": "user", "content": classification_prompt}],
#         temperature=0.1,
#         max_tokens=512
#     )
    
#     output = res.choices[0].message.content.strip()
    
#     # Parse the output
#     lines = output.splitlines()
#     continuation = "no"
#     improved = user_input  # fallback
    
#     for line in lines:
#         if line.startswith("CONTINUATION:"):
#             continuation = line.split(":", 1)[1].strip().lower()
#         elif line.startswith("IMPROVED:"):
#             improved = line.split(":", 1)[1].strip()
    
#     is_continuation = continuation == "yes"
#     return improved, is_continuation

# # def ask_llm(messages: list) -> str:
# #     res = client.chat.completions.create(
# #         model="llama-3.3-70b-versatile",
# #         messages=messages,
# #         temperature=0.7,  # More natural responses
# #         max_tokens=1024
# #     )
# #     return res.choices[0].message.content

# print("Smart Continuous Chat with Prompt Improvement (using Groq)")
# print("Type your message naturally. The system will improve it if needed and remember context.")
# print("Type 'exit' or 'quit' to stop.\n")

# while True:
#     user_input = input("You: ").strip()
    
#     if user_input.lower() in {"exit", "quit", ""}:
#         print("Goodbye!")
#         break
    
#     if not user_input:
#         continue
    
#     try:
#         # Step 1: Improve and classify the input
#         improved_prompt, is_continuation = improve_and_classify_prompt(user_input, history)
        
#         print(f"\n[Improved input sent]: {improved_prompt}\n")
#         print("-" * 80)
        
#         # Step 2: Add to history appropriately
#         if is_continuation:
#             # Just add as user message (context already there)
#             history.append({"role": "user", "content": improved_prompt})
#         else:
#             # Optional: you could clear or summarize old history for truly new topics
#             # Here we keep everything for simplicity
#             history.append({"role": "user", "content": improved_prompt})
        
        
#     except Exception as e:
#         print(f"Error: {e}")



# backend/llm.py
import os
from groq import Groq
from dotenv import load_dotenv
import certifi

# Fix common Windows SSL issue
os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=GROQ_API_KEY)

IMPROVER_MODEL = "openai/gpt-oss-120b"
CHAT_MODEL = "llama-3.3-70b-versatile"

def classify_and_improve_prompt(user_input: str, history: list) -> dict:
    """
    Classifies the user input and improves it if needed.
    
    Returns:
    {
        "type": "greeting" | "vague" | "clear",
        "improved_prompt": str,   # Only meaningful if type == "clear"
        "suggested_response": str # Ready-to-use response if greeting/vague
    }
    """
    user_input = user_input.strip()
    lower = user_input.lower()

    # === 1. Handle Greetings ===
    greetings = ["hi", "hello", "hey", "hii", "hiii", "good morning", "good afternoon", "good evening", "sup", "yo"]
    if any(lower.startswith(g) or lower == g for g in greetings):
        return {
            "type": "greeting",
            "improved_prompt": user_input,
            "suggested_response": (
                "I'll help you build n8n workflows! 👋\n\n"
                "Here are some popular things I can help you create:\n\n"
                "• Chatbots & AI assistants\n"
                "• Web scrapers\n"
                "• Scheduled automations\n"
                "• AI agents with tools\n"
                "• Data processing & ETL\n"
                "• Notifications (Email, Slack, Telegram, etc.)\n"
                "• App integrations\n\n"
                "What would you like to build today?"
            )
        }

    # === 2. Handle Vague / Incomplete Inputs ===
    vague_starts = ["i want to", "i want", "help", "workflow", "automate", "create", "build", "make", "can you"]
    if any(lower.startswith(v) for v in vague_starts) and len(user_input.split()) <= 6:
        return {
            "type": "vague",
            "improved_prompt": user_input,
            "suggested_response": (
                "I'm ready to help! Please tell me what you'd like to build.\n\n"
                "For example:\n"
                "• \"I want to create a chatbot that answers customer questions\"\n"
                "• \"I want to scrape product prices daily\"\n"
                "• \"Send me a Telegram message when a new Google Form is submitted\"\n"
                "• \"Automate invoice processing from email\"\n\n"
                "What workflow would you like to create?"
            )
        }

    # === 3. Clear Request → Improve Prompt ===
    recent_history = history[-8:]  # Last few messages for context
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])

    improvement_prompt = f"""
        You are an expert at refining user requests for an n8n workflow assistant.

        Previous conversation:
        {history_text}

        Latest user message: "{user_input}"

        Task: Improve this into a clear, complete, standalone request for building an n8n workflow.
        - Fix grammar, spelling, make it natural and specific
        - Add obvious implied details from context (e.g., app names, actions)
        - Keep it concise

        Output exactly:
        IMPROVED: [the improved request]
    """

    try:
        res = client.chat.completions.create(
            model=IMPROVER_MODEL,
            messages=[{"role": "user", "content": improvement_prompt}],
            temperature=0.2,
            max_tokens=256
        )
        output = res.choices[0].message.content.strip()
        improved = output.split("IMPROVED:", 1)[-1].strip() if "IMPROVED:" in output else user_input
    except Exception:
        improved = user_input  # fallback

    return {
        "type": "clear",
        "improved_prompt": improved,
        "suggested_response": None  # Will be generated by your main LLM logic
    }


def ask_llm(messages: list) -> str:
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,  # More natural responses
        max_tokens=1024
    )
    return res.choices[0].message.content

print("Smart Continuous Chat with Prompt Improvement (using Groq)")
print("Type your message naturally. The system will improve it if needed and remember context.")
print("Type 'exit' or 'quit' to stop.\n")

while True:
    user_input = input("You: ").strip()
    
#     if user_input.lower() in {"exit", "quit", ""}:
#         print("Goodbye!")
#         break
    
#     if not user_input:
#         continue
    
    try:
        # Step 1: Improve and classify the input
        improved_prompt, is_continuation = improve_and_classify_prompt(user_input, history)
        
        print(f"\n[Improved input sent]: {improved_prompt}\n")
        print("-" * 80)
        
        # Step 2: Add to history appropriately
        if is_continuation:
            # Just add as user message (context already there)
            history.append({"role": "user", "content": improved_prompt})
        else:
            # Optional: you could clear or summarize old history for truly new topics
            # Here we keep everything for simplicity
            history.append({"role": "user", "content": improved_prompt})
        
        
#     except Exception as e:
#         print(f"Error: {e}")