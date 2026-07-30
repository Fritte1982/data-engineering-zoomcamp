from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output"





test_dir = OUTPUT_DIR
def main():
    if test_dir.exists():
        print("test_dir exists"+ f"\n{test_dir}")

if __name__ == '__main__':
    main()