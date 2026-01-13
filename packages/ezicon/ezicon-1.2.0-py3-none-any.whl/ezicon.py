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

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def find_python_interpreter(script_path):
    """Searches for a virtual environment (.venv, venv, env) up the directory tree."""
    search_dir = os.path.dirname(os.path.abspath(script_path))
    venv_names = ['.venv', 'venv', 'env']
    
    # Search up to 4 levels or until root
    for _ in range(5):
        for venv in venv_names:
            possible_venv = os.path.join(search_dir, venv)
            if os.path.isdir(possible_venv):
                # Windows venv structure
                py_exe = os.path.join(possible_venv, "Scripts", "python.exe")
                if os.path.exists(py_exe):
                    return py_exe
        
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent
        
    return sys.executable

def create_link(target_script_path, custom_name=None, icon_path=None, desktop=False, force_console=False, python_exe=None):
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

    if desktop:
        location = get_desktop_path()
    else:
        location = get_start_menu_path()
        
    shortcut_path = os.path.join(location, f"{script_name}.lnk")

    # Check if shortcut already exists
    if os.path.exists(shortcut_path):
        while True:
            choice = input(f"Shortcut '{script_name}.lnk' already exists in {('Desktop' if desktop else 'Start Menu')}. Overwrite? (y/n): ").lower()
            if choice in ['n', 'no']:
                print("Operation cancelled.")
                return
            if choice in ['y', 'yes']:
                break

    # Python Interpreter selection
    base_python = python_exe if python_exe else find_python_interpreter(target_script)
    python_dir = os.path.dirname(base_python)
    
    if base_python != sys.executable:
        print(f"Using environment: {os.path.dirname(python_dir)}")

    # GUI Detection & pythonw selection
    if is_gui_application(target_script) and not force_console:
        print(f"Detected GUI/Tkinter in '{script_name}': Hiding console window...")
        pythonw_exe = os.path.join(python_dir, "pythonw.exe")
        python_exe_to_use = pythonw_exe if os.path.exists(pythonw_exe) else base_python
    else:
        if force_console:
            print(f"Forcing console mode for '{script_name}'...")
        else:
            print(f"Detected Console App in '{script_name}': Keeping console window...")
        python_exe_to_use = base_python

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        
        shortcut.Targetpath = python_exe_to_use
        shortcut.Arguments = f'"{target_script}"'
        shortcut.WorkingDirectory = os.path.dirname(target_script)
        shortcut.IconLocation = icon_path if icon_path else python_exe_to_use
        
        # --- IMPORTANT: Tag the shortcut so we can clean it later ---
        shortcut.Description = EZICON_TAG 
        # -----------------------------------------------------------
        
        shortcut.save()
        print(f"Success! Shortcut created: '{script_name}'")
        print(f"Location: {shortcut_path}")
        
    except Exception as e:
        print(f"Error creating shortcut: {e}")

def create_shell_command(target_script_path, command_name, python_exe=None):
    target_script = os.path.abspath(target_script_path)
    if not os.path.exists(target_script):
        print(f"Error: File '{target_script}' not found.")
        return

    # Python Interpreter selection
    base_python = python_exe if python_exe else find_python_interpreter(target_script)

    # Determine Scripts folder
    python_dir = os.path.dirname(sys.executable)
    scripts_dir = os.path.join(python_dir, "Scripts")
    if not os.path.exists(scripts_dir):
        scripts_dir = python_dir

    bat_path = os.path.join(scripts_dir, f"{command_name}.bat")

    if os.path.exists(bat_path):
        while True:
            choice = input(f"Command '{command_name}' already exists at {bat_path}. Overwrite? (y/n): ").lower()
            if choice in ['n', 'no']:
                print("Operation cancelled.")
                return
            if choice in ['y', 'yes']:
                break

    try:
        with open(bat_path, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f":: {EZICON_TAG}\n")
            f.write(f'"{base_python}" "{target_script}" %*\n')
        print(f"Success! Shell command created: '{command_name}'")
        print(f"Location: {bat_path}")
    except Exception as e:
        print(f"Error creating shell command: {e}")

def list_shortcuts():
    """Lists all shortcuts and shell commands created by ezicon."""
    start_menu = get_start_menu_path()
    desktop = get_desktop_path()
    shell = win32com.client.Dispatch("WScript.Shell")
    
    found_shortcuts = []
    for folder in [start_menu, desktop]:
        for file_path in glob.glob(os.path.join(folder, "*.lnk")):
            try:
                shortcut = shell.CreateShortCut(file_path)
                if shortcut.Description == EZICON_TAG:
                    loc = "Desktop" if folder == desktop else "Start Menu"
                    found_shortcuts.append(f"{os.path.basename(file_path)} ({loc})")
            except Exception:
                continue

    # Check for shell commands
    found_commands = []
    python_dir = os.path.dirname(sys.executable)
    scripts_dir = os.path.join(python_dir, "Scripts")
    if not os.path.exists(scripts_dir):
        scripts_dir = python_dir
    
    for file_path in glob.glob(os.path.join(scripts_dir, "*.bat")):
        try:
            with open(file_path, 'r') as f:
                if EZICON_TAG in f.read():
                    found_commands.append(os.path.basename(file_path))
        except Exception:
            continue

    if not found_shortcuts and not found_commands:
        print("No ezicon shortcuts or commands found.")
        return

    if found_shortcuts:
        print(f"\nFound {len(found_shortcuts)} shortcut(s) created by ezicon:")
        for sc in found_shortcuts:
            print(f" - {sc}")
    
    if found_commands:
        print(f"\nFound {len(found_commands)} shell command(s) created by ezicon:")
        for cmd in found_commands:
            print(f" - {cmd}")

def delete_item(name):
    """Deletes a specific shortcut or shell command by name."""
    start_menu = get_start_menu_path()
    desktop = get_desktop_path()
    shell = win32com.client.Dispatch("WScript.Shell")
    
    # Normalize name (remove extension if provided)
    base_name = os.path.splitext(name)[0]
    
    deleted_count = 0
    
    # Check Shortcuts in both locations
    for folder in [start_menu, desktop]:
        shortcut_path = os.path.join(folder, f"{base_name}.lnk")
        if os.path.exists(shortcut_path):
            try:
                shortcut = shell.CreateShortCut(shortcut_path)
                if shortcut.Description == EZICON_TAG:
                    os.remove(shortcut_path)
                    loc = "Desktop" if folder == desktop else "Start Menu"
                    print(f"Deleted shortcut '{base_name}' from {loc}.")
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting shortcut {shortcut_path}: {e}")

    # Check Shell Commands
    python_dir = os.path.dirname(sys.executable)
    scripts_dir = os.path.join(python_dir, "Scripts")
    if not os.path.exists(scripts_dir):
        scripts_dir = python_dir
    
    bat_path = os.path.join(scripts_dir, f"{base_name}.bat")
    if os.path.exists(bat_path):
        is_ezicon = False
        try:
            with open(bat_path, 'r') as f:
                if EZICON_TAG in f.read():
                    is_ezicon = True
            
            if is_ezicon:
                os.remove(bat_path)
                print(f"Deleted shell command '{base_name}'.")
                deleted_count += 1
        except Exception as e:
            print(f"Error deleting shell command {bat_path}: {e}")

    if deleted_count == 0:
        print(f"No ezicon item found with name '{base_name}'.")

def clean_shortcuts():
    """Scans start menu, desktop, and scripts for ezicon items and asks to delete them."""
    start_menu = get_start_menu_path()
    desktop = get_desktop_path()
    shell = win32com.client.Dispatch("WScript.Shell")
    
    found_files = []
    
    # Shortcuts
    for folder in [start_menu, desktop]:
        for file_path in glob.glob(os.path.join(folder, "*.lnk")):
            try:
                shortcut = shell.CreateShortCut(file_path)
                if shortcut.Description == EZICON_TAG:
                    found_files.append(file_path)
            except Exception:
                continue

    # Shell commands
    python_dir = os.path.dirname(sys.executable)
    scripts_dir = os.path.join(python_dir, "Scripts")
    if not os.path.exists(scripts_dir):
        scripts_dir = python_dir
    
    for file_path in glob.glob(os.path.join(scripts_dir, "*.bat")):
        try:
            with open(file_path, 'r') as f:
                if EZICON_TAG in f.read():
                    found_files.append(file_path)
        except Exception:
            continue

    if not found_files:
        print("No ezicon items found to clean.")
        return

    print(f"\nFound {len(found_files)} item(s) created by ezicon:")
    for f in found_files:
        print(f" - {os.path.basename(f)}")

    # Confirmation Prompt
    while True:
        choice = input("\nAre you sure you want to delete these items? (y/n): ").lower()
        if choice in ['y', 'yes']:
            count = 0
            for f in found_files:
                try:
                    os.remove(f)
                    count += 1
                except Exception as e:
                    print(f"Failed to delete {os.path.basename(f)}: {e}")
            print(f"\nClean up complete. Deleted {count} items.")
            break
        elif choice in ['n', 'no']:
            print("Operation cancelled.")
            break

def main():
    parser = argparse.ArgumentParser(description="Create or clean Windows shortcuts and shell commands for Python scripts.")
    
    # Flags
    parser.add_argument("--clean", action="store_true", help="Remove all items created by this tool")
    parser.add_argument("--delete", help="Delete a specific shortcut or shell command by name")
    parser.add_argument("-l", "--list", action="store_true", help="List all items created by this tool")
    parser.add_argument("-f", "--file", help="Path to the python file")
    parser.add_argument("-n", "--name", help="Custom name for the shortcut icon")
    parser.add_argument("-i", "--icon", help="Path to a .ico file for the shortcut icon")
    parser.add_argument("-d", "--desktop", action="store_true", help="Create shortcut on the Desktop")
    parser.add_argument("-c", "--force-console", action="store_true", help="Always use python.exe (shows console) even for GUI apps")
    parser.add_argument("-p", "--python", help="Path to a specific python executable to use")
    parser.add_argument("-T", "--terminal", help="Create a shell command (batch file) with the given name")
    
    # Positionals
    parser.add_argument("pos_file", nargs='?', help="Path to the python file (positional)")
    parser.add_argument("pos_name", nargs='?', help="Custom name for the shortcut icon (positional)")

    args = parser.parse_args()

    # Priority 1: Cleaning
    if args.clean:
        clean_shortcuts()
        return

    # Priority 2: Deleting specific item
    if args.delete:
        delete_item(args.delete)
        return

    # Priority 3: Listing
    if args.list:
        list_shortcuts()
        return

    # Priority 3: Creating
    target_file = args.file if args.file else args.pos_file
    target_name = args.name if args.name else args.pos_name
    icon_file = args.icon

    if not target_file:
        if not any([args.clean, args.list]):
            parser.print_help()
        return

    if args.terminal:
        create_shell_command(target_file, args.terminal, args.python)
    
    # If -T is used, we might still want a shortcut if -d or other flags are present
    # but usually -T is a separate thing. Let's allow both if requested.
    if not args.terminal or args.desktop or target_name or icon_file:
        # If -T was used but no other shortcut-specific flags, we might skip create_link
        # unless the user explicitly wants it. 
        # For now, if -T is NOT used, we always try to create a link.
        # If -T IS used, we only create a link if other shortcut flags are present.
        if not args.terminal:
            create_link(target_file, target_name, icon_file, args.desktop, args.force_console, args.python)
        elif args.desktop or target_name or icon_file:
            create_link(target_file, target_name, icon_file, args.desktop, args.force_console, args.python)

if __name__ == "__main__":
    main()