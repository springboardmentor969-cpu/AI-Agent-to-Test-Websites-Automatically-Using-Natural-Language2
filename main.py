from workflow import graph

print("Enter your test instructions (press Enter after each step).")
print("Type DONE when finished.\n")

lines = []

while True:
    line = input()
    if line.upper() == "DONE":
        break
    lines.append(line)

instruction = "\n".join(lines)

result = graph.invoke({"instruction": instruction})

print("\nParsed Actions:")
print(result)