"""
Assertion Generator
-------------------
Converts structured JSON assert actions into Playwright Python assertion code.

Supported conditions:
  - "visible"       → expect(page.locator(selector)).to_be_visible()
  - "text_present"  → expect(page.locator(selector)).to_contain_text(value)
  - "url_contains"  → expect(page).to_have_url(re.compile(value))
"""


def generate_assertion(action: dict) -> str:
    """
    Generate a Playwright assertion code string from a structured action dict.

    Parameters
    ----------
    action : dict
        Must contain:
          - "selector"  : CSS selector (for visible / text_present)
          - "condition" : one of "visible", "text_present", "url_contains"
          - "value"     : (optional) expected text or URL substring

    Returns
    -------
    str
        A single line of Playwright assertion code.

    Raises
    ------
    ValueError
        If the condition is not recognized.
    """
    condition = str(action.get("condition") or "visible")
    selector = str(action.get("selector") or "")
    value = str(action.get("value") or "")

    if condition == "visible":
        return f'expect(page.locator("{selector}")).to_be_visible()'

    elif condition == "text_present":
        return f'expect(page.locator("{selector}")).to_contain_text("{value}")'

    elif condition == "url_contains":
        return f'expect(page).to_have_url(re.compile(r"{value}"))'

    else:
        raise ValueError(
            f"Unsupported assertion condition: '{condition}'. "
            f"Supported: visible, text_present, url_contains"
        )
