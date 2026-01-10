import os
import shutil

def organize_folder(path: str) -> None:
    
    FILE_EXTENSIONS = {
        "Images" : [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"],
        "Videos" : [".mp4", ".mkv", ".mov", ".avi"],
        "Documents" : [".md", ".txt", ".pdf", ".docx", ".pptv", ".csv"],
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

            if not os.path.exists('Others'):
                os.makedirs('Others')

            shutil.move(file, os.path.join('Others', file))
            print(f"Moved: {file} -> Others")

if __name__ == "__main__":
    target_path = "." 
    organize_folder(target_path)
    print("\nCompleted. Folder organized.")