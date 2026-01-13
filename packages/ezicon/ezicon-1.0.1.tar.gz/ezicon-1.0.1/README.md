# ezicon

A simple tool to create Windows Start Menu shortcuts for Python scripts.

## Installation
```bash
pip install ezicon
```

## Usage

### Basic Usage
Create a shortcut for your script in the Start Menu:
```bash
ezicon my_script.py
```

### Custom Name
Specify a custom name for the shortcut:
```bash
ezicon my_script.py "My Awesome App"
```

### Clean Up
Remove all shortcuts created by `ezicon`:
```bash
ezicon --clean
```

After creating the program icon, you can execute your python script from the Start Menu.