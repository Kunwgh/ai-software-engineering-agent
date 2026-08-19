from app.tools.registry import TOOLS


print("Available tools:")

for name in TOOLS:
    print("-", name)