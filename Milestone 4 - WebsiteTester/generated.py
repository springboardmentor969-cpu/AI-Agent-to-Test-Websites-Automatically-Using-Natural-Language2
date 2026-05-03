from __future__ import annotations
import textwrap



SEARCH_SELECTORS: dict[str, str] = {
    "google":    "textarea[name='q'], input[name='q']",
    "youtube":   "input[name='search_query']",
    "bing":      "input[name='q']",
    "yahoo":     "input[name='p']",
    "github":    "input[name='q']",
    "reddit":    "input[name='q']",
    "twitter":   "input[data-testid='SearchBox_Search_Input']",
    "x.com":     "input[data-testid='SearchBox_Search_Input']",
    "default":   "input[type='search'], input[name='q'], textarea[name='q']",
}


RESULT_SELECTORS: dict[str, dict] = {
    "google": {
        "container": "div.g, div[data-hveid]",
        "title":     "h3",
        "link":      "a[href]",
        "snippet":   "div[data-sncf], span.VwiC3b, div.IsZvec",
    },
    "youtube": {
        "container": "ytd-video-renderer",
        "title":     "#video-title",
        "link":      "a#video-title",
        "snippet":   "#description-text",
    },
    "bing": {
        "container": "li.b_algo",
        "title":     "h2",
        "link":      "h2 a",
        "snippet":   "div.b_caption p",
    },
    "github": {
        "container": "div.search-title",
        "title":     "a",
        "link":      "a",
        "snippet":   "p",
    },
    "default": {
        "container": "h3",
        "title":     "h3",
        "link":      "a",
        "snippet":   "p",
    },
}




def _get_search_selector(url: str) -> str:
    for key, sel in SEARCH_SELECTORS.items():
        if key in url:
            return sel
    return SEARCH_SELECTORS["default"]


def _get_result_selectors(url: str) -> dict:
    for key, sels in RESULT_SELECTORS.items():
        if key in url:
            return sels
    return RESULT_SELECTORS["default"]


def _esc(s: str) -> str:
    """Escape double-quotes for safe embedding in f-strings."""
    return s.replace('"', '\\"')



def generate_code(steps: list[dict]) -> str:
    """
    Given a list of step-dicts (from parser.py), return a complete Playwright
    Python script as a string.

    Recognised step actions:
        open_url  – { "action": "open_url", "url": "https://..." }
        search    – { "action": "search",   "text": "query" }
    """

    
    url = "https://www.google.com"   
    search_text = ""

    for step in steps:
        if step["action"] == "open_url":
            url = step["url"]
        elif step["action"] == "search":
            search_text = step["text"]

    search_sel   = _get_search_selector(url)
    result_sels  = _get_result_selectors(url)

    
    lines: list[str] = []

    
    lines += [
        "import json",
        "from playwright.sync_api import sync_playwright",
        "",
        "def run_search() -> list[dict]:",
        '    """Execute the browser automation and return scraped results."""',
        "    results = []",
        "    with sync_playwright() as p:",
        "        browser = p.chromium.launch(",
        "            headless=False,",
        "            slow_mo=400,",
        "            args=[",
        "                '--disable-blink-features=AutomationControlled',",
        "                '--no-sandbox',",
        "                '--disable-dev-shm-usage',",
        "            ]",
        "        )",
        "        context = browser.new_context(",
        "            user_agent=(",
        "                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '",
        "                'AppleWebKit/537.36 (KHTML, like Gecko) '",
        "                'Chrome/120.0.0.0 Safari/537.36'",
        "            ),",
        "            viewport={'width': 1280, 'height': 800},",
        "        )",
        "        page = context.new_page()",
        "",
    ]

    
    lines += [
        f'        # ── Step 1: Open URL ──────────────────────────────────────',
        f'        page.goto("{_esc(url)}", timeout=20000)',
        f'        page.wait_for_load_state("domcontentloaded")',
        f'        print(f"Opened: {{page.title()}}")',
        "",
    ]

    
    if search_text:
        lines += [
            f'        # ── Step 2: Search ────────────────────────────────────────',
            f'        search_selector = "{_esc(search_sel)}"',
            f'        page.wait_for_selector(search_selector, timeout=15000)',
            f'        page.click(search_selector)           # focus the field',
            f'        page.fill(search_selector, "{_esc(search_text)}")',
            f'        page.press(search_selector, "Enter")',
            f'        print("Search submitted: {_esc(search_text)}")',
            "",
            f'        # ── Step 3: Wait for results ─────────────────────────────',
            f'        page.wait_for_load_state("domcontentloaded")',
            f'        page.wait_for_timeout(3000)   # let JS-rendered results appear',
            "",
        ]

       
        r = result_sels
        lines += [
            f'        # ── Step 4: Scrape results ───────────────────────────────',
            f'        containers = page.locator("{_esc(r["container"])}").all()',
            f'        print(f"Found {{len(containers)}} result containers")',
            f'',
            f'        for i, item in enumerate(containers[:10]):',
            f'            try:',
            f'                title_el   = item.locator("{_esc(r["title"])}").first',
            f'                link_el    = item.locator("{_esc(r["link"])}").first',
            f'                snippet_el = item.locator("{_esc(r["snippet"])}").first',
            f'',
            f'                title   = title_el.inner_text()   if title_el.count()   else ""',
            f'                href    = link_el.get_attribute("href") if link_el.count() else ""',
            f'                snippet = snippet_el.inner_text() if snippet_el.count() else ""',
            f'',
            f'                title   = title.strip()',
            f'                snippet = snippet.strip()[:300]',
            f'',
            f'                if title:',
            f'                    results.append({{',
            f'                        "rank":    i + 1,',
            f'                        "title":   title,',
            f'                        "url":     href or "",',
            f'                        "snippet": snippet,',
            f'                    }})',
            f'            except Exception as scrape_err:',
            f'                print(f"Skipping result {{i}}: {{scrape_err}}")',
            f'                continue',
            f'',
        ]

    
    lines += [
        "        page.wait_for_timeout(2000)",
        "        browser.close()",
        "    return results",
        "",
        "",
        "# ── Entry-point when script is run directly ──────────────────────────",
        "if __name__ == '__main__':",
        "    data = run_search()",
        "    print(json.dumps(data, indent=2, ensure_ascii=False))",
    ]

    
    script = "\n".join(lines)
    return script


#Quick smoke test for the generator
if __name__ == "__main__":
    from parser import parse_instruction
    steps = parse_instruction("open google.com and search nptel courses")
    print("=" * 60)
    print("PARSED STEPS:")
    import json
    print(json.dumps(steps, indent=2))
    print("=" * 60)
    print("GENERATED CODE:")
    print(generate_code(steps))
