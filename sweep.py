import os
import shutil
import argparse

def organize_folder(path: str, dry_run: bool = False) -> None:
    
    FILE_EXTENSIONS = {
        "Images" : [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"],
        "Videos" : [".mp4", ".mkv", ".mov", ".avi"],
        "Documents" : [".md", ".txt", ".pdf", ".docx", ".pptx", ".csv"],
        "Archives" : [".zip", ".7z", ".rar", ".tar"],
        "Executables": [".exe", ".msi", ".sh", ".bat"],
        "Music": [".mp3", ".wav"]
    }

    # change working directory
    os.chdir(path)

    for file in os.listdir():

        # ignore directories and script
        if file == "sweep.py" or os.path.isdir(file): continue

        # get file extension
        _, extension = os.path.splitext(file)
        extension = extension.lower()

        category_found = False
        for category, ext_list in FILE_EXTENSIONS.items():

            if extension in ext_list:

                if dry_run:
                    print(f"[Dry Run] Would move: {file} -> {category}")
                    category_found = True
                    break
                else:
                    # validate if folder already exist
                    if not os.path.exists(category):
                        os.makedirs(category)
                    
                    shutil.move(file, os.path.join(category, file))

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

                shutil.move(file, os.path.join('Others', file))
                print(f"Moved: {file} -> Others")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Organize your files into categorized folders.")

    parser.add_argument("path", nargs="?", default=".", help="Target directory path (default: current)") # path to the target directory
    parser.add_argument("--dry-run", action="store_true", help="Simulate the organization without making changes") # dry run option

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: The path '{args.path}' does not exist.")
        exit(1)

    mode_label = " (DRY RUN MODE)" if args.dry_run else ""

    print(f"--- Organizing: {os.path.abspath(args.path)}{mode_label} ---")

    organize_folder(args.path, dry_run=args.dry_run)

    if not args.dry_run:
        print("\nCompleted. Folder organized.")
    else:
        print("\nDry run completed. No changes were made.")