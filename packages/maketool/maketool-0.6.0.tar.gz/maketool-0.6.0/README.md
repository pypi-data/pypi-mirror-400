# 🛠️ maketool

**maketool** is a command-line utility and helper module that simplifies execution and building [PySide6](https://doc.qt.io/qtforpython/) Python 3.7+ applications into executables using **PyInstaller 5.8.0**.

It's especially useful for GUI projects that need embedded resources (e.g., `.ui`, `.qrc`) and aim to produce portable `.exe` builds with minimal setup.

---

## ❤️ Why Use maketool?

If you build windows desktop apps using PySide6 or PyQt, `maketool`:

- Saves time when converting `.ui` and `.qrc` files
- Simplifies PyInstaller builds
- Packages your application with minimal commands
- Automates repetitive tasks like building and cleanup
- Integrates easily with `.bat` scripts or shell commands
- Is great for both beginners and advanced developers using PySide6

---

## 🔧 Commands

### 1. `run`

Executes the Python program after recursively builds all `.ui` and `.qrc` files in the current directory and subdirectories using `pyside6-uic.exe` and `pyside6-rcc.exe`.  Then run python source code.

Note: it will ONLY rebuild pyside components that are out of date, so that execution is fast as possible, yet always includes any changes.
FYI: python program is run with pythonw.exe so that the terminal window does not appear.

```cli
usage: maketool-run [-h] file

positional parameters:
  file        python file to run

parameters:
  -h, --help  show this help message and exit
```

### 2. `clean`

Removes temporary files and build artifacts, including:

- `__pycache__` folders  
- `*_ui.py`, `*_rc.py`, `*.pyc`, `*.pyo`  
- PyInstaller `build/` and `dist/` folders  
- `.spec` files in the current directory

Run it like this:

```cli
maketool-clean
```

### 3. `compile`

Builds your python app into an executable using PyInstaller.

- Compiles `.ui` and `.qrc` and image resources  
- Generates a PyInstaller `.spec` file  
- Runs PyInstaller with the provided options
- Updates __version__ if exists in python file with --version value if provided

```cli
usage: maketool-compile [-h] --file FILE --type {onefile,onedir,console} [--icon="myicon.ico"] [--embed="sqlite3.dll"]

parameters:
  -h, --help            show this help message and exit
  --file FILE           python file to compile to exe
  --type {onefile,onedir,console}
                        type of exe to build
  --icon ICON           ico file
  --embed EMBED         comma delimited list of files to embed
  --version VERSION     program version (otherwise use __version__ in py source)
```

### 4. `sublime`

Update local `Sublime Text 4` installation with these useful shortcuts:

F1 - insert print statement for variable where cursor is located
CTRL+BACKSPACE - delete line
CTRL+ALT+E - open windows explorer where current file is located
F5 - run pyflakes on current python source
CTRL+0 - reset font size
F10 - insert current date/day
F7 - maketool-run - build and run current python script

```cli
usage: maketool-sublime [-h] --path PATH

parameters:
  -h, --help            show this help message and exit
  --path PATH           sublime text - data/package/user path
```

---

## ✨ Features

- 💡 Simple command-line interface for `.bat` or `.sh` workflows 
- 🔄 Converts all `.ui` and `.qrc` files recursively
- 🧹 Cleans up Python build artifacts
- 📦 Packages apps using PyInstaller 
- 🛠️ Supports custom `.ico` icons  
- 📎 Supports optional resource embedding

---

## 📦 Requirements

- 🐍 [**Python 3.7+**](https://www.python.org/downloads/)
- 🪟 [**PySide6**](https://pypi.org/project/PySide6/)
- 📦 [**PyInstaller 5.8**](https://pypi.org/project/pyinstaller/)

---

## 📥 Installation

Install maketool helper from PyPI with following command:

```cli
pip install maketool
```

---

## 📝 License

MIT License  
© 2025 Alan Lilly  
