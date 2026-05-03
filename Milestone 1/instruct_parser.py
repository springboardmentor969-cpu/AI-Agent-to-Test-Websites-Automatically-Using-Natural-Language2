from typing import List, Dict
import re
import google.generativeai as genai
import os
import json


class InstructionParser:
    def __init__(self):
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        
        # Define supported action types
        self.action_types = {
            "navigate": ["go to", "open", "visit", "navigate to"],
            "click": ["click", "press", "tap", "select"],
            "type": ["type", "enter", "input", "fill", "write"],
            "wait": ["wait", "pause", "delay"],
            "verify": ["verify", "check", "assert", "confirm", "validate"],
            "screenshot": ["screenshot", "capture", "take picture"],
            "scroll": ["scroll", "scroll to", "scroll down", "scroll up"]
        }
    
    def parse_instruction(self, instruction: str) -> Dict:
        """
        Parse a single natural language instruction into structured format
        
        Args:
            instruction: Natural language test instruction
            
        Returns:
            Dictionary with parsed action details
        """
        
        prompt = f"""
You are an expert test automation parser. Parse the following test instruction into a structured format.

Instruction: "{instruction}"

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
    "action_type": "navigate|click|type|wait|verify|screenshot|scroll",
    "target": "the element or URL to interact with",
    "value": "value to input (for type actions) or expected value (for verify)",
    "description": "human-readable description of what this step does"
}}

Examples:
- "Go to https://example.com" → {{"action_type": "navigate", "target": "https://example.com", "value": null, "description": "Navigate to example.com"}}
- "Click the login button" → {{"action_type": "click", "target": "login button", "value": null, "description": "Click the login button"}}
- "Type 'admin' in username field" → {{"action_type": "type", "target": "username field", "value": "admin", "description": "Enter username"}}
- "Verify page title contains 'Dashboard'" → {{"action_type": "verify", "target": "page title", "value": "Dashboard", "description": "Verify Dashboard page loaded"}}

Now parse the instruction and return ONLY the JSON object.
"""
        
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up the response - remove markdown code blocks if present
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)
        result_text = result_text.strip()
        
        try:
            parsed_action = json.loads(result_text)
            return parsed_action
        except json.JSONDecodeError as e:
            # Fallback to basic parsing
            return self._fallback_parse(instruction)
    
    def _fallback_parse(self, instruction: str) -> Dict:
        """
        Fallback parsing method if LLM fails to return valid JSON
        """
        instruction_lower = instruction.lower()
        
        # Detect action type
        action_type = "unknown"
        for action, keywords in self.action_types.items():
            if any(keyword in instruction_lower for keyword in keywords):
                action_type = action
                break
        
        return {
            "action_type": action_type,
            "target": instruction,
            "value": None,
            "description": instruction
        }
    
    def parse_test_case(self, test_case: str) -> List[Dict]:
        """
        Parse a complete test case with multiple steps
        
        Args:
            test_case: Natural language test case (can be multi-line)
            
        Returns:
            List of parsed action dictionaries
        """
        
        # Split by newlines or common separators
        steps = []
        lines = test_case.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            # Remove numbering like "1.", "2.", "Step 1:", etc.
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            line = re.sub(r'^Step\s+\d+:\s*', '', line, flags=re.IGNORECASE)
            
            if line:
                parsed = self.parse_instruction(line)
                steps.append(parsed)
        
        return steps
    
    def map_to_playwright_actions(self, parsed_actions: List[Dict]) -> List[Dict]:
        """
        Map parsed actions to Playwright-specific commands
        
        Args:
            parsed_actions: List of parsed action dictionaries
            
        Returns:
            List of Playwright command dictionaries
        """
        
        playwright_actions = []
        
        for action in parsed_actions:
            action_type = action.get("action_type", "unknown")
            target = action.get("target", "")
            value = action.get("value")
            
            pw_action = {
                "original_action": action,
                "playwright_command": None,
                "selector_strategy": None
            }
            
            if action_type == "navigate":
                pw_action["playwright_command"] = f'page.goto("{target}")'
                
            elif action_type == "click":
                selector = self._generate_selector(target)
                pw_action["playwright_command"] = f'page.click("{selector}")'
                pw_action["selector_strategy"] = selector
                
            elif action_type == "type":
                selector = self._generate_selector(target)
                pw_action["playwright_command"] = f'page.fill("{selector}", "{value}")'
                pw_action["selector_strategy"] = selector
                
            elif action_type == "wait":
                # Extract wait time if present
                time_match = re.search(r'(\d+)', str(target))
                wait_time = time_match.group(1) if time_match else "1000"
                pw_action["playwright_command"] = f'page.wait_for_timeout({wait_time})'
                
            elif action_type == "verify":
                # Generate assertion
                if "title" in target.lower():
                    pw_action["playwright_command"] = f'assert "{value}" in page.title()'
                elif "text" in target.lower() or "contains" in target.lower():
                    pw_action["playwright_command"] = f'assert page.locator("body").inner_text().__contains__("{value}")'
                else:
                    selector = self._generate_selector(target)
                    pw_action["playwright_command"] = f'assert page.locator("{selector}").is_visible()'
                    
            elif action_type == "screenshot":
                filename = value if value else "screenshot.png"
                pw_action["playwright_command"] = f'page.screenshot(path="{filename}")'
                
            elif action_type == "scroll":
                pw_action["playwright_command"] = 'page.evaluate("window.scrollTo(0, document.body.scrollHeight)")'
            
            playwright_actions.append(pw_action)
        
        return playwright_actions
    
    def _generate_selector(self, target: str) -> str:
        """
        Generate appropriate CSS/text selector for a target element
        
        Args:
            target: Element description (e.g., "login button", "username field")
            
        Returns:
            Playwright selector string
        """
        
        target_lower = target.lower()
        
        # Button detection
        if "button" in target_lower:
            # Extract button text/name
            text = target_lower.replace("button", "").strip()
            if text:
                return f'button:has-text("{text}")'
            return 'button'
        
        # Input field detection
        if any(keyword in target_lower for keyword in ["field", "input", "textbox", "box"]):
            # Try to identify by placeholder or label
            field_name = re.sub(r'\s*(field|input|textbox|box)\s*', '', target_lower).strip()
            if field_name:
                # Try multiple strategies
                return f'input[placeholder*="{field_name}" i], input[name*="{field_name}"], input[id*="{field_name}"]'
            return 'input'
        
        # Link detection
        if "link" in target_lower:
            text = target_lower.replace("link", "").strip()
            if text:
                return f'a:has-text("{text}")'
            return 'a'
        
        # Checkbox/Radio detection
        if "checkbox" in target_lower:
            return 'input[type="checkbox"]'
        if "radio" in target_lower:
            return 'input[type="radio"]'
        
        # Default: use text content matching
        return f'text="{target}"'


# Utility function for quick testing
def test_parser():
    """Test the instruction parser"""
    parser = InstructionParser()
    
    test_cases = [
        "Go to https://demo.playwright.dev/todomvc",
        "Click the new todo input",
        "Type 'Buy groceries' in the todo field",
        "Press Enter",
        "Verify the todo item appears",
        "Take a screenshot"
    ]
    
    print("=== Testing Instruction Parser ===\n")
    for instruction in test_cases:
        result = parser.parse_instruction(instruction)
        print(f"Input: {instruction}")
        print(f"Parsed: {json.dumps(result, indent=2)}\n")


if __name__ == "__main__":
    test_parser()
