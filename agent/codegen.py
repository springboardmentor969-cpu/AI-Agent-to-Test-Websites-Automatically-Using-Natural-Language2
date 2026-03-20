import json
import os
from textwrap import dedent

from dotenv import load_dotenv
from openai import OpenAI

from agent.assertions import infer_expected_result
from agent.models import ParsedInstruction


load_dotenv()


def _python_string(value: str | None) -> str:
    return json.dumps(value or "")


def _sanitize_generated_code(code: str) -> str:
    cleaned = code.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def generate_demo_login_code(parsed: ParsedInstruction) -> str:
    expected_result = infer_expected_result(parsed) or "Success"

    return dedent(
        f"""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless={str(parsed.headless)})
            page = browser.new_page()
            page.goto({_python_string(parsed.target_url)})
            page.fill("#username", {_python_string(parsed.username or "test")})
            page.fill("#password", {_python_string(parsed.password or "1234")})
            page.click("#login")
            page.wait_for_timeout(500)
            expected_result = {_python_string(expected_result)}
            result = page.inner_text("#result")
            print(result)
            if result != expected_result:
                raise AssertionError(f"Expected {{expected_result!r}}, got {{result!r}}")
            browser.close()
        """
    ).strip()


def generate_youtube_code(parsed: ParsedInstruction) -> str:
    return dedent(
        f"""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto({_python_string(parsed.target_url)}, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            consent_buttons = [
                'button:has-text("Accept all")',
                'button:has-text("I agree")',
                'button:has-text("Accept")',
            ]
            for selector in consent_buttons:
                button = page.locator(selector).first
                if button.count() > 0:
                    try:
                        button.click(timeout=2000)
                        page.wait_for_timeout(2000)
                        break
                    except Exception:
                        pass

            first_video = None
            for selector in [
                'a[href*="/watch?v="]:visible',
                "a#video-title:visible",
                "a#video-title-link:visible",
                "ytd-rich-grid-media a#thumbnail:visible",
            ]:
                locator = page.locator(selector).first
                if locator.count() > 0:
                    first_video = locator
                    break

            if first_video is None:
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2000)
                retry_locator = page.locator('a[href*="/watch?v="]:visible').first
                if retry_locator.count() > 0:
                    first_video = retry_locator

            if first_video is None:
                raise RuntimeError("Could not find a clickable YouTube video on the page")

            first_video.scroll_into_view_if_needed(timeout=5000)
            first_video.click(timeout=10000)
            page.wait_for_timeout(3000)
            print("Clicked first YouTube video")
            browser.close()
        """
    ).strip()


def _get_llm_client() -> OpenAI | None:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def generate_llm_code(parsed: ParsedInstruction) -> str:
    client = _get_llm_client()
    if client is None:
        return dedent(
            f"""
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless={str(parsed.headless)})
                page = browser.new_page()
                page.goto({_python_string(parsed.target_url)})
                page.wait_for_timeout(3000)
                print("Opened {parsed.target_url}")
                browser.close()
            """
        ).strip()

    prompt = dedent(
        f"""
        You are generating a Playwright Python script.

        User instruction:
        {parsed.raw_input}

        Target URL:
        {parsed.target_url}

        Parsed actions:
        {[action.to_dict() for action in parsed.actions]}

        Rules:
        - Return only Python code
        - Use Playwright sync API
        - Launch Chromium with headless={str(parsed.headless)}
        - Visit the target URL
        - Print a short final status message
        """
    ).strip()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def generate_playwright_code(parsed: ParsedInstruction) -> str:
    if parsed.target_type == "demo_login":
        return generate_demo_login_code(parsed)
    if parsed.target_name == "youtube" and any(action.target == "first_video" for action in parsed.actions):
        return generate_youtube_code(parsed)
    return _sanitize_generated_code(generate_llm_code(parsed))
