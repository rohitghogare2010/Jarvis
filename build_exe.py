"""
Jarvis AI OS - Windows Executable Builder
Creates standalone .exe for Windows distribution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def build_exe():
    print("="*60)
    print("Building Jarvis AI OS Windows Executable...")
    print("="*60)
    
    # Check for PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Jarvis-AI-OS",
        "--onefile",
        "--windowed",
        "--icon=icons/jarvis.ico",
        "--add-data=styles;styles",
        "--add-data=assets;assets",
        "--add-data=config.json;.",
        "--hidden-import=pyttsx3",
        "--hidden-import=speech_recognition",
        "--hidden-import=pywin32",
        "--hidden-import=cryptography",
        "--hidden-import=psutil",
        "--collect-all=transformers",
        "--collect-all=diffusers",
        "Jarvis.py"
    ]
    
    print("\nRunning PyInstaller...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ Build successful!")
        print("📦 Executable location: dist/Jarvis-AI-OS.exe")
        
        # Create distribution folder
        dist_folder = Path("release")
        dist_folder.mkdir(exist_ok=True)
        exe_path = Path("dist/Jarvis-AI-OS.exe")
        
        if exe_path.exists():
            shutil.copy(exe_path, dist_folder / "Jarvis-AI-OS.exe")
            print(f"📁 Copied to: {dist_folder / 'Jarvis-AI-OS.exe'}")
    else:
        print("\n❌ Build failed!")
        print(result.stderr)
    
    print("="*60)


if __name__ == "__main__":
    build_exe()