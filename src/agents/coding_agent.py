"""
Coding Agent - Full-featured coding assistant with VS Code integration
Creates/edits files, executes commands, installs dependencies, 50+ language support.
"""

import os
import subprocess
import json
import re
import tempfile
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Language(Enum):
    """Supported programming languages"""
    PYTHON = ("python", ["py"], ["python", "python3"], "pip")
    JAVASCRIPT = ("javascript", ["js"], ["node"], "npm")
    TYPESCRIPT = ("typescript", ["ts"], ["node", "tsc"], "npm")
    JAVA = ("java", ["java"], ["javac"], "maven")
    CPP = ("c++", ["cpp", "cc", "cxx"], ["g++"], "apt")
    C = ("c", ["c", "h"], ["gcc"], "apt")
    CSHARP = ("c#", ["cs"], ["dotnet"], "dotnet")
    RUBY = ("ruby", ["rb"], ["ruby"], "gem")
    GO = ("go", ["go"], ["go"], "go")
    RUST = ("rust", ["rs"], ["rustc"], "cargo")
    PHP = ("php", ["php"], ["php"], "composer")
    SWIFT = ("swift", ["swift"], ["swift"], "swift")
    KOTLIN = ("kotlin", ["kt"], ["kotlinc"], "gradle")
    SCALA = ("scala", ["scala"], ["scala"], "sbt")
    R = ("r", ["r", "R"], ["Rscript"], "install.packages")
    PERL = ("perl", ["pl"], ["perl"], "cpan")
    LUA = ("lua", ["lua"], ["lua"], "luarocks")
    HASKELL = ("haskell", ["hs"], ["ghc"], "cabal")
    ERLANG = ("erlang", ["erl"], ["erlc"], "rebar3")
    ELIXIR = ("elixir", ["ex"], ["elixir"], "mix")
    CLOJURE = ("clojure", ["clj"], ["clojure"], "lein")
    DART = ("dart", ["dart"], ["dart"], "pub")
    GROOVY = ("groovy", ["groovy"], ["groovy"], "gradle")
    POWERSHELL = ("powershell", ["ps1"], ["pwsh"], "powershell")
    BASH = ("bash", ["sh", "bash"], ["bash"], "apt")
    SQL = ("sql", ["sql"], [], [])
    HTML = ("html", ["html", "htm"], [], [])
    CSS = ("css", ["css"], [], [])
    SCSS = ("scss", ["scss"], ["sass"], "npm")
    JSON = ("json", ["json"], [], [])
    XML = ("xml", ["xml"], [], [])
    YAML = ("yaml", ["yaml", "yml"], [], [])
    MARKDOWN = ("markdown", ["md"], [], [])
    LATEX = ("latex", ["tex"], ["pdflatex"], "tlmgr")
    ASSEMBLY = ("assembly", ["asm"], ["nasm"], "apt")
    FORTRAN = ("fortran", ["f90", "for"], ["gfortran"], "apt")
    MATLAB = ("matlab", ["m"], ["matlab"], "matlab")
    VHDL = ("vhdl", ["vhd"], ["ghdl"], "apt")
    VERILOG = ("verilog", ["v"], ["iverilog"], "apt")
    LISP = ("lisp", ["lisp", "lsp"], ["sbcl"], "quicklisp")
    PROLOG = ("prolog", ["pl"], ["swipl"], "apt")
    SCHEME = ("scheme", ["scm"], ["guile"], "apt")
    OCAML = ("ocaml", ["ml"], ["ocaml"], "opam")
    F_SHARP = ("f#", ["fs"], ["dotnet"], "dotnet")
    JULIA = ("julia", ["jl"], ["julia"], "Pkg")
    CRYSTAL = ("crystal", ["cr"], ["crystal"], "shards")
    ZIG = ("zig", ["zig"], ["zig"], "zig")
    NIM = ("nim", ["nim"], ["nim"], "nimble")
    D = ("d", ["d"], ["dmd"], "dub")
    OBJECTIVE_C = ("objective-c", ["m"], ["clang"], "apt")
    COBOL = ("cobol", ["cob", "cbl"], ["cobc"], "apt")
    PASCAL = ("pascal", ["pas"], ["fpc"], "apt")


@dataclass
class CodeFile:
    """Represents a code file"""
    path: str
    content: str
    language: Language
    line_count: int
    char_count: int
    checksum: str
    
    @classmethod
    def create(cls, path: str, content: str) -> 'CodeFile':
        lang = LanguageDetector.detect_from_path(path)
        return cls(
            path=path,
            content=content,
            language=lang,
            line_count=len(content.splitlines()),
            char_count=len(content),
            checksum=hashlib.md5(content.encode()).hexdigest()
        )


class LanguageDetector:
    """Detects programming language from file content or path"""
    
    LANGUAGE_PATTERNS = {
        'python': [r'^\s*import\s+\w+', r'^\s*from\s+\w+\s+import', r'def\s+\w+\s*\('],
        'javascript': [r'^\s*const\s+\w+\s*=', r'^\s*let\s+\w+\s*=', r'function\s+\w+\s*\('],
        'java': [r'public\s+class\s+\w+', r'public\s+static\s+void\s+main'],
        'c': [r'#include\s*<\w+\.h>', r'int\s+main\s*\('],
        'cpp': [r'#include\s*<\w+>', r'using\s+namespace\s+std', r'class\s+\w+\s*\{'],
        'rust': [r'fn\s+\w+\s*\(', r'let\s+mut\s+', r'use\s+\w+::'],
        'go': [r'package\s+\w+', r'func\s+\w+\s*\(', r'import\s*\('],
        'typescript': [r'interface\s+\w+', r'type\s+\w+\s*=', r':\s*(string|number|boolean)'],
    }
    
    @classmethod
    def detect_from_path(cls, path: str) -> Language:
        """Detect language from file extension"""
        ext = Path(path).suffix.lower().strip('.')
        
        for lang in Language:
            if ext in lang.value[1]:
                return lang
        
        return Language.PYTHON  # Default
    
    @classmethod
    def detect_from_content(cls, content: str) -> Language:
        """Detect language from file content patterns"""
        for lang_name, patterns in cls.LANGUAGE_PATTERNS.items():
            matches = sum(1 for p in patterns if re.search(p, content, re.MULTILINE))
            if matches >= 2:
                for lang in Language:
                    if lang.value[0] == lang_name:
                        return lang
        
        return Language.PYTHON


class BugDetector:
    """Automatically detects and fixes bugs in code"""
    
    # Common bug patterns and their fixes
    COMMON_BUGS = {
        r'print\s*\(\s*["\']': 'print_function',
        r'Tabs?\s+vs\s+Spaces': 'indentation',
        r'while\s+True\s*:\s*(?!.*time\.sleep)': 'infinite_loop',
        r'except\s*:\s*pass': 'bare_except',
        r'==\s*(None|True|False)': 'identity_vs_equality',
        r'global\s+\w+': 'global_variable',
        r'\[\s*i\s+for\s+i\s+in\s+range\([^)]+\)\s*\]\s*\[\s*-1\s*\]\s*==': 'off_by_one',
    }
    
    # Error patterns to fix
    ERROR_FIXES = {
        'IndentationError': 'Fix indentation (use 4 spaces)',
        'SyntaxError': 'Fix syntax - check parentheses, quotes, brackets',
        'NameError': 'Define variable before use or check spelling',
        'TypeError': 'Check types match expected parameters',
        'ImportError': 'Install missing package or check import path',
        'FileNotFoundError': 'Check file path exists or create it',
        'KeyError': 'Key not found in dictionary - use .get() or check key exists',
        'IndexError': 'Index out of range - check list bounds',
        'AttributeError': 'Object has no attribute - check type or attribute name',
        'ValueError': 'Invalid value - check input format',
        'TimeoutError': 'Operation timed out - increase timeout or check network',
    }
    
    @classmethod
    def detect_bugs(cls, code: str) -> List[Dict[str, Any]]:
        """Detect common bugs in code"""
        bugs = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if re.search(r'except\s*:\s*pass', line):
                bugs.append({
                    'line': i,
                    'type': 'bare_except',
                    'message': 'Bare except clause - specify exception type',
                    'severity': 'warning'
                })
            
            if re.search(r'print\s*\(\s*["\']\s*\)', line):
                bugs.append({
                    'line': i,
                    'type': 'empty_print',
                    'message': 'Empty print statement',
                    'severity': 'error'
                })
            
            if re.search(r'[^#]\s*#.*$', line) and not line.strip():
                bugs.append({
                    'line': i,
                    'type': 'commented_code',
                    'message': 'Empty line with trailing comment',
                    'severity': 'info'
                })
        
        return bugs
    
    @classmethod
    def fix_error(cls, error_type: str, error_msg: str) -> str:
        """Suggest fix for an error"""
        # Extract error type from error message
        for error, fix in cls.ERROR_FIXES.items():
            if error in error_msg:
                return f"{error}: {fix}"
        
        return "Unknown error - review code manually"


class VSCodeIntegration:
    """VS Code command integration for coding workflow"""
    
    COMMON_COMMANDS = [
        'workbench.action.files.newFile',
        'workbench.action.files.save',
        'workbench.action.files.saveAll',
        'workbench.action.closeActiveEditor',
        'workbench.action.closeAllEditors',
        'workbench.action.terminal.newTerminal',
        'workbench.action.terminal.kill',
        'workbench.action.formatDocument',
        'workbench.action.quickOpen',
        'workbench.action.gotoSymbol',
        'editor.action.formatSelection',
        'editor.action.commentLine',
        'editor.action.addSelectionToNextFindMatch',
        'workbench.action.findInFiles',
        'workbench.action.replaceInFiles',
    ]
    
    def __init__(self):
        self.vscode_path = self._find_vscode()
    
    def _find_vscode(self) -> Optional[str]:
        """Find VS Code installation path"""
        common_paths = [
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def open_file(self, file_path: str):
        """Open file in VS Code"""
        if self.vscode_path:
            subprocess.Popen([self.vscode_path, file_path])
        else:
            print(f"VS Code not found. File: {file_path}")
    
    def open_folder(self, folder_path: str):
        """Open folder in VS Code"""
        if self.vscode_path:
            subprocess.Popen([self.vscode_path, '--folder-uri', folder_path])
        else:
            print(f"VS Code not found. Folder: {folder_path}")
    
    def execute_command(self, command: str):
        """Execute a VS Code command (requires extension)"""
        # This would require a VS Code extension to work
        # For now, just a placeholder
        pass


class CodeExecutor:
    """Executes code in various programming languages"""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or tempfile.mkdtemp()
        self.execution_history: List[Dict] = []
    
    def execute(self, code: str, language: Language) -> Dict[str, Any]:
        """Execute code and return result"""
        result = {
            'success': False,
            'output': '',
            'error': '',
            'execution_time': 0,
            'language': language.value[0]
        }
        
        start_time = os.times().elapsed
        
        try:
            if language == Language.PYTHON:
                result = self._execute_python(code)
            elif language == Language.JAVASCRIPT:
                result = self._execute_javascript(code)
            elif language == Language.BASH:
                result = self._execute_bash(code)
            else:
                result['error'] = f"Language {language.value[0]} not supported for execution"
        except Exception as e:
            result['error'] = str(e)
        
        result['execution_time'] = os.times().elapsed - start_time
        self.execution_history.append(result)
        
        return result
    
    def _execute_python(self, code: str) -> Dict:
        """Execute Python code"""
        result = {'success': False, 'output': '', 'error': ''}
        
        try:
            # Write to temp file
            temp_file = os.path.join(self.workspace_dir, 'temp_script.py')
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Execute
            proc = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result['success'] = proc.returncode == 0
            result['output'] = proc.stdout
            result['error'] = proc.stderr
        except subprocess.TimeoutExpired:
            result['error'] = 'Execution timed out (30s limit)'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _execute_javascript(self, code: str) -> Dict:
        """Execute JavaScript code"""
        result = {'success': False, 'output': '', 'error': ''}
        
        try:
            temp_file = os.path.join(self.workspace_dir, 'temp_script.js')
            with open(temp_file, 'w') as f:
                f.write(code)
            
            proc = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result['success'] = proc.returncode == 0
            result['output'] = proc.stdout
            result['error'] = proc.stderr
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _execute_bash(self, code: str) -> Dict:
        """Execute Bash script"""
        result = {'success': False, 'output': '', 'error': ''}
        
        try:
            proc = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result['success'] = proc.returncode == 0
            result['output'] = proc.stdout
            result['error'] = proc.stderr
        except Exception as e:
            result['error'] = str(e)
        
        return result


class DependencyManager:
    """Manages package dependencies for various languages"""
    
    @classmethod
    def install(cls, package: str, language: Language) -> Dict[str, Any]:
        """Install a package dependency"""
        result = {'success': False, 'output': '', 'error': ''}
        
        package_manager = language.value[3] if len(language.value) > 3 else None
        
        if not package_manager:
            result['error'] = f"No package manager defined for {language.value[0]}"
            return result
        
        try:
            if language == Language.PYTHON:
                cmd = f'pip install {package}'
            elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
                cmd = f'npm install {package}'
            elif language == Language.RUST:
                cmd = f'cargo add {package}'
            elif language == Language.GO:
                cmd = f'go get {package}'
            elif language == Language.RUBY:
                cmd = f'gem install {package}'
            else:
                cmd = f'{package_manager} install {package}'
            
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            result['success'] = proc.returncode == 0
            result['output'] = proc.stdout
            result['error'] = proc.stderr
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    @classmethod
    def get_installed(cls, language: Language) -> List[str]:
        """Get list of installed packages"""
        try:
            if language == Language.PYTHON:
                proc = subprocess.run(
                    ['pip', 'list'],
                    capture_output=True,
                    text=True
                )
                packages = []
                for line in proc.stdout.split('\n')[2:]:
                    if line:
                        packages.append(line.split()[0])
                return packages
            elif language == Language.JAVASCRIPT:
                # Parse package.json
                if os.path.exists('package.json'):
                    with open('package.json') as f:
                        data = json.load(f)
                        deps = list(data.get('dependencies', {}).keys())
                        dev_deps = list(data.get('devDependencies', {}).keys())
                        return deps + dev_deps
        except:
            pass
        
        return []


class CodingAgent:
    """
    Main Coding Agent - Coordinates all coding operations
    Provides unified interface for code generation, editing, execution, and debugging.
    """
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or tempfile.mkdtemp()
        self.executor = CodeExecutor(self.workspace_dir)
        self.bug_detector = BugDetector()
        self.vscode = VSCodeIntegration()
        self.dependency_manager = DependencyManager()
        self.supported_languages = list(Language)
        
        # Project tracking
        self.active_projects: Dict[str, Dict] = {}
        self.code_templates: Dict[str, str] = {}
        
        # Initialize code templates
        self._init_templates()
    
    def _init_templates(self):
        """Initialize code generation templates"""
        self.code_templates = {
            'python_fastapi': '''from fastapi import FastAPI
from typing import Optional

app = FastAPI(title="{name}", version="1.0.0")

@app.get("/")
def read_root():
    return {{"message": "Hello World"}}

@app.get("/items/{{item_id}}")
def read_item(item_id: int, q: Optional[str] = None):
    return {{"item_id": item_id, "q": q}}
''',
            'javascript_express': '''const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {{
    res.json({{ message: "Hello World" }});
}});

app.listen(PORT, () => {{
    console.log(`Server running on port ${{PORT}}`);
}});
''',
            'react_component': '''import React, {{ useState, useEffect }} from 'react';

const {name} = () => {{
    const [data, setData] = useState(null);
    
    useEffect(() => {{
        // Fetch data on mount
        fetch('/api/data')
            .then(res => res.json())
            .then(data => setData(data));
    }}, []);
    
    return (
        <div className="{name}">
            <h1>{name}</h1>
            {{data && <p>{{JSON.stringify(data)}}</p>}}
        </div>
    );
}};

export default {name};
''',
            'html_boilerplate': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Welcome to {title}</p>
    <script src="main.js"></script>
</body>
</html>
'''
        }
    
    def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """Create a new code file"""
        result = {'success': False, 'path': path, 'error': ''}
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            
            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result['success'] = True
            result['file'] = CodeFile.create(path, content).__dict__
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def edit_file(self, path: str, changes: List[Dict]) -> Dict[str, Any]:
        """Edit an existing file"""
        result = {'success': False, 'path': path, 'error': ''}
        
        try:
            if not os.path.exists(path):
                result['error'] = f"File not found: {path}"
                return result
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply changes (sorted by line descending to preserve line numbers)
            for change in sorted(changes, key=lambda x: x.get('line', 0), reverse=True):
                line_num = change.get('line', 0) - 1
                new_content = change.get('content', '')
                
                if 0 <= line_num < len(lines):
                    lines[line_num] = new_content + '\n'
            
            # Write back
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file contents"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def execute_code(self, code: str, language: Language = Language.PYTHON) -> Dict[str, Any]:
        """Execute code"""
        return self.executor.execute(code, language)
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for bugs and issues"""
        bugs = self.bug_detector.detect_bugs(code)
        language = LanguageDetector.detect_from_content(code)
        line_count = len(code.split('\n'))
        
        return {
            'bugs': bugs,
            'language': language.value[0],
            'line_count': line_count,
            'has_issues': len(bugs) > 0
        }
    
    def fix_bug(self, code: str, bug: Dict) -> str:
        """Attempt to fix a detected bug"""
        # This would use AI to generate fixes
        # For now, return simple fixes
        lines = code.split('\n')
        line_num = bug.get('line', 0) - 1
        
        if bug.get('type') == 'bare_except':
            lines[line_num] = 'except Exception as e:\n    print(f"Error: {e}")'
        elif bug.get('type') == 'empty_print':
            lines[line_num] = 'print("Debug info")'
        
        return '\n'.join(lines)
    
    def generate_code(self, description: str, language: Language = Language.PYTHON, 
                      template: str = None) -> str:
        """Generate code from description"""
        # Use AI or templates to generate code
        # For now, return a placeholder
        return f"# Generated code for: {description}\n# Language: {language.value[0]}\n\n# TODO: Implement\n"
    
    def install_dependency(self, package: str, language: Language) -> Dict[str, Any]:
        """Install a dependency"""
        return self.dependency_manager.install(package, language)
    
    def open_in_vscode(self, path: str):
        """Open file in VS Code"""
        self.vscode.open_file(path)
    
    def create_project(self, name: str, framework: str, location: str) -> Dict[str, Any]:
        """Create a new project from template"""
        result = {'success': False, 'project_dir': '', 'files_created': [], 'error': ''}
        
        try:
            project_dir = os.path.join(location, name)
            os.makedirs(project_dir, exist_ok=True)
            
            if framework == 'fastapi':
                content = self.code_templates['python_fastapi'].format(name=name)
                self.create_file(os.path.join(project_dir, 'main.py'), content)
                self.create_file(os.path.join(project_dir, 'requirements.txt'), 'fastapi\nuvicorn')
            
            elif framework == 'react':
                self.create_file(
                    os.path.join(project_dir, 'App.jsx'),
                    self.code_templates['react_component'].format(name=name)
                )
                self.create_file(
                    os.path.join(project_dir, 'index.html'),
                    self.code_templates['html_boilerplate'].format(title=name)
                )
            
            result['success'] = True
            result['project_dir'] = project_dir
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return [lang.value[0] for lang in self.supported_languages]
    
    def get_workspace_status(self) -> Dict[str, Any]:
        """Get workspace status"""
        files = []
        for root, dirs, filenames in os.walk(self.workspace_dir):
            for f in filenames:
                path = os.path.join(root, f)
                files.append({
                    'path': path,
                    'size': os.path.getsize(path)
                })
        
        return {
            'workspace_dir': self.workspace_dir,
            'files_count': len(files),
            'files': files,
            'execution_history_count': len(self.executor.execution_history)
        }


# Global instance
_coding_agent = None

def get_coding_agent(workspace_dir: str = None) -> CodingAgent:
    """Get or create the global Coding Agent instance"""
    global _coding_agent
    if _coding_agent is None:
        _coding_agent = CodingAgent(workspace_dir)
    return _coding_agent
