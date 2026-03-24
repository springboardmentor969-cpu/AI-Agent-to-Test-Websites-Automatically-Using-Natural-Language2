"""
Instruction Parser — NL → Structured JSON Actions
----------------------------------------------------
Converts natural-language test instructions into the structured action
format expected by code_generator.py and playwright_runner.py.

Uses Google Gemini (via google.genai) for rich, multi-step instructions,
with a lightweight spaCy fallback for simple single-action commands.

Output format (list of dicts):
    [
        {"type": "navigate", "url": "https://..."},
        {"type": "input",    "selector": "...", "value": "..."},
        {"type": "click",    "selector": "..."},
        {"type": "press",    "key": "Enter"},
        {"type": "wait",     "duration": 3000},
        {"type": "assert",   "selector": "...", "condition": "visible"},
    ]
"""

import json
import os
import time
from dotenv import load_dotenv

# ─── Gemini client ────────────────────────────────────────────────────────────

_PARSE_PROMPT = """\
You are an expert test-automation planner.

The user will give you a natural-language instruction describing what to do in
a web browser.  Your job is to produce a JSON array of action objects.

Each object must have a "type" key.  Valid types and their required fields:

| type     | required fields                           |
|----------|-------------------------------------------|
| navigate | url                                       |
| input    | selector, value                           |
| click    | selector                                  |
| press    | key  (e.g. "Enter", "Tab")                |
| wait     | duration  (milliseconds, integer)         |
| assert   | selector, condition, value (optional)     |

Rules:
1. Use CSS selectors that are likely to work on real sites.
   - For YouTube search: input[name='search_query']
   - For YouTube video click: ytd-video-renderer a#thumbnail
   - For generic login forms: #username, #password, #login-btn or button[type='submit']
2. Always start with a "navigate" action.
3. For YouTube tasks, add a wait after pressing Enter (3000ms) and after clicking
   a video (5000ms).
4. For login/form tasks, add an assert at the end to check success.
5. Output ONLY the JSON array — no explanation, no markdown fences.
"""


def _parse_with_gemini(instruction: str) -> list[dict]:
    """Use Gemini to convert NL instruction to structured actions."""
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    for attempt in range(1, 4):
        try:
            response = model.generate_content(
                f"{_PARSE_PROMPT}\n\nInstruction: {instruction}"
            )
            text = response.text.strip()

            # Strip markdown code fences if the model adds them
            if text.startswith("```json"):
                text = text[len("```json"):].strip()
            elif text.startswith("```"):
                text = text[3:].strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            actions = json.loads(text)
            if isinstance(actions, list) and len(actions) > 0:
                print(f"[Parser] Gemini returned {len(actions)} actions")
                return actions

            raise ValueError("Gemini returned empty or non-list JSON")

        except Exception as exc:
            error_msg = str(exc)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                wait = 30 * attempt
                print(f"[Parser] Rate limited, waiting {wait}s (attempt {attempt}/3)")
                time.sleep(wait)
                continue
            if attempt < 3 and ("json" in error_msg.lower() or "decode" in error_msg.lower()):
                print(f"[Parser] JSON parse error, retrying... ({error_msg})")
                continue
            raise

    raise RuntimeError("Gemini parser failed after 3 attempts")


# ─── Lightweight spaCy fallback ───────────────────────────────────────────────

def _parse_with_spacy(text: str) -> list[dict]:
    """Basic spaCy parser for simple single-action commands."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        return []

    doc = nlp(text)

    action = None
    target = None
    value = None

    for token in doc:
        if token.lemma_ in ["click", "open", "enter", "type", "go", "navigate"]:
            action = token.lemma_

    if "'" in text:
        value = text.split("'")[1]
    else:
        # Very crude fallback for "open youtube" -> value="youtube.com"
        words = text.lower().split()
        if "youtube" in words:
            value = "youtube.com"
        elif "localhost" in text:
            value = "localhost:5000/sample"
        # Extract target object generically
        for token in doc:
            if token.dep_ in ["dobj", "pobj"] and not value:
                value = token.text + ".com"

    if not action:
        return []

    # Map to structured action
    result = []
    if action in ("open", "go", "navigate") and value:
        url = value if value.startswith("http") else f"https://{value}"
        result.append({"type": "navigate", "url": url})
    elif action in ("click",) and target:
        result.append({"type": "click", "selector": f"#{target}"})
    elif action in ("enter", "type") and target and value:
        result.append({"type": "input", "selector": f"#{target}", "value": value})

    return result


# ─── Public API ───────────────────────────────────────────────────────────────

def parse_instruction(text: str) -> list[dict]:
    """
    Parse a natural-language test instruction into structured JSON actions.

    Tries Gemini first for rich multi-step parsing.
    Falls back to spaCy for simple commands if Gemini fails.
    """
    try:
        actions = _parse_with_gemini(text)
        if actions:
            return actions
    except Exception as exc:
        print(f"[Parser] Gemini failed: {exc}  — falling back to spaCy")

    actions = _parse_with_spacy(text)
    if actions:
        print(f"[Parser] spaCy fallback returned {len(actions)} actions")
        return actions

    # Last resort: try to clean up the input into a URL
    clean = text.lower().replace("open", "").replace("go to", "").replace("navigate to", "").strip()
    if not clean:
        clean = text.strip()
    
    # If it has spaces and no dots, it's likely a conversational question, not a URL
    if " " in clean and "." not in clean and "localhost" not in clean:
        raise ValueError("Instruction does not appear to be a valid test action or URL.")

    # If it lacks a domain suffix or localhost, append .com for testing purposes
    if "localhost" not in clean and "." not in clean:
        clean += ".com"
        
    url = clean if clean.startswith("http") else f"https://{clean}"
    print(f"[Parser] No actions parsed — creating basic navigate action to {url}")
    return [{"type": "navigate", "url": url}]