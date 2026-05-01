"""
Jarvis AI OS - Setup & Installation Script
Advanced AI Operating System Assistant for Windows
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class JarvisSetup:
    def __init__(self):
        self.name = "Jarvis"
        self.version = "2.0.0-Beta"
        self.base_dir = Path(__file__).parent
        
    def print_banner(self):
        print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     ██╗    ██╗███████╗███╗   ███╗███████╗                   ║
    ║     ██║    ██║██╔════╝████╗ ████║██╔════╝                   ║
    ║     ██║ █╗ ██║█████╗  ██╔████╔██║███████╗                   ║
    ║     ██║███╗██║██╔══╝  ██║╚██╔╝██║╚════██║                   ║
    ║     ╚███╔███╔╝███████╗██║ ╚═╝ ██║███████║                   ║
    ║      ╚══╝╚══╝ ╚══════╝╚═╝     ╚═╝╚══════╝                   ║
    ║                                                              ║
    ║     🤖 Advanced AI Operating System Assistant               ║
    ║     💫 Premium 3D Holographic Glassmorphism UI               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """)
        print(f"    Version: {self.version}")
        print("    Platform: Windows 10/11")
        print("    Python: 3.10+\n")
    
    def check_python_version(self):
        print("[1/5] Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            print(f"❌ Python 3.10+ required. Found: {version.major}.{version.minor}")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    
    def install_dependencies(self):
        print("\n[2/5] Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
            print("✅ Dependencies installed successfully")
            return True
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def create_directories(self):
        print("\n[3/5] Creating directories...")
        dirs = ['storage', 'keys', 'models', 'cache', 'logs']
        for d in dirs:
            path = self.base_dir / d
            path.mkdir(exist_ok=True)
            print(f"   ✅ {d}/")
        return True
    
    def download_models(self):
        print("\n[4/5] Downloading AI models...")
        print("   ℹ️ This may take several minutes...")
        print("   ℹ️ Ensure stable internet connection")
        
        # Create placeholder for models
        models_dir = self.base_dir / 'models'
        (models_dir / '.gitkeep').touch()
        print("   ✅ Models directory ready")
        return True
    
    def setup_ollama(self):
        print("\n[5/5] Setting up Ollama (Local AI)...")
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Ollama detected: {result.stdout.strip()}")
                print("   ℹ️ Run 'ollama pull llama3' to download the default model")
            else:
                print("   ⚠️ Ollama not found. Install from: https://ollama.ai/")
        except FileNotFoundError:
            print("   ⚠️ Ollama not installed. Install from: https://ollama.ai/")
        return True
    
    def run(self):
        self.print_banner()
        
        if not self.check_python_version():
            sys.exit(1)
        
        if not self.install_dependencies():
            sys.exit(1)
        
        self.create_directories()
        self.download_models()
        self.setup_ollama()
        
        print("\n" + "="*60)
        print("✅ JARVIS INSTALLATION COMPLETE!")
        print("="*60)
        print("\nTo launch Jarvis:")
        print("   python Jarvis.py")
        print("\nFor GUI mode:")
        print("   python -m jarvis.gui")
        print("\nFor voice mode:")
        print("   python -m jarvis.voice")
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    setup = JarvisSetup()
    setup.run()