import PyInstaller.__main__
import os

def build():
    # Define parameters for PyInstaller
    params = [
        'src/main.py',
        '--name=RS_AI',
        '--windowed', # No console window
        '--onefile',   # Combine into a single executable
        '--hidden-import=PyQt6',
        '--hidden-import=requests',
        '--hidden-import=whisper',
        '--hidden-import=torch',
        '--hidden-import=diffusers',
        '--hidden-import=cv2',
        '--add-data=src/gui:gui',
        '--add-data=src/ai:ai',
        '--add-data=src/audio:audio',
        '--add-data=src/utils:utils',
    ]
    
    PyInstaller.__main__.run(params)

if __name__ == "__main__":
    build()
