from pathlib import Path

current_dir = Path().cwd()
current_file = Path(__file__)

for item in current_dir.iterdir():
    if item == current_file:
        continue

    print(f"  - {item.name}")

    if item.is_file():
        content = None

        for enc in ("utf-8-sig", "utf-16", "utf-8"):
            try:
                content = item.read_text(encoding=enc)
                break
            except UnicodeDecodeError:
                continue

        print("-----\ncontent:\n", content)