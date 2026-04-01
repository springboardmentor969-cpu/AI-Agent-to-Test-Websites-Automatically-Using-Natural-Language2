from groq import Groq
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def normalize_instruction(user_input):

    prompt = f"""
You are an intelligent automation planner.

Convert the user instruction into structured steps.

Instruction:
{user_input}

STRICT RULES:
- If user mentions "youtube" → use https://www.youtube.com
- If user says "google" → use https://www.google.com
- "search <text>" → action: search
- "play" or "click first video" → action: click target="first video"
- "login with <value>" → action: type
- Always keep steps in correct order

Allowed actions:
open_url, search, click, type, wait

Return ONLY valid JSON list.

Example:
[
  {{"action":"open_url","url":"https://www.youtube.com"}},
  {{"action":"search","query":"telusko"}},
  {{"action":"click","target":"first video"}}
]
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        text = response.choices[0].message.content.strip()

        # 🔥 SAFE JSON PARSE
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        actions = json.loads(text)

        # ✅ VALIDATION (important)
        if isinstance(actions, list):
            return actions
        else:
            return []

    except Exception as e:
        print("LLM parsing failed:", e)
        return []


# -------- FALLBACK RULE-BASED (SAFETY) --------
def parse_instruction(user_input):

    text = user_input.lower()

    actions = []

    if "youtube" in text:
        actions.append(
            {"action": "open_url", "url": "https://www.youtube.com"})

    if "search" in text:
        query = text.split("search")[-1].strip()
        actions.append({"action": "search", "query": query})

    if "video" in text or "play" in text:
        actions.append({"action": "click", "target": "first video"})

    return actions
