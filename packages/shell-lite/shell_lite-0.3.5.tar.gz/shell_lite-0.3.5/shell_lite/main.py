import sys
import os
import shutil
import urllib.request
import zipfile
import io
import subprocess
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .ast_nodes import *
import json
def execute_source(source: str, interpreter: Interpreter):
    lines = source.split('\n')
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        statements = parser.parse()
        for stmt in statements:
            interpreter.visit(stmt)
    except Exception as e:
        if hasattr(e, 'line') and e.line > 0:
            print(f"Error on line {e.line}:")
            if 0 <= e.line-1 < len(lines):
                print(f"  {lines[e.line-1].strip()}")
        print(f"Exception: {e}")
def run_file(filename: str):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    interpreter = Interpreter()
    execute_source(source, interpreter)
def run_repl():
    interpreter = Interpreter()
    print("\n" + "="*40)
    print("  ShellLite REPL - English Syntax")
    print("="*40)
    print("Version: v0.03.3 | Made by Shrey Naithani")
    print("Commands: Type 'exit' to quit, 'help' for examples.")
    print("Note: Terminal commands (like 'shl install') must be run in CMD/PowerShell, not here.")
    buffer = []
    indent_level = 0
    while True:
        try:
            prompt = "... " if indent_level > 0 else ">>> "
            line = input(prompt)
            if line.strip() == "exit":
                break
            if line.endswith("\\"):
                buffer.append(line[:-1])
                indent_level = 1
                continue
            if line.strip() == "help":
                print("\nShellLite Examples:")
                print('  say "Hello World"')
                print('  tasks is a list            # Initialize an empty list')
                print('  add "Buy Milk" to tasks    # Add items to the list')
                print('  display(tasks)             # View the list')
                print('  \\                          # Tip: Use \\ at the end of a line for multi-line typing')
                continue
            if line.strip().startswith("shl"):
                print("! Hint: You are already INSIDE ShellLite. You don't need to type 'shl' here.")
                print("! To run terminal commands, exit this REPL first.")
                continue
            if not line:
                if indent_level > 0:
                    source = "\n".join(buffer)
                    execute_source(source, interpreter)
                    buffer = []
                    indent_level = 0
                continue
            if line.strip().endswith(":"):
                indent_level = 1
                buffer.append(line)
            elif indent_level > 0 and (line.startswith(" ") or line.startswith("\t")):
                buffer.append(line)
            else:
                if indent_level > 0:
                     source = "\n".join(buffer)
                     execute_source(source, interpreter)
                     buffer = []
                     indent_level = 0
                if line.strip():
                    execute_source(line, interpreter)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            buffer = []
            indent_level = 0
def install_globally():
    print("\n" + "="*50)
    print("  ShellLite Global Installer")
    print("="*50)
    install_dir = os.path.join(os.environ['LOCALAPPDATA'], 'ShellLite')
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    target_exe = os.path.join(install_dir, 'shl.exe')
    current_path = sys.executable
    is_frozen = getattr(sys, 'frozen', False)
    try:
        if is_frozen:
            shutil.copy2(current_path, target_exe)
        else:
            print("Error: Installation requires the shl.exe file.")
            return
        ps_cmd = f'$oldPath = [Environment]::GetEnvironmentVariable("Path", "User"); if ($oldPath -notlike "*ShellLite*") {{ [Environment]::SetEnvironmentVariable("Path", "$oldPath;{install_dir}", "User") }}'
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        print(f"\n[SUCCESS] ShellLite is now installed!")
        print(f"Location: {install_dir}")
        print("\nACTION REQUIRED:")
        print("1. Close this terminal window.")
        print("2. Open a NEW terminal.")
        print("3. Type 'shl' to verify.")
        print("="*50 + "\n")
        input("Press Enter to continue...")
    except Exception as e:
        print(f"Installation failed: {e}")
def install_package(package_name: str):
    if '/' not in package_name:
        print("Error: Package must be in format 'user/repo'")
        return
    user, repo = package_name.split('/')
    print(f"Fetching '{package_name}' from GitHub...")
    home = os.path.expanduser("~")
    modules_dir = os.path.join(home, ".shell_lite", "modules")
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    target_dir = os.path.join(modules_dir, repo)
    if os.path.exists(target_dir):
        print(f"Removing existing '{repo}'...")
        shutil.rmtree(target_dir)
    zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"
    try:
        print(f"Downloading {zip_url}...")
        with urllib.request.urlopen(zip_url) as response:
            zip_data = response.read()
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            z.extractall(modules_dir)
        extracted_name = f"{repo}-main"
        extracted_path = os.path.join(modules_dir, extracted_name)
        if os.path.exists(extracted_path):
            os.rename(extracted_path, target_dir)
            print(f"[SUCCESS] Installed '{repo}' to {target_dir}")
        else:
             print(f"Error: Could not find extracted folder '{extracted_name}'.")
        return
    except urllib.error.HTTPError:
         zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/master.zip"
         try:
            print(f"Downloading {zip_url}...")
            with urllib.request.urlopen(zip_url) as response:
                zip_data = response.read()
            with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                z.extractall(modules_dir)
            extracted_name = f"{repo}-master"
            extracted_path = os.path.join(modules_dir, extracted_name)
            if os.path.exists(extracted_path):
                os.rename(extracted_path, target_dir)
                print(f"[SUCCESS] Installed '{repo}' to {target_dir}")
            else:
                 print(f"Error: Could not find extracted folder '{extracted_name}'.")
         except Exception as e:
              print(f"Installation failed: {e}")
    except Exception as e:
        print(f"Installation failed: {e}")
def compile_file(filename: str, target: str = 'python'):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return
    print(f"Compiling {filename} to {target.upper()}...")
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        from .parser import Parser
        from .lexer import Lexer
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        statements = parser.parse()
        if target.lower() == 'js':
            from .js_compiler import JSCompiler
            compiler = JSCompiler()
            code = compiler.compile(statements)
            ext = '.js'
        else:
            from .compiler import Compiler
            compiler = Compiler()
            code = compiler.compile(statements)
            ext = '.py'
        output_file = filename.replace('.shl', ext)
        if output_file == filename: output_file += ext
        with open(output_file, 'w') as f:
            f.write(code)
        print(f"[SUCCESS] Transpiled to {output_file}")
        if target.lower() == 'python':
            try:
                import PyInstaller.__main__
                print("Building Executable with PyInstaller...")
                PyInstaller.__main__.run([
                    output_file,
                    '--onefile',
                    '--name', os.path.splitext(os.path.basename(filename))[0],
                    '--log-level', 'WARN'
                ])
                print(f"[SUCCESS] Built {os.path.splitext(os.path.basename(filename))[0]}.exe")
            except ImportError:
                 pass 
    except Exception as e:
        print(f"Compilation Failed: {e}")
def lint_file(filename: str):
    if not os.path.exists(filename):
        print(json.dumps([{"line": 0, "message": f"File {filename} not found"}]))
        return
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse()
        print(json.dumps([]))
    except Exception as e:
        line = getattr(e, 'line', 1)
        print(json.dumps([{
            "line": line, 
            "message": str(e)
        }]))
def resolve_cursor(filename: str, line: int, col: int):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        nodes = parser.parse()
        target_token = None
        for t in tokens:
            if t.line == line:
                if t.column <= col <= t.column + len(t.value):
                    target_token = t
                    break
        if not target_token or target_token.type != 'ID':
             print(json.dumps({"found": False}))
             return
        word = target_token.value
        def find_def(n_list, name):
            for node in n_list:
                if isinstance(node, FunctionDef) and node.name == name:
                    return node, "Function"
                if isinstance(node, ClassDef) and node.name == name:
                    return node, "Class"
                if isinstance(node, Assign) and node.name == name:
                    return node, "Variable"
                if isinstance(node, If):
                     res = find_def(node.body, name)
                     if res: return res
            return None, None
        found_node = None
        found_type = None
        queue = nodes[:]
        while queue:
            n = queue.pop(0)
            if isinstance(n, FunctionDef):
                if n.name == word: 
                    found_node = n
                    found_type = "Function"
                    break
                queue.extend(n.body)
            elif isinstance(n, ClassDef):
                if n.name == word:
                    found_node = n
                    found_type = "Class"
                    break
                queue.extend(n.methods)
            elif isinstance(n, Assign) and n.name == word:
                found_node = n
                found_type = "Variable"
                break
            elif isinstance(n, If): queue.extend(n.body)
            elif isinstance(n, While): queue.extend(n.body)
            elif isinstance(n, For): queue.extend(n.body)
        if found_node:
            print(json.dumps({
                "found": True,
                "file": filename,
                "line": found_node.line,
                "hover": f"**{found_type}** `{word}`"
            }))
        else:
             print(json.dumps({"found": False}))
    except Exception:
        print(json.dumps({"found": False}))
def format_file(filename: str):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        from .formatter import Formatter
        formatter = Formatter(source)
        formatted_code = formatter.format()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_code)
        print(f"[SUCCESS] Formatted {filename}")
    except Exception as e:
        print(f"Formatting failed: {e}")
def self_install_check():
    res = subprocess.run(["where", "shl"], capture_output=True, text=True)
    if "ShellLite" not in res.stdout:
        print("\nShellLite is not installed globally.")
        choice = input("Would you like to install it so 'shl' works everywhere? (y/n): ").lower()
        if choice == 'y':
            install_globally()
def show_help():
    print("""
ShellLite - The English-Like Programming Language
Usage:
  shl <filename.shl>    Run a ShellLite script
  shl                   Start the interactive REPL
  shl help              Show this help message
  shl compile <file>    Compile a script (Options: --target js)
  shl fmt <file>        Format a script
  shl check <file>      Lint a file (JSON output)
  shl resolve <file> <line> <col>  Resolve symbol (JSON output)
  shl install           Install ShellLite globally to your system PATH
For documentation, visit: https://github.com/Shrey-N/ShellDesk
""")
def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "compile" or cmd == "build":
            if len(sys.argv) > 2:
                filename = sys.argv[2]
                target = 'python'
                if '--target' in sys.argv:
                    try:
                        idx = sys.argv.index('--target')
                        target = sys.argv[idx+1]
                    except IndexError:
                        print("Error: --target requires an argument (js/python)")
                        return
                compile_file(filename, target)
            else:
                print("Usage: shl compile <filename> [--target js]")
        elif cmd == "help" or cmd == "--help" or cmd == "-h":
            show_help()
        elif cmd == "get":
            if len(sys.argv) > 2:
                package_name = sys.argv[2]
                install_package(package_name)
            else:
                 print("Usage: shl get <user/repo>")
        elif cmd == "install":
            install_globally()
        elif cmd == "fmt" or cmd == "format":
            if len(sys.argv) > 2:
                filename = sys.argv[2]
                format_file(filename)
            else:
                print("Usage: shl fmt <filename>")
        elif cmd == "check":
            if len(sys.argv) > 2:
                filename = sys.argv[2]
                lint_file(filename)
        elif cmd == "resolve":
            if len(sys.argv) > 4:
                filename = sys.argv[2]
                line = int(sys.argv[3])
                col = int(sys.argv[4])
                resolve_cursor(filename, line, col)
        else:
            run_file(sys.argv[1])
    else:
        self_install_check()
        run_repl()
if __name__ == "__main__":
    main()
