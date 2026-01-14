import os
import re
import argparse
import json
from pathlib import Path

HISTORY_FILE = Path.home() / ".renameit_history.json"


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_history():
    if not HISTORY_FILE.exists():
        print("No rename history found.")
        # return None

        with open(HISTORY_FILE, "r") as f:
            return json.load(f)


def rename_data(abs_path: str, data: list, name: str = None):
    renamed_history = []

    try:
        for i, filename in enumerate(data, 1):
            old_path = os.path.join(abs_path, filename)
            _, ext = os.path.splitext(filename)

            new_name = f"{i}_{name}{ext}" if name else f"{i}{ext}"
            new_path = os.path.join(abs_path, new_name)

            os.rename(old_path, new_path)
            renamed_history.append([old_path, new_path])

        save_history(renamed_history)

    except Exception as e:
        print(f"Error: {e}")
        print("Reverting...")
        for old, new in reversed(renamed_history):
            if os.path.exists(new):
                os.rename(new, old)
        raise


def rename_logic(path: str, files_name: str = None, folders_name: str = None):
    abs_path = os.path.abspath(path)

    data = os.listdir(abs_path)
    data.sort(
        key=lambda s: [
            int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", s)
        ]
    )

    files = []
    folders = []

    for item in data:
        full = os.path.join(abs_path, item)
        if os.path.isfile(full):
            files.append(item)
        elif os.path.isdir(full):
            folders.append(item)

    if files:
        print("Renaming files...")
        rename_data(abs_path, files, files_name)

    if folders:
        print("Renaming folders...")
        rename_data(abs_path, folders, folders_name)

    print("Done!")


def undo():
    history = load_history()
    if not history:
        return

    for old, new in reversed(history):
        if os.path.exists(new):
            os.rename(new, old)

    HISTORY_FILE.unlink()
    print("Undo completed.")


def main():
    parser = argparse.ArgumentParser(description="Rename files and folders")

    subparsers = parser.add_subparsers(dest="command")

    rename_parser = subparsers.add_parser("rename")
    rename_parser.add_argument("-pt", "--path", required=True)
    rename_parser.add_argument("-fl", "--files-name")
    rename_parser.add_argument("-fd", "--folders-name")

    subparsers.add_parser("undo")

    args = parser.parse_args()

    if args.command == "rename":
        rename_logic(args.path, args.files_name, args.folders_name)
    elif args.command == "undo":
        undo()
    else:
        parser.print_help()
