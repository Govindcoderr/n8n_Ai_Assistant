# llm.py - Smart Continuous Chat with Contextual Prompt Improvement (using Groq)

import os
import certifi

# Fix common Windows SSL issue:  vs code error  
os.environ["SSL_CERT_FILE"] = certifi.where()

from groq import Groq

# === REPLACE WITH YOUR REAL GROQ API KEY ===
GROQ_API_KEY = "your_groq_api_key_here"

client = Groq(api_key=GROQ_API_KEY)

# Conversation history to maintain context across messages
history = [
    {"role": "system", "content": """
You are a helpful, friendly AI assistant. Respond naturally and conversationally.
Always answer based on the full context of the conversation so far.
"""}
]

def improve_and_classify_prompt(user_input: str, conversation_history: list) -> tuple[str, bool]:
    """
    Uses Groq to:
    1. Determine if the new input is continuing the previous topic or starting a new unrelated one.
    2. Improve the raw input into a clear, concise prompt/question.
    Returns: (improved_prompt, is_continuation)
    """
    # Build a short summary of recent history for context
    recent_history = conversation_history[-6:]  # Last 3 exchanges (user + assistant)
    history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent_history])

    classification_prompt = f"""
        You are an expert at understanding conversation flow and prompt refinement.

        Previous conversation (if any):
        {history_text}

        New user input: "{user_input}"

        Task:
        1. Determine if this new input is:
        - Continuing the previous topic/conversation (e.g., follow-up question, correction, more details about the same subject)
        - OR starting a completely new, unrelated topic

        2. Improve the raw user input into a clear, concise, standalone prompt/question that the AI can answer directly:
        - Fix spelling, grammar, capitalization, and make it polite/natural.
        - Turn fragments/statements into proper questions if needed.
        - For continuations: Incorporate obvious context from previous messages to make it self-contained (e.g., restate the main topic like app or action if implied).
        - Only add what is clearly implied — do not invent new details.
        - Keep it concise.

        Output exactly in this format (nothing else, no extra text):
        CONTINUATION: yes/no
        IMPROVED: [the improved prompt/question here]
    """

    res = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": classification_prompt}],
        temperature=0.1,
        max_tokens=512
    )
    
    output = res.choices[0].message.content.strip()
    
    # Parse the output
    lines = output.splitlines()
    continuation = "no"
    improved = user_input  # fallback
    
    for line in lines:
        if line.startswith("CONTINUATION:"):
            continuation = line.split(":", 1)[1].strip().lower()
        elif line.startswith("IMPROVED:"):
            improved = line.split(":", 1)[1].strip()
    
    is_continuation = continuation == "yes"
    return improved, is_continuation

def ask_llm(messages: list) -> str:
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,  # More natural responses
        max_tokens=1024
    )
    return res.choices[0].message.content

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