def _normalize_url(raw: str) -> str:
    """
    Normalize any user-supplied URL string to a clean https:// URL.
    Handles all casing/format variants:
      youtube / Youtube / YOUTUBE / youtube.com / YouTube.com /
      https://youtube.com / http://www.youtube.com  →  https://www.youtube.com
    """
    clean = raw.strip()
    lower = clean.lower()

    # Remove scheme for inspection
    for prefix in ("https://", "http://"):
        if lower.startswith(prefix):
            lower = lower[len(prefix):]
            break

    # Remove leading www.
    bare = lower.lstrip("www.")

    # Known-site canonical URL table — extend as needed
    KNOWN = {
        "youtube":     "https://www.youtube.com",
        "youtube.com": "https://www.youtube.com",
        "google":      "https://www.google.com",
        "google.com":  "https://www.google.com",
        "github":      "https://www.github.com",
        "github.com":  "https://www.github.com",
    }

    host = bare.split("/")[0]
    if host in KNOWN:
        return KNOWN[host]

    # Unknown site — just ensure it has a scheme
    if not clean.lower().startswith(("http://", "https://")):
        return "https://" + clean
    return clean


def parse_instruction(text):
    steps = []

    # NOTE: do NOT lowercase the whole text here — URLs need original casing
    # We lowercase only for keyword matching
    text_lower = text.lower().strip()

    # Split multiple actions using "and"
    # Use original text for splitting so URLs aren't mangled
    parts_lower = [p.strip() for p in text_lower.split(" and ")]
    parts_orig  = [p.strip() for p in text.strip().split(" and ")]

    for part_lower, part_orig in zip(parts_lower, parts_orig):

        # ── OPEN URL ──────────────────────────────────────────────────────────
        if part_lower.startswith("open"):
            try:
                # Extract the token right after "open"
                raw_url = part_orig.replace("open", "", 1).replace("Open", "", 1).strip().split()[0]
                url = _normalize_url(raw_url)
                steps.append({"action": "open_url", "url": url})
            except:
                pass

        # ── CLICK ─────────────────────────────────────────────────────────────
        elif part_lower.startswith("click"):
            element = part_lower.replace("click", "").strip()
            element = element.replace("button", "").strip().replace(" ", "")
            steps.append({"action": "click", "element": element})

        # ── SEARCH ────────────────────────────────────────────────────────────
        elif part_lower.startswith("search"):
            query = part_orig.replace("search", "", 1).replace("Search", "", 1).strip()
            # strip leading "for" if present  e.g. "search for cats"
            if query.lower().startswith("for "):
                query = query[4:].strip()
            steps.append({"action": "search", "text": query})

        # ── TYPE (treated as search) ──────────────────────────────────────────
        elif part_lower.startswith("type"):
            query = part_orig.replace("type", "", 1).replace("Type", "", 1).strip()
            steps.append({"action": "search", "text": query})

        # ── ENTER TEXT INTO FIELD ─────────────────────────────────────────────
        elif part_lower.startswith("enter") and "into" in part_lower:
            try:
                content = part_orig.replace("enter", "", 1).replace("Enter", "", 1).strip()
                text_to_enter, field = content.split(" into ", 1)
                steps.append({
                    "action": "enter_text",
                    "text": text_to_enter.strip(),
                    "field": field.strip()
                })
            except:
                pass

        # ── CLICK FIRST RESULT ────────────────────────────────────────────────
        elif "click" in part_lower and ("first" in part_lower or "top" in part_lower):
            steps.append({"action": "click_first_result"})

        # ── FREE-FORM INSTRUCTION TEXT ────────────────────────────────────────
        elif not any(kw in part_lower for kw in ["open", "click", "search", "type", "enter"]):
            steps.append({
                "action": "enter_instruction_text",
                "text": part_orig.strip()
            })

    return steps