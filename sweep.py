import os
import shutil
import argparse
import fnmatch
import json
from tqdm import tqdm

DEFAULT_UNDO_LOG = ".sweep_undo.log"


def load_config():
    default_config = {
        "categories": {
            "Images" : [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"],
            "Videos" : [".mp4", ".mkv", ".mov", ".avi"],
            "Documents" : [".md", ".txt", ".pdf", ".docx", ".pptx", ".csv"],
            "Archives" : [".zip", ".7z", ".rar", ".tar"],
            "Executables": [".exe", ".msi", ".sh", ".bat"],
            "Music": [".mp3", ".wav"]
        }, "settings" : {
            "undo_log_filename": DEFAULT_UNDO_LOG
        }
    }
    
    config_path = "sweep_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)

                if "categories" in user_config:
                    default_config["categories"] = user_config["categories"]
                if "settings" in user_config:
                    default_config["settings"].update(user_config["settings"])
        except Exception as e:
            print(f"Warning: Could not read config file, using defaults. {e}")
            
    return default_config

def save_undo_log(path, moves, undo_log) -> None:
    """Saves all move information to the undo log in the target directory."""
    if not moves:
        return
        
    log_path = os.path.join(path, undo_log)
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(moves, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save undo log: {e}")

def get_unique_path(destination_folder, filename) -> str:
    """Generates a unique filename if a conflict exists."""
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_path = os.path.join(destination_folder, filename)
    
    while os.path.exists(unique_path):
        unique_filename = f"{base}_{counter}{extension}"
        unique_path = os.path.join(destination_folder, unique_filename)
        counter += 1
        
    return unique_path

def undo_last_organize(path: str, undo_log: str) -> None:
    """Reverts the last organization based on the undo log."""

    log_path = os.path.join(path, undo_log)
    
    if not os.path.exists(log_path):
        print("No undo log found. Nothing to revert.")
        return
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        
        if not entries:
            print("Undo log is empty.")
            return
        
        print(f"Reverting {len(entries)} file moves...")
        
        for entry in tqdm(reversed(entries), desc="Reverting moves", unit="file"):
            original = entry["original"]
            moved_to = entry["moved_to"]
            
            if not os.path.exists(moved_to):
                print(f"Skipped (already missing): {moved_to}")
                continue
            
            # ensure original directory exists
            os.makedirs(os.path.dirname(original), exist_ok=True)
            
            # conflict resolution
            if os.path.exists(original):
                base, ext = os.path.splitext(original)
                counter = 1
                new_original = original
                while os.path.exists(new_original):
                    new_original = f"{base}_restored_{counter}{ext}"
                    counter += 1
                print(f"Name conflict - restoring as: {os.path.basename(new_original)}")
                original = new_original
            
            shutil.move(moved_to, original)
            print(f"Restored: {os.path.basename(moved_to)} → {os.path.basename(original)}")
        
        # after undoing all moves remove the log file
        os.remove(log_path)
        print("\nUndo completed. Log file removed.")
        
    except Exception as e:
        print(f"Error during undo: {e}")

def organize_folder(path: str, categories: dict, undo_log: str, dry_run: bool = False, handle_config: bool = False, use_gitignore: bool = False) -> None:
    """Organizes files in the specified folder into categorized subfolders."""

    moves = []
    

    # change working directory
    os.chdir(path)

    all_items = os.listdir()
    files_to_process = [f for f in all_items if os.path.isfile(f) and f != "sweep.py"]

    # load patterns from .gitignore if requested
    gitignore_patterns = []
    if use_gitignore and os.path.exists(".gitignore"):
        with open(".gitignore", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                gitignore_patterns.append(line.rstrip("/"))

    def is_ignored_by_gitignore(name: str) -> bool:
        if not gitignore_patterns:
            return False
        return any(fnmatch.fnmatch(name, pattern) for pattern in gitignore_patterns)

    for file in tqdm(files_to_process, desc="Organizing files", unit="file"):

        # ignore directories and script itself
        if file == "sweep.py" or os.path.isdir(file):
            continue

        # handle hidden/config files (dotfiles)
        if file.startswith("."):
            if handle_config:
                if dry_run:
                    print(f"[Dry Run] Would move config: {file} -> Config")
                else:
                    if not os.path.exists("Config"):
                        os.makedirs("Config")

                    dest_path = get_unique_path("Config", file)
                    moves.append({
                        "original": os.path.abspath(file),
                        "moved_to": os.path.abspath(dest_path)
                    })
                    shutil.move(file, dest_path)
                    print(f"Moved config: {file} -> Config")

            # if not handling config, just skip dotfiles
            continue

        # skip files ignored via .gitignore (if enabled)
        if is_ignored_by_gitignore(file):
            if dry_run:
                print(f"[Dry Run] Ignored by .gitignore: {file}")
            continue

        # get file extension
        _, extension = os.path.splitext(file)
        extension = extension.lower()

        category_found = False
        for category, ext_list in categories.items():

            if extension in ext_list:

                if dry_run:
                    print(f"[Dry Run] Would move: {file} -> {category}")
                    category_found = True
                    break
                else:
                    # validate if folder already exist
                    if not os.path.exists(category):
                        os.makedirs(category)
                    
                    dest_path = get_unique_path(category, file)
                    moves.append({
                        "original": os.path.abspath(file),
                        "moved_to": os.path.abspath(dest_path)
                    })
                    shutil.move(file, dest_path)

                    # log changes
                    print(f"Moved: {file} -> {category}")
                    category_found = True
                    break
        
        # move rest of files to "Others" folder
        if not category_found:

            if dry_run:
                print(f"[Dry Run] Would move: {file} -> Others")
                continue

            else:

                if not os.path.exists('Others'):
                    os.makedirs('Others')

                dest_path = get_unique_path("Others", file)
                moves.append({
                    "original": os.path.abspath(file),
                    "moved_to": os.path.abspath(dest_path)
                })
                shutil.move(file, dest_path)
                print(f"Moved: {file} -> Others")

    if not dry_run and moves:
        save_undo_log(".", moves, undo_log)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Organize your files into categorized folders.")

    default_home = os.path.expanduser("~")
    parser.add_argument("path", nargs="?", default=default_home, help="Target directory path (default: current)") # path to the target directory
    parser.add_argument("--dry-run", action="store_true", help="Simulate the organization without making changes") # dry run option
    parser.add_argument("--config", action="store_true", help="Also organize hidden config files (dotfiles) into 'Config' folder") # handle config files option
    parser.add_argument("--gitignore", action="store_true", help="Ignore files matching patterns from .gitignore in the target directory") # use .gitignore patterns
    parser.add_argument("--undo", action="store_true", help="Revert the last organization based on the undo log") # undo option

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: The path '{args.path}' does not exist.")
        exit(1)

    config = load_config()
    categories = config["categories"]
    undo_log_name = config["settings"]["undo_log_filename"]
    
    os.chdir(args.path)

    if args.undo:
        print(f"--- Undoing last organization in: {os.path.abspath(args.path)} ---")
        undo_last_organize(args.path, undo_log_name)
        exit(0)

    mode_label = " (DRY RUN MODE)" if args.dry_run else ""
    print(f"--- Organizing: {os.path.abspath(args.path)}{mode_label} ---")

    organize_folder(args.path, categories, undo_log_name, dry_run=args.dry_run, handle_config=args.config, use_gitignore=args.gitignore)

    if not args.dry_run:
        print("\nCompleted. Folder organized.")
    else:
        print("\nDry run completed. No changes were made.")