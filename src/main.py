#!/usr/bin/env python3
"""
JARVIS OS - Advanced AI Operating System Assistant
Main entry point for the application.
"""

import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from gui.jarvis_main_window import JARVISMainWindow


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray
    
    # Set application style
    app.setStyle('Fusion')
    
    window = JARVISMainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    main()
