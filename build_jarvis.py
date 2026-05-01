#!/usr/bin/env python3
"""
Build script for JARVIS OS - Advanced AI Operating System Assistant
Creates Windows executable using PyInstaller.
"""

import PyInstaller.__main__
import os
import sys
import shutil


def build():
    """Build JARVIS OS executable for Windows"""
    
    print("=" * 60)
    print("  JARVIS OS - Advanced AI Operating System")
    print("  Building Windows Executable...")
    print("=" * 60)
    
    # Build parameters
    params = [
        'src/main.py',
        '--name=JARVIS_OS',
        '--windowed',  # No console window
        '--onefile',  # Single executable
        '--icon=assets/icon.ico',
        '--add-data=src/gui:gui',
        '--add-data=src/ai:ai',
        '--add-data=src/audio:audio',
        '--add-data=src/agents:agents',
        '--add-data=src/services:services',
        '--add-data=src/utils:utils',
        '--hidden-import=PyQt6',
        '--hidden-import=requests',
        '--hidden-import=whisper',
        '--hidden-import=torch',
        '--hidden-import=torchvision',
        '--hidden-import=diffusers',
        '--hidden-import=cv2',
        '--hidden-import=transformers',
        '--hidden-import=accelerate',
        '--hidden-import=pyttsx3',
        '--hidden-import=pyautogui',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=opencv-python',
        '--hidden-import=pillow',
        '--hidden-import=numpy',
        '--hidden-import=moviepy',
        '--hidden-import=TTS',
        '--hidden-import=sounddevice',
        '--hidden-import=scipy',
        '--hidden-import=git',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
    ]
    
    print("\nRunning PyInstaller...")
    try:
        PyInstaller.__main__.run(params)
        print("\n✅ Build completed successfully!")
        print(f"   Executable location: dist/JARVIS_OS.exe")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(build())
