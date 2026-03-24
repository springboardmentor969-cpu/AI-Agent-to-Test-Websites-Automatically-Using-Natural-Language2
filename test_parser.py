import sys
sys.path.insert(0, '.')
from parser.instruction_parser import parse_instruction

text1 = "Go to YouTube and search for lofi music"
print("Test 1:")
print(parse_instruction(text1))

text2 = "Open localhost:5000/sample, type admin as username and password123 as password, click login"
print("\nTest 2:")
print(parse_instruction(text2))
