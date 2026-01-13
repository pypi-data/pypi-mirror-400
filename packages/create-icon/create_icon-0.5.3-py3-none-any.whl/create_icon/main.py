# create_icon/__main__.py

from .create_icon import create_icon, get_icon_path

def main() -> None:
    # Step 1: generate icon (print path)
    path = create_icon(force=False, quiet=False)
    # Step 2: also show resolved path helper
    print(f"Resolved icon path: {get_icon_path()}")

if __name__ == "__main__":
    main()
