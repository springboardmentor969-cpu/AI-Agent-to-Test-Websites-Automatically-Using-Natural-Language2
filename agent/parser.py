import re

from agent.models import ParsedAction, ParsedInstruction


DEMO_LOGIN_URL = "http://127.0.0.1:5000/login"
YOUTUBE_URL = "https://www.youtube.com"
GOOGLE_URL = "https://www.google.com"


def _extract_value(text: str, field: str) -> str | None:
    patterns = [
        rf"{field}\s+(?:as|is)\s+[\"']?([A-Za-z0-9_@.\-]+)",
        rf"{field}\s*(?:=|:)\s*[\"']?([A-Za-z0-9_@.\-]+)",
        rf"{field}\s+[\"']?([A-Za-z0-9_@.\-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def parse_instruction_details(text: str) -> ParsedInstruction:
    lowered = text.lower()
    username = _extract_value(text, "username")
    password = _extract_value(text, "password")
    explicit_url = re.search(r"https?://[^\s]+", text, re.IGNORECASE)
    expected_result = None

    if "success" in lowered:
        expected_result = "Success"
    elif "fail" in lowered or "failure" in lowered:
        expected_result = "Failed"

    if explicit_url:
        target_name = explicit_url.group(0)
        target_url = target_name
        target_type = "website"
    elif "youtube" in lowered:
        target_name = "youtube"
        target_url = YOUTUBE_URL
        target_type = "website"
    elif "google" in lowered:
        target_name = "google"
        target_url = GOOGLE_URL
        target_type = "website"
    else:
        target_name = "demo_login"
        target_url = DEMO_LOGIN_URL
        target_type = "demo_login"

    actions: list[ParsedAction] = []

    if any(word in lowered for word in ["open", "go to", "visit", "navigate"]):
        actions.append(ParsedAction(action="open_page", target=target_name, value=target_url))

    if target_type == "demo_login":
        actions.append(ParsedAction(action="fill", target="#username", value=username or "test"))
        actions.append(ParsedAction(action="fill", target="#password", value=password or "1234"))
        actions.append(ParsedAction(action="click", target="#login"))
    elif "first video" in lowered:
        actions.append(ParsedAction(action="click", target="first_video"))
    elif "search" in lowered:
        actions.append(ParsedAction(action="search", target="query"))

    return ParsedInstruction(
        raw_input=text,
        target_name=target_name,
        target_url=target_url,
        target_type=target_type,
        username=username,
        password=password,
        expected_result=expected_result,
        actions=actions,
    )


def parse_instruction(text: str) -> list[dict[str, str | None]]:
    return parse_instruction_details(text).actions_as_dicts()


if __name__ == "__main__":
    sample = "Open login page and enter username test and password 1234 then click login"
    print(parse_instruction(sample))
