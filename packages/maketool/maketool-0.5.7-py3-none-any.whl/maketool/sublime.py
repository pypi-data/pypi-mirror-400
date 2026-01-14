import os
import sys
import argparse
import json
import shutil


def process(user_packages_dir: str):
    """
    Update Pythonw.sublime-build in a Sublime Text 4 installation so that maketool python build will work when F7 pressed.
    
    Parameters:
        user_packages_dir (str): Path to the 'Packages/User' folder.
        Example: r"C:/alan/app/sublime text 4/Data/Packages/User"
    """

    if user_packages_dir is None:
        print("Error: sublime_text user_packages_dir must be provided.")
        sys.exit()

    keymap_file_path = os.path.join(user_packages_dir, "Default (Windows).sublime-keymap")
    keymap_config = [
        {
            "keys": ["f1"],
            "command": "run_macro_file",
            "args": {"file": "Packages/User/print-python.sublime-macro"},
            "context": [{"key": "selector", "operator": "equal", "operand": "source.python"}]
        },
        {
            "keys": ["ctrl+backspace"],
            "command": "run_macro_file",
            "args": {"file": "res://Packages/Default/Delete Line.sublime-macro"}
        },
        {
            "keys": ["ctrl+alt+e"],
            "command": "open_dir",
            "args": {"dir": "$file_path", "file": "$file_name"}
        },
        {
            "keys": ["f5"],
            "command": "build",
            "args": {"variant": "pyflakes"}
        },
        {
            "keys": ["ctrl+0"],
            "command": "reset_font_size"
        },

        {   
            "keys": ["f10"],
            "command": "insert_date" 
        }
    ]


    # Backup existing keymap if it exists
    if os.path.exists(keymap_file_path):
        backup_path = keymap_file_path + ".bak"
        shutil.copy2(keymap_file_path, backup_path)
        print(f"Backed up existing keymap to {backup_path}")

    # Write the new keymap file
    with open(keymap_file_path, "w", encoding="utf-8") as f:
        json.dump(keymap_config, f, indent=4)

    print(f"Updated Sublime Text: {keymap_file_path}")




    build_file_path = os.path.join(user_packages_dir, "Pythonw.sublime-build")
    maketool_build_config = {
        "selector": "source.python",
        "shell": True,
        "working_dir": "${file_path}",
        "cmd": ["maketool-run", "$file"],
        "file_regex": "File \"(.*)\", line (.*)",
        "variants": [
            {
                "cmd": ["maketool-build", "${file}"],
                "name": "build",
                "shell": True
            },
            {
                "cmd": ["maketool-clean"],
                "name": "clean",
                "shell": True
            },
            {
                "cmd": ["pyflakes", "${file}"],
                "file_regex": "^(.*?):(\\d+):(\\d+): ([^\\n]+)",
                "name": "pyflakes",
                "shell": True
            },
            {
                "name": "print",
                "command": "run_macro_file",
                "args": {"file": "Packages/User/print.sublime-macro"}
            }
        ]
    }

    # Backup existing file if it exists
    if os.path.exists(build_file_path):
        backup_path = build_file_path + ".bak"
        shutil.copy2(build_file_path, backup_path)
        print(f"Backed up existing file to {backup_path}")

    # Ensure directory exists
    print(f"user_packages_dir = {user_packages_dir}")
    os.makedirs(user_packages_dir, exist_ok=True)
    
    # Write the new build file
    with open(build_file_path, "w", encoding="utf-8") as f:
        json.dump(maketool_build_config, f, indent=4)

    print(f"Updated Sublime Text: {build_file_path}")



def main():

    #------------------------------------
    # parse command line for path argument and value
    #------------------------------------
    # parser = argparse.ArgumentParser(
    #     description="Setup Sublime Text for maketool integration."
    # )
    # parser.add_argument(
    #     "--path",
    #     required=True,
    #     help=r"Path to Sublime Text folder, e.g. C:\alan\app\sublime text 4",
    # )
    # args = parser.parse_args()
    # user_packages_dir = os.path.normpath(args.path)

    user_packages_dir = os.path.normpath(r"C:\alan\app\sublime text 4")

    process(user_packages_dir)

    print("Sublime Text setup complete!")


if __name__ == "__main__":

    main()   