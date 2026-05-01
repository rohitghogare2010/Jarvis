"""
Jarvis AI OS - PyQt5 GUI with 3D Holographic UI
Premium glassmorphism and animated interface
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QFrame, QStackedWidget,
    QGraphicsDropShadowEffect, QPropertyAnimation, QParallelAnimationGroup
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient, QPainter, QPen
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineCore import QWebEngineSettings
import json


class HolographicPanel(QFrame):
    """Holographic glass panel with animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HoloPanel")
        self.setStyleSheet("""
            #HoloPanel {
                background: rgba(0, 20, 40, 0.7);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 20px;
                backdrop-filter: blur(20px);
            }
            #HoloPanel:hover {
                border: 1px solid rgba(0, 245, 255, 0.8);
                background: rgba(0, 30, 50, 0.8);
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 245, 255, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


class JarvisWindow(QMainWindow):
    """Main Jarvis AI OS Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis AI OS - Advanced Assistant")
        self.setMinimumSize(1400, 900)
        self.center_window()
        self.init_ui()
        self.init_animations()
        
    def center_window(self):
        """Center window on screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def init_ui(self):
        """Initialize the UI"""
        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Background gradient
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 10, 30, 1),
                    stop:0.5 rgba(26, 10, 46, 1),
                    stop:1 rgba(10, 26, 46, 1));
            }
            QPushButton {
                background: rgba(0, 245, 255, 0.1);
                border: 1px solid rgba(0, 245, 255, 0.5);
                border-radius: 12px;
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 245, 255, 0.3);
                border: 1px solid rgba(0, 245, 255, 1);
            }
            QLineEdit, QTextEdit {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 15px;
                color: white;
                padding: 15px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid rgba(0, 245, 255, 0.8);
            }
            QLabel {
                color: white;
            }
        """)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Left panel - AI Modules
        left_panel = self.create_modules_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Center panel - Chat and controls
        center_panel = self.create_center_panel()
        content_layout.addWidget(center_panel, 2)
        
        # Right panel - Status
        right_panel = self.create_status_panel()
        content_layout.addWidget(right_panel, 1)
        
        main_layout.addWidget(content, 1)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
        # System tray
        self.create_system_tray()
    
    def create_header(self):
        """Create header with logo and status"""
        header = HolographicPanel()
        layout = QHBoxLayout(header)
        
        # Logo section
        logo_layout = QHBoxLayout()
        
        # Orb animation placeholder
        orb_label = QLabel("◉")
        orb_label.setStyleSheet("""
            font-size: 40px;
            color: #00f5ff;
            text-shadow: 0 0 20px #00f5ff, 0 0 40px #00f5ff;
        """)
        logo_layout.addWidget(orb_label)
        
        title = QLabel("JARVIS")
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title.setStyleSheet("""
            background: linear-gradient(90deg, #00f5ff, #7b2cbf, #ff006e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: 10px;
        """)
        logo_layout.addWidget(title)
        
        version = QLabel("v2.0.0-BETA")
        version.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 12px;")
        logo_layout.addWidget(version)
        
        layout.addLayout(logo_layout)
        layout.addStretch()
        
        # Status indicators
        status_layout = QHBoxLayout()
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #00ff00; font-size: 16px;")
        status_layout.addWidget(status_dot)
        
        status_text = QLabel("Systems Online")
        status_text.setStyleSheet("color: rgba(255,255,255,0.8);")
        status_layout.addWidget(status_text)
        
        layout.addLayout(status_layout)
        
        return header
    
    def create_modules_panel(self):
        """Create AI modules panel"""
        panel = HolographicPanel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🎯 AI MODULES")
        title.setStyleSheet("color: #00f5ff; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Module buttons
        modules = [
            ("👁️", "Visual AI", "visual-ai"),
            ("🖼️", "Image Gen", "image-gen"),
            ("🎬", "Video Gen", "video-gen"),
            ("💻", "Coding", "coding"),
            ("📚", "Learning", "learning"),
            ("🏗️", "Projects", "projects"),
            ("🤖", "Local AI", "local-ai"),
            ("⚙️", "OS Control", "os-control"),
        ]
        
        for icon, name, module_id in modules:
            btn = QPushButton(f"{icon} {name}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, m=module_id: self.open_module(m))
            layout.addWidget(btn)
        
        layout.addStretch()
        return panel
    
    def create_center_panel(self):
        """Create center panel with chat and voice"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Voice visualization
        voice_panel = HolographicPanel()
        voice_layout = QVBoxLayout(voice_panel)
        
        voice_title = QLabel("🎤 VOICE INTERFACE")
        voice_title.setStyleSheet("color: #00f5ff; font-weight: bold;")
        voice_layout.addWidget(voice_title, 0, Qt.AlignCenter)
        
        voice_status = QLabel('Listening for "Hey Jarvis"...')
        voice_status.setStyleSheet("color: rgba(255,255,255,0.6); margin: 20px;")
        voice_layout.addWidget(voice_status, 0, Qt.AlignCenter)
        
        mic_btn = QPushButton("🎤")
        mic_btn.setFixedSize(80, 80)
        mic_btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0,245,255,0.8),
                    stop:1 rgba(0,245,255,0.2));
                border: 2px solid #00f5ff;
                border-radius: 40px;
                font-size: 30px;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0,245,255,1),
                    stop:1 rgba(0,245,255,0.5));
                box-shadow: 0 0 30px #00f5ff;
            }
        """)
        mic_btn.clicked.connect(self.toggle_voice)
        voice_layout.addWidget(mic_btn, 0, Qt.AlignCenter)
        
        layout.addWidget(voice_panel)
        
        # Chat interface
        chat_panel = HolographicPanel()
        chat_layout = QVBoxLayout(chat_panel)
        
        chat_title = QLabel("💬 COMMAND CENTER")
        chat_title.setStyleSheet("color: #00f5ff; font-weight: bold;")
        chat_layout.addWidget(chat_title)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(0,0,0,0.3);
                border: none;
                border-radius: 10px;
                padding: 15px;
                color: white;
            }
        """)
        self.chat_display.setMinimumHeight(200)
        chat_layout.addWidget(self.chat_display)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your command...")
        self.chat_input.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.chat_input)
        
        send_btn = QPushButton("➤")
        send_btn.setFixedSize(50, 50)
        send_btn.clicked.connect(self.send_command)
        input_layout.addWidget(send_btn)
        
        chat_layout.addLayout(input_layout)
        layout.addWidget(chat_panel)
        
        # Quick actions
        actions_panel = HolographicPanel()
        actions_layout = QHBoxLayout(actions_panel)
        
        actions = [
            ("🎨", "Image"),
            ("🎬", "Video"),
            ("💻", "Code"),
            ("📚", "Learn"),
            ("🏗️", "Build"),
        ]
        
        for icon, name in actions:
            btn = QPushButton(f"{icon} {name}")
            btn.setMinimumHeight(40)
            actions_layout.addWidget(btn)
        
        layout.addWidget(actions_panel)
        
        return panel
    
    def create_status_panel(self):
        """Create status and info panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # System Status
        status_panel = HolographicPanel()
        status_layout = QVBoxLayout(status_panel)
        
        title = QLabel("📊 SYSTEM STATUS")
        title.setStyleSheet("color: #00f5ff; font-weight: bold;")
        status_layout.addWidget(title)
        
        # Progress bars
        status_items = [
            ("AI Engine", 100),
            ("Voice I/O", 95),
            ("Storage", 45),
            ("Local AI", 100),
        ]
        
        for name, value in status_items:
            row = QHBoxLayout()
            lbl = QLabel(name)
            lbl.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
            row.addWidget(lbl)
            
            progress = QFrame()
            progress.setFixedHeight(8)
            progress.setStyleSheet(f"""
                QFrame {{
                    background: rgba(0,0,0,0.3);
                    border-radius: 4px;
                }}
            """)
            progress_bar = QFrame()
            progress_bar.setFixedWidth(int(100 * value / 100 * 1.5))
            progress_bar.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00f5ff, stop:1 #7b2cbf);
                    border-radius: 4px;
                }}
            """)
            progress_layout = QHBoxLayout(progress)
            progress_layout.setContentsMargins(0, 0, 0, 0)
            progress_layout.addWidget(progress_bar)
            progress_layout.addStretch()
            row.addWidget(progress)
            
            val_lbl = QLabel(f"{value}%")
            val_lbl.setStyleSheet("color: #00f5ff; font-size: 12px;")
            row.addWidget(val_lbl)
            
            status_layout.addLayout(row)
        
        layout.addWidget(status_panel)
        
        # Capabilities
        cap_panel = HolographicPanel()
        cap_layout = QVBoxLayout(cap_panel)
        
        cap_title = QLabel("🚀 CAPABILITIES")
        cap_title.setStyleSheet("color: #00f5ff; font-weight: bold;")
        cap_layout.addWidget(cap_title)
        
        capabilities = [
            "🌐 50+ Languages",
            "🎨 8K/16K Image Gen",
            "🎬 SVD Video Gen",
            "💻 VS Code Integration",
            "🔧 Auto Bug Fix",
            "📚 GitHub Learning",
            "🤖 Ollama Offline AI",
            "💾 50GB Encrypted Storage",
        ]
        
        for cap in capabilities:
            lbl = QLabel(cap)
            lbl.setStyleSheet("padding: 5px 0;")
            cap_layout.addWidget(lbl)
        
        layout.addWidget(cap_panel)
        
        # Processing stats
        stats_panel = HolographicPanel()
        stats_layout = QVBoxLayout(stats_panel)
        
        stats_title = QLabel("⚡ PROCESSING")
        stats_title.setStyleSheet("color: #00f5ff; font-weight: bold;")
        stats_layout.addWidget(stats_title)
        
        stats_items = [
            ("50L+", "Videos/min"),
            ("1Cr+", "Images/min"),
            ("20GB", "Video Storage"),
        ]
        
        for value, label in stats_items:
            stat = QWidget()
            stat_layout = QHBoxLayout(stat)
            
            val_lbl = QLabel(value)
            val_lbl.setStyleSheet("color: #00f5ff; font-size: 20px; font-weight: bold;")
            stat_layout.addWidget(val_lbl)
            
            lbl_lbl = QLabel(label)
            lbl_lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")
            stat_layout.addWidget(lbl_lbl)
            
            stats_layout.addWidget(stat)
        
        layout.addWidget(stats_panel)
        layout.addStretch()
        
        return panel
    
    def create_footer(self):
        """Create footer bar"""
        footer = HolographicPanel()
        footer.setFixedHeight(50)
        layout = QHBoxLayout(footer)
        
        copyright = QLabel("© 2024 Jarvis AI OS - Rohit Ghogare")
        copyright.setStyleSheet("color: rgba(255,255,255,0.5);")
        layout.addWidget(copyright)
        
        layout.addStretch()
        
        status = QLabel("Ready to assist")
        status.setStyleSheet("color: rgba(255,255,255,0.7);")
        layout.addWidget(status)
        
        layout.addStretch()
        
        minimize_btn = QPushButton("—")
        minimize_btn.setFixedSize(40, 40)
        minimize_btn.clicked.connect(self.minimize_to_tray)
        layout.addWidget(minimize_btn)
        
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        layout.addWidget(settings_btn)
        
        return footer
    
    def create_system_tray(self):
        """Create system tray icon and menu"""
        try:
            from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
            
            self.tray = QSystemTrayIcon(self)
            self.tray.setToolTip("Jarvis AI OS")
            
            # Tray menu
            menu = QMenu()
            
            show_action = QAction("Show Jarvis", self)
            show_action.triggered.connect(self.show)
            menu.addAction(show_action)
            
            voice_action = QAction("🎤 Voice Mode", self)
            menu.addAction(voice_action)
            
            menu.addSeparator()
            
            quit_action = QAction("Exit", self)
            quit_action.triggered.connect(self.close)
            menu.addAction(quit_action)
            
            self.tray.setContextMenu(menu)
            self.tray.show()
            
        except Exception as e:
            print(f"Tray not available: {e}")
    
    def init_animations(self):
        """Initialize UI animations"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(50)
        
        self.animation_frame = 0
    
    def update_animations(self):
        """Update animated elements"""
        self.animation_frame += 1
    
    def open_module(self, module_id):
        """Open a specific AI module"""
        self.add_chat_message("system", f"Opening {module_id}...")
    
    def toggle_voice(self):
        """Toggle voice input"""
        self.add_chat_message("system", "🎤 Voice activated...")
    
    def send_command(self):
        """Send a chat command"""
        text = self.chat_input.text().strip()
        if text:
            self.add_chat_message("user", text)
            self.chat_input.clear()
            self.process_command(text)
    
    def add_chat_message(self, msg_type, text):
        """Add a message to the chat display"""
        if msg_type == "user":
            self.chat_display.append(f'<div style="text-align: right; color: #00f5ff;">👤 {text}</div>')
        else:
            self.chat_display.append(f'<div style="text-align: left; color: white;">🤖 {text}</div>')
    
    def process_command(self, command):
        """Process user command"""
        # Simulated response
        response = f"Processing: {command}"
        self.add_chat_message("system", response)
    
    def minimize_to_tray(self):
        """Minimize window to system tray"""
        self.hide()
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Jarvis AI OS")
    app.setApplicationVersion("2.0.0")
    
    window = JarvisWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()