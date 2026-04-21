from pathlib import Path


current_dir = Path().cwd()
current_file = Path(__file__)

for item in current_dir.iterdir():
    if item == current_file:
        continue
    print(f"  - {item.name}")
    if item.is_file():
        content = item.read_text("utf-8")
        print(f"-----\ncontent:\n {content}")