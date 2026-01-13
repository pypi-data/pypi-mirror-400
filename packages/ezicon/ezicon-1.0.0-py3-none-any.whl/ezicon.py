import sys
import os
import argparse
import win32com.client
import glob

# This tag identifies shortcuts created by this tool
EZICON_TAG = "Created by ezicon"

def is_gui_application(file_path):
    if file_path.lower().endswith('.pyw'):
        return True
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            if 'tkinter' in content or 'from tkinter' in content:
                return True
    except Exception:
        pass
    return False

def get_start_menu_path():
    return os.path.join(os.environ['APPDATA'], r"Microsoft\Windows\Start Menu\Programs")

def create_link(target_script_path, custom_name=None, icon_path=None):
    target_script = os.path.abspath(target_script_path)
    
    if not os.path.exists(target_script):
        print(f"Error: File '{target_script}' not found.")
        return
    
    # Validate icon file if provided
    if icon_path:
        icon_path = os.path.abspath(icon_path)
        if not os.path.exists(icon_path):
            print(f"Error: Icon file '{icon_path}' not found.")
            return
        if not icon_path.lower().endswith('.ico'):
            print(f"Error: Icon file must be a .ico file, got '{os.path.splitext(icon_path)[1]}'")
            return

    if custom_name:
        script_name = custom_name
    else:
        script_name = os.path.splitext(os.path.basename(target_script))[0]

    start_menu = get_start_menu_path()
    shortcut_path = os.path.join(start_menu, f"{script_name}.lnk")

    # Check if shortcut already exists
    if os.path.exists(shortcut_path):
        while True:
            choice = input(f"Shortcut '{script_name}.lnk' already exists. Overwrite? (y/n): ").lower()
            if choice in ['n', 'no']:
                print("Operation cancelled.")
                return
            if choice in ['y', 'yes']:
                break

    python_dir = os.path.dirname(sys.executable)
    
    # GUI Detection
    if is_gui_application(target_script):
        print(f"Detected GUI/Tkinter in '{script_name}': Hiding console window...")
        python_exe = os.path.join(python_dir, "pythonw.exe")
    else:
        print(f"Detected Console App in '{script_name}': Keeping console window...")
        python_exe = sys.executable

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{target_script}"'
        shortcut.WorkingDirectory = os.path.dirname(target_script)
        shortcut.IconLocation = icon_path if icon_path else sys.executable
        
        # --- IMPORTANT: Tag the shortcut so we can clean it later ---
        shortcut.Description = EZICON_TAG 
        # -----------------------------------------------------------
        
        shortcut.save()
        print(f"Success! Shortcut created: '{script_name}'")
        print(f"Location: {shortcut_path}")
        
    except Exception as e:
        print(f"Error creating shortcut: {e}")

def clean_shortcuts():
    """Scans start menu for shortcuts with the PyIcon tag and asks to delete them."""
    start_menu = get_start_menu_path()
    shell = win32com.client.Dispatch("WScript.Shell")
    
    found_shortcuts = []
    
    print(f"Scanning {start_menu} for ezicon shortcuts...")
    
    # Iterate over all .lnk files in the directory
    for file_path in glob.glob(os.path.join(start_menu, "*.lnk")):
        try:
            shortcut = shell.CreateShortCut(file_path)
            # Check the metadata tag
            if shortcut.Description == EZICON_TAG:
                found_shortcuts.append(file_path)
        except Exception:
            continue

    if not found_shortcuts:
        print("No ezicon shortcuts found to clean.")
        return

    print(f"\nFound {len(found_shortcuts)} shortcut(s) created by ezicon:")
    for sc in found_shortcuts:
        print(f" - {os.path.basename(sc)}")

    # Confirmation Prompt
    while True:
        choice = input("\nAre you sure you want to delete these icons? (y/n): ").lower()
        if choice in ['y', 'yes']:
            count = 0
            for sc in found_shortcuts:
                try:
                    os.remove(sc)
                    count += 1
                except Exception as e:
                    print(f"Failed to delete {os.path.basename(sc)}: {e}")
            print(f"\nClean up complete. Deleted {count} icons.")
            break
        elif choice in ['n', 'no']:
            print("Operation cancelled.")
            break

def main():
    parser = argparse.ArgumentParser(description="Create or clean Windows Start Menu shortcuts for Python scripts.")
    
    # Flags
    parser.add_argument("--clean", action="store_true", help="Remove all icons created by this tool")
    parser.add_argument("-f", "--file", help="Path to the python file")
    parser.add_argument("-n", "--name", help="Custom name for the shortcut icon")
    parser.add_argument("-i", "--icon", help="Path to a .ico file for the shortcut icon")
    
    # Positionals
    parser.add_argument("pos_file", nargs='?', help="Path to the python file (positional)")
    parser.add_argument("pos_name", nargs='?', help="Custom name for the shortcut icon (positional)")

    args = parser.parse_args()

    # Priority 1: Cleaning
    if args.clean:
        clean_shortcuts()
        return

    # Priority 2: Creating
    target_file = args.file if args.file else args.pos_file
    target_name = args.name if args.name else args.pos_name
    icon_file = args.icon

    if not target_file:
        parser.print_help()
        return

    create_link(target_file, target_name, icon_file)

if __name__ == "__main__":
    main()