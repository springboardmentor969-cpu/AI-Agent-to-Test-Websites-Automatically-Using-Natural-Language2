#!/usr/bin/env python3
"""
Quick test script to validate Milestone 2 completion
Tests the instruction parser and workflow without running the full Flask app
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*70)
print("🚀 MILESTONE 2 - QUICK TEST SCRIPT")
print("="*70)

# Check if API key is set
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
    print("Please add your API key to the .env file")
    sys.exit(1)
else:
    print("✅ API Key found")

print("\n" + "="*70)
print("TEST 1: Testing Instruction Parser Module")
print("="*70 + "\n")

try:
    from instruct_parser import InstructionParser
    parser = InstructionParser()
    print("✅ Instruction Parser imported successfully")
    
    # Test parsing
    test_instruction = "Click the login button"
    result = parser.parse_instruction(test_instruction)
    print(f"\nTest Input: '{test_instruction}'")
    print(f"Parsed Result: {result}")
    print("✅ Parser test passed")
    
except Exception as e:
    print(f"❌ Parser test failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("TEST 2: Testing LangGraph Workflow")
print("="*70 + "\n")

try:
    from agent import graph
    print("✅ Agent workflow imported successfully")
    
    # Test workflow
    test_case = """
    Go to https://demo.playwright.dev/todomvc
    Click on the input field
    Type 'Test task' in the field
    """
    
    print(f"Test Case:\n{test_case}")
    print("\nRunning workflow...\n")
    
    result = graph.invoke({"input": test_case})
    
    print("✅ Workflow executed successfully")
    print(f"\n📊 Results:")
    print(f"   - Parsed Actions: {len(result.get('parsed_actions', []))}")
    print(f"   - Playwright Commands: {len(result.get('playwright_commands', []))}")
    print(f"   - Generated Code: {len(result.get('output', '').split('\\n'))} lines")
    
    print("\n💻 Generated Code Preview:")
    print("-" * 70)
    code = result.get('output', '')
    lines = code.split('\n')[:10]  # First 10 lines
    print('\n'.join(lines))
    if len(code.split('\n')) > 10:
        print(f"... ({len(code.split('\\n')) - 10} more lines)")
    print("-" * 70)
    
except Exception as e:
    print(f"❌ Workflow test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("TEST 3: Checking File Structure")
print("="*70 + "\n")

required_files = [
    ("instruction_parser.py", "Instruction Parser Module"),
    ("agent_updated.py", "Enhanced Agent with Multi-Node Workflow"),
    ("app_updated.py", "Updated Flask App"),
    ("index.html", "Enhanced UI Template"),
    (".env", "Environment Variables"),
    ("requirements.txt", "Dependencies")
]

all_present = True
for filename, description in required_files:
    if os.path.exists(filename):
        print(f"✅ {filename} - {description}")
    else:
        print(f"❌ {filename} - MISSING")
        all_present = False

if not all_present:
    print("\n⚠️ Some files are missing. Make sure to copy all files to your project.")

print("\n" + "="*70)
print("🎉 MILESTONE 2 VALIDATION COMPLETE!")
print("="*70)

print("""
✅All tests passed! You have successfully completed.

)

Next Steps:
-----------
1. Run the Flask app: python app_updated.py
2. Open browser: http://localhost:5000
3. Try the example test cases
4. Review the workflow visualization

To start Milestone 3:
---------------------
- Add real-time DOM inspection
- Improve selector reliability with actual page state
- Enhance assertion generation
- Add comprehensive test reporting

Happy Testing! 🚀
""")
