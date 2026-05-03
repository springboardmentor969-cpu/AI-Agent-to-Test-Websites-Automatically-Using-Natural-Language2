import re
import json


KNOWN_DOMAINS = {
    "google":  "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github":  "https://www.github.com",
    "bing":    "https://www.bing.com",
    "yahoo":   "https://www.yahoo.com",
    "reddit":  "https://www.reddit.com",
    "twitter": "https://www.twitter.com",
    "x":       "https://www.x.com",
    "nptel":   "https://www.nptel.ac.in",
    "amazon":  "https://www.amazon.in",
    "flipkart":"https://www.flipkart.com",
    "linkedin":"https://www.linkedin.com",
    "wikipedia":"https://www.wikipedia.org",
}

def normalise_url(raw: str) -> str:
    """Turn bare words/partial URLs into a fully-qualified https:// URL."""
    raw = raw.strip().lower().rstrip("/")
    
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    
    base = raw.split(".")[0]
    if base in KNOWN_DOMAINS:
        return KNOWN_DOMAINS[base]
    
    if "." in raw:
        return "https://" + raw
    
    return "https://www." + raw + ".com"



def parse_instruction(instruction: str) -> list[dict]:
    """
    Convert a natural-language browser instruction into an ordered list of
    action steps that generated.py can consume.

    Supported patterns (case-insensitive, combinable):
      • open <url>
      • go to <url>  /  navigate to <url>  /  visit <url>
      • search <query>  /  search for <query>
      • type <text>  /  enter <text>
      • click <element>
    """
    text = instruction.strip()
    steps: list[dict] = []


    url_pattern = re.compile(
        r'\b(?:open|go\s+to|navigate\s+to|visit|launch)\s+'
        r'([\w.\-]+(?:\.[a-z]{2,})?(?:/\S*)?)',
        re.IGNORECASE
    )
    url_match = url_pattern.search(text)
    if url_match:
        raw_url = url_match.group(1)
        steps.append({"action": "open_url", "url": normalise_url(raw_url)})


    search_pattern = re.compile(
        r'\bsearch(?:\s+for)?\s+(.+?)(?:\s+(?:on|in|at)\s+\S+)?$',
        re.IGNORECASE
    )
    search_match = search_pattern.search(text)
    if search_match:
        query = search_match.group(1).strip()
        
        query = re.sub(r'\s+(?:on|in|at)\s+\S+$', '', query, flags=re.IGNORECASE)
        steps.append({"action": "search", "text": query})


    if not search_match:
        type_pattern = re.compile(
            r'\b(?:type|enter|input|write)\s+["\']?(.+?)["\']?(?:\s+(?:in|into|on)\s+\S+)?$',
            re.IGNORECASE
        )
        type_match = type_pattern.search(text)
        if type_match:
            steps.append({"action": "enter_text",
                          "field": "search",
                          "text": type_match.group(1).strip()})

    click_pattern = re.compile(
        r'\bclick\s+(?:on\s+)?["\']?(.+?)["\']?(?:\s*$|\s+(?:and|then))',
        re.IGNORECASE
    )
    for m in click_pattern.finditer(text):
        steps.append({"action": "click", "element": m.group(1).strip()})

    
    if not steps:
        steps.append({
            "action": "error",
            "message": f"Could not parse instruction: '{instruction}'"
        })

    return steps



if __name__ == "__main__":
    tests = [
        "open google.com and search nptel courses",
        "go to youtube.com and search lofi music",
        "open github.com and search langchain",
        "open google.com and search python tutorials",
        "visit wikipedia.org and search machine learning",
    ]
    for t in tests:
        print(f"\nInstruction : {t}")
        print(f"Parsed Steps: {json.dumps(parse_instruction(t), indent=2)}")
